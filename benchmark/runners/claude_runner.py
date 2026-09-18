import json
import time

import anthropic

from .base import BaseRunner

SYSTEM = (
    "You are a structured decision model. For each question, return ONLY valid JSON. "
    "Every answer MUST include the confidence fields specified (0.0-1.0) representing "
    "how certain you are. Do NOT explain. Do NOT add commentary. JSON only."
)


class ClaudeRunner(BaseRunner):
    def __init__(self, model: str, *, label: str | None = None, thinking: bool = False):
        self._model = model
        self._client = anthropic.Anthropic()
        self._label = label or ("opus" if "opus" in model else "sonnet")
        self._thinking = thinking

    def name(self) -> str:
        return self._label

    def model_string(self) -> str:
        return self._model

    def run_case(self, task: dict, case: dict) -> dict | None:
        prompt = task["claude_prompt"].replace("{text}", case["text"])
        raw = self._call_api(prompt)
        if raw is None:
            raw = self._call_api(prompt)
        if raw is None:
            print(f"  [{self._label}] case {case['id']} failed after retry")
            return None

        parsed, latency_ms, usage = raw
        answers = self._extract_answers(task, parsed, case["id"])
        if answers is None:
            return None

        return {
            "answers": answers,
            "latency_ms": latency_ms,
            "input_tokens": usage.input_tokens,
            "output_tokens": usage.output_tokens,
        }

    def _call_api(self, prompt: str):
        t0 = time.perf_counter()
        try:
            kwargs = dict(
                model=self._model,
                max_tokens=300,
                system=SYSTEM,
                messages=[{"role": "user", "content": prompt}],
            )
            if self._thinking:
                kwargs["thinking"] = {"type": "adaptive"}
                kwargs["max_tokens"] = 4096
            else:
                kwargs["temperature"] = 0
            r = self._client.messages.create(**kwargs)
        except Exception as e:
            print(f"  [{self._label}] API error: {e}")
            return None
        latency_ms = (time.perf_counter() - t0) * 1000

        text_blocks = [b for b in r.content if b.type == "text"]
        text = text_blocks[0].text.strip() if text_blocks else ""
        if text.startswith("```"):
            text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            print(f"  [{self._label}] malformed JSON: {text[:120]}")
            return None

        return parsed, latency_ms, r.usage

    def _extract_answers(self, task: dict, parsed: dict, case_id: int) -> dict | None:
        answers = {}
        for q in task["questions"]:
            qname = q["name"]
            conf_key = f"{qname}_confidence"

            if qname not in parsed:
                print(f"  [{self._label}] case {case_id} missing key '{qname}'")
                return None

            val = parsed[qname]
            confidence = parsed.get(conf_key, parsed.get("confidence", 0.5))

            if q["type"] == "choice":
                answers[qname] = {"value": str(val).lower(), "confidence": float(confidence)}
            elif q["type"] == "noul":
                if isinstance(val, bool):
                    answers[qname] = {"value": val, "confidence": float(confidence)}
                else:
                    answers[qname] = {"value": bool(val), "confidence": float(confidence)}
            elif q["type"] == "score":
                answers[qname] = {"value": float(val), "confidence": float(confidence)}

        return answers
