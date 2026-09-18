import json
import os
import time

import requests

from .base import BaseRunner

DECISIONS_URL = "https://openrouter.ai/api/alpha/decisions"


def _build_questions(task: dict) -> dict:
    qs = {}
    for q in task["questions"]:
        entry = {
            "type": q["type"],
            "instructions": q["instructions"],
        }
        if "criteria" in q and q["criteria"] is not None:
            if q["type"] == "choice":
                criteria = {}
                for key, val in q["criteria"].items():
                    if isinstance(val, list):
                        criteria[key] = ", ".join(val)
                    elif val is None:
                        criteria[key] = None
                    else:
                        criteria[key] = str(val)
                entry["criteria"] = criteria
            else:
                entry["criteria"] = q["criteria"]
        qs[q["name"]] = entry
    return qs


class JevRunner(BaseRunner):
    def __init__(self):
        self._api_key = os.environ.get("OPENROUTER_API_KEY")
        if not self._api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY not set. "
                "Get one at https://openrouter.ai/settings/keys"
            )

    def name(self) -> str:
        return "jev"

    def model_string(self) -> str:
        return "typesafe/jev-1.13"

    def run_case(self, task: dict, case: dict) -> dict | None:
        questions = _build_questions(task)

        payload = {
            "model": "typesafe/jev-1.13",
            "state": case["text"],
            "questions": questions,
        }

        t0 = time.perf_counter()
        try:
            resp = requests.post(
                DECISIONS_URL,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                data=json.dumps(payload),
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"  [jev] case {case['id']} failed: {e}")
            return None
        latency_ms = (time.perf_counter() - t0) * 1000

        raw_answers = data.get("answers", {})
        answers = {}

        for q in task["questions"]:
            qname = q["name"]
            try:
                ans = raw_answers[qname]

                if q["type"] == "choice":
                    probs = ans.get("probabilities", {})
                    conf = ans.get("confidence", max(probs.values(), default=0.5))
                    answers[qname] = {
                        "value": ans["choice"],
                        "confidence": conf,
                    }

                elif q["type"] == "noul":
                    noul_prob = ans["noul"]
                    answers[qname] = {
                        "value": noul_prob > 0.5,
                        "confidence": max(noul_prob, 1 - noul_prob),
                    }

                elif q["type"] == "score":
                    num_criteria = len(q.get("criteria", []))
                    raw_score = ans["score"]
                    normalized = (
                        raw_score / (num_criteria - 1)
                        if num_criteria > 1
                        else raw_score
                    )
                    normalized = max(0.0, min(1.0, normalized))
                    answers[qname] = {
                        "value": normalized,
                        "confidence": ans.get("confidence", 0.5),
                    }

            except Exception as e:
                print(
                    f"  [jev] case {case['id']} question '{qname}' "
                    f"parse error: {e}"
                )
                return None

        usage = data.get("usage", {})
        input_tokens = usage.get("input_tokens", usage.get("prompt_tokens", 0))
        output_tokens = usage.get("output_tokens", usage.get("completion_tokens", 0))

        return {
            "answers": answers,
            "latency_ms": latency_ms,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        }
