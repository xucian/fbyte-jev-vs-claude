# "Can a Mute Model Beat the Loudest LLMs?"
## Jev vs Claude Opus 4.6 vs Sonnet 4.6 — Benchmark Design

> Hand this to your coding agent. It has everything.

---

## Models

| Model | Provider | Model String | Input $/1M | Output $/1M |
|-------|----------|-------------|-----------|-------------|
| **Jev** | OpenRouter | `typesafe/jev-1.13` | $0.042 | $0 (free) |
| **Opus 4.6** | Anthropic | `claude-opus-4-6` | $15.00 | $75.00 |
| **Sonnet 4.6** | Anthropic | `claude-sonnet-4-6` | $3.00 | $15.00 |

### API Keys (env vars)
```
OPENROUTER_API_KEY   — for Jev via OpenRouter
ANTHROPIC_API_KEY    — for Claude models
```

### Grid: 5 tasks × 3 models = 15 runs, 20 cases each = 300 API calls total

---

## Architecture

```
benchmark/
├── run.py              # CLI: python run.py [--model jev|opus|sonnet] [--task bouncer|...]
├── tasks.py            # 5 task definitions with 20 hardcoded cases + ground truth
├── runners/
│   ├── base.py         # Abstract: run_case(task, case) → {answer, confidence, latency_ms, tokens, cost}
│   ├── jev_runner.py   # TypeSafe Python SDK (typesafe-sdk) via OpenRouter
│   └── claude_runner.py# Anthropic SDK
├── scoring.py          # Compares predictions to ground truth, computes metrics
├── report.py           # Reads results.json → generates report.html
├── results.json        # Raw output (auto-generated)
└── report.html         # Eye candy (auto-generated)
```

### Dependencies
```
pip install typesafe-sdk anthropic
```

---

## Jev Runner — TypeSafe Python SDK

```python
from typesafe_sdk import TypeSafeClient, Choice, Noul, Score

# NOTE: Jev is on OpenRouter as typesafe/jev-1.13
# But the TypeSafe SDK hits api.typesafe.ai directly.
# Use the SDK — it's the clean way. Env var: TYPESAFE_API_KEY

with TypeSafeClient() as client:
    response = client.system_one(
        state={"message": "My card was charged twice"},
        questions={
            "department": Choice(
                instructions="Which team handles this?",
                criteria={
                    "billing": ["Charges", "Invoices", "Refunds"],
                    "technical": ["Bugs", "Outages"],
                    "other": None,
                },
            ),
            "urgent": Noul(instructions="Is this urgent?"),
            "severity": Score(
                instructions="How severe?",
                criteria=["cosmetic", "workaround exists", "blocking"],
            ),
        },
    )

# Jev returns native confidence + probabilities per option
response.choices["department"].choice       # "billing"
response.choices["department"].confidence   # 0.92
response.choices["department"].probabilities # {"billing": 0.87, "technical": 0.08, "other": 0.05}
response.nouls["urgent"].noul               # 0.85 (probability of yes)
response.nouls["urgent"].confidence         # 0.91
response.scores["severity"].score           # 1.7
response.scores["severity"].confidence      # 0.88
```

---

## Claude Runner — Must Also Return Confidence

```python
import anthropic, json

client = anthropic.Anthropic()

SYSTEM = """You are a structured decision model. For each question, return ONLY valid JSON.
Every answer MUST include a "confidence" field (0.0–1.0) representing how certain you are.
Do NOT explain. Do NOT add commentary. JSON only."""

def classify(model: str, task_prompt: str) -> dict:
    r = client.messages.create(
        model=model,  # "claude-opus-4-6" or "claude-sonnet-4-6"
        max_tokens=300,
        temperature=0,
        system=SYSTEM,
        messages=[{"role": "user", "content": task_prompt}],
    )
    return json.loads(r.content[0].text)

# Example output from Claude:
# {"department": "billing", "confidence": 0.93}
```

**Key difference:** Jev's confidence is *calibrated* (trained against outcomes).
Claude's confidence is *self-reported* (it says how sure it thinks it is).
Comparing these is part of the narrative — "Is the one who CAN'T explain itself
more honest about what it doesn't know?"

---

## 5 Tasks — Design for Maximum Narrative Punch

Each task is chosen to test a different failure mode and create visual variety
in the report. All accuracy-first. Speed is logged but secondary.

---

### Task 1: "The Bouncer" 🚪 — Single-Label Intent Routing

**What:** 20 customer messages → classify into 1 of 8 departments
**Jev questions:** 1× Choice (8 options)
**Claude prompt:** Classify + confidence
**Why it's hard:** Deliberately ambiguous multi-intent messages where one is dominant.

**Departments:** `billing`, `technical`, `account`, `shipping`, `returns`, `sales`, `security`, `other`

Example cases (hardcode 20):
```
"My card was charged twice but I also can't log in"              → billing
"I want to upgrade but your pricing page is broken"              → technical
"Someone else is buying stuff with my account"                   → security
"When will my refund ship back to my card?"                      → returns (not shipping, not billing)
"Do you have an API? I'd like to integrate."                     → sales
"I changed my email but now I can't reset my password"           → account
"Your app crashes every time I open the notifications tab"       → technical
"I'm a reseller — can I get volume pricing?"                     → sales
"My package says delivered but I never got it"                   → shipping
"I just got a password reset email I didn't request"             → security
```
+ 10 more in the same style, all intentionally ambiguous.

**Scoring:** Exact match = 1.0, else 0.0

---

### Task 2: "The Lie Detector" 🔍 — Fake Review Detection

**What:** 20 product reviews → multi-question evaluation
**Jev questions:** 1× Choice (sentiment), 1× Score (fakeness), 1× Noul (contains PII)
**Claude prompt:** Return JSON with all three + confidence per field

**Why it's hard:** Fake reviews have subtle tells. PII detection has edge cases.
Mix of Amazon-style reviews: genuine raves, genuine complaints, astroturfed praise,
competitor sabotage, reviews with accidental PII.

Example:
```
"I've been using this blender for 3 months and it's AMAZING!!!
 Model XR-7700B is the best $49.99 purchase. Buy from amzn.link/d/abc123"
→ sentiment: positive, fakeness: 0.7, pii: false

"Bought this for my daughter Sarah at 123 Oak St, it broke day one.
 Absolute garbage. Called support and John employee #4421 was rude."
→ sentiment: negative, fakeness: 0.1, pii: true
```

**Scoring:**
- Sentiment: exact match (1 or 0)
- Fakeness: 1 - abs(predicted - truth) (continuous, closer = better)
- PII: exact match (1 or 0)
- Case score = mean of three

---

### Task 3: "The Oracle" 🔮 — Bug Triage

**What:** 20 bug reports → priority + component + is_regression
**Jev questions:** 2× Choice + 1× Noul
**Claude prompt:** Return JSON with all three + confidence

**Why it's hard:** Severity != priority. Regression requires temporal reading.

**Priority:** `P0` `P1` `P2` `P3` `P4`
**Component:** `auth` `payments` `api` `ui` `database` `infra` `notifications` `other`

Example:
```
"After deploying v2.3.1, none of our EU customers can check out.
 Payment gateway returns 502. Was fine on v2.3.0."
→ P0, payments, regression: true

"The loading spinner is blue instead of our brand purple.
 It's been like this since we launched."
→ P4, ui, regression: false
```

**Scoring:**
- Priority: exact = 1.0, within-1 = 0.5, else 0.0
- Component: exact match (1 or 0)
- Regression: exact match (1 or 0)
- Case score = mean of three

---

### Task 4: "The Bartender" 🍸 — Multi-Axis Content Moderation

**What:** 20 user-generated comments → toxic? + category + severity score
**Jev questions:** 1× Noul (is_toxic), 1× Choice (category), 1× Score (severity)
**Claude prompt:** Return JSON with all three + confidence

**Why it's hard:** Sarcasm, coded language, context-dependent offensiveness,
and comments that LOOK toxic but aren't (passionate sports fans, dark humor
that's self-directed). Mix of social media comments.

**Categories:** `hate_speech`, `harassment`, `threat`, `sexual`, `self_harm`, `spam`, `clean`

Example:
```
"I hope your team loses so badly they disband the franchise forever lol"
→ toxic: false, category: clean, severity: 0.1 (hyperbolic sports talk)

"People like you shouldn't be allowed to have opinions. Crawl back to your hole."
→ toxic: true, category: harassment, severity: 0.8

"kys lol ratio + didn't ask + L + maidenless"
→ toxic: true, category: harassment, severity: 0.6 (internet slang, still harmful)

"Just mass-reported this guy's account from 12 alts 😂"
→ toxic: true, category: spam, severity: 0.5

"As a cancer survivor, I can joke about dying — it's MY coping mechanism"
→ toxic: false, category: clean, severity: 0.0 (self-directed, not harmful)
```

**Scoring:**
- Toxic: exact match on Noul threshold (>0.5 = toxic)
- Category: exact match (1 or 0)
- Severity: 1 - abs(predicted - truth)
- Case score = mean of three

---

### Task 5: "The Customs Agent" 🛂 — Contract Clause Classification

**What:** 20 contract clause excerpts → clause type + risk level + needs_lawyer
**Jev questions:** 1× Choice (clause_type), 1× Score (risk), 1× Noul (needs_lawyer)
**Claude prompt:** Return JSON with all three + confidence

**Why it's hard:** Legal language is dense. Risk depends on WHOSE side you're on
(we always evaluate from "your company signing this" perspective). Some
innocuous-sounding clauses are actually dangerous.

**Clause types:** `liability_cap`, `indemnification`, `termination`, `ip_assignment`,
`non_compete`, `confidentiality`, `payment_terms`, `force_majeure`, `other`

Example:
```
"Contractor assigns all intellectual property created during the engagement,
 including any derivative works, to Company in perpetuity."
→ type: ip_assignment, risk: 0.9, needs_lawyer: true

"Either party may terminate this agreement with 30 days written notice."
→ type: termination, risk: 0.1, needs_lawyer: false

"Company shall not be liable for any indirect, incidental, or consequential
 damages, regardless of the cause of action or theory of liability."
→ type: liability_cap, risk: 0.8, needs_lawyer: true
```

**Scoring:**
- Clause type: exact match (1 or 0)
- Risk: 1 - abs(predicted - truth)
- Needs lawyer: exact match (1 or 0)
- Case score = mean of three

---

## Confidence Calibration — The Secret 6th Metric

For each model, compute **calibration error** across all 100 predictions:
- Bucket predictions by reported confidence (0.0–0.2, 0.2–0.4, ..., 0.8–1.0)
- In each bucket, measure actual accuracy
- Perfect calibration: 80% confident predictions are right 80% of the time
- Expected Calibration Error (ECE) = weighted mean |accuracy - confidence| per bucket

This is Jev's *claimed* superpower. If it actually delivers better calibration
than Claude, that's the video's thesis confirmed. If not, even better drama.

**Show this as a calibration plot in the HTML** — predicted confidence (x) vs
actual accuracy (y). Perfect = diagonal. Overconfident = below diagonal.

---

## Metrics Summary

For each of the 15 runs (model × task):

```json
{
  "model": "jev",
  "task": "bouncer",
  "cases": [
    {
      "id": 1,
      "input": "...",
      "expected": {"department": "billing"},
      "predicted": {"department": "billing"},
      "confidence": 0.92,
      "score": 1.0,
      "latency_ms": 42,
      "input_tokens": 156,
      "output_tokens": 0,
      "cost_usd": 0.0000065
    }
  ],
  "summary": {
    "accuracy": 0.85,
    "mean_confidence": 0.78,
    "calibration_error": 0.04,
    "median_latency_ms": 45,
    "p95_latency_ms": 120,
    "total_cost_usd": 0.00013,
    "cost_per_correct_usd": 0.0000076
  }
}
```

---

## HTML Report Design

### Vibe: "Sci-fi mission control meets Fireship"
Dark bg (#0a0a0f). Neon accents. Monospace data. Smooth animations.
Single self-contained HTML file. `results.json` embedded as `<script>const RESULTS = {...}</script>`.

### Colors
- Jev: electric cyan `#00f0ff`
- Opus 4.6: deep purple `#8b5cf6`
- Sonnet 4.6: hot orange `#f97316`

### Fonts (Google Fonts)
- Headlines: `JetBrains Mono`
- Body: `Inter`

### Sections (scroll down):

**1. Hero**
`CAN A MUTE MODEL BEAT THE LOUDEST LLMS?`
`Jev vs Opus 4.6 vs Sonnet 4.6 · 5 tasks · 15 runs · 1 truth`
Typing animation on subtitle.

**2. The Accuracy Gauntlet** (THE main section)
5 grouped bar charts, one per task. Each has 3 bars (one per model).
Show accuracy % on the bar. Highlight winner with a glow effect.
Below each chart: task name + emoji + one-liner description.

**3. Confidence vs Reality** (the spicy chart)
Calibration plot. X = model's reported confidence, Y = actual accuracy.
Diagonal line = perfection. Each model is a line/scatter.
If Jev hugs the diagonal and Claude is overconfident — chef's kiss for the video.
If the reverse — also great, different narrative.

**4. Speed Race** (secondary but visual)
Horizontal bars per task racing left→right. Jev comically fast.
Show median latency. Label: "Yeah, speed isn't the question. But still."

**5. The Money Shot** 💰
Cost per task, log scale. Show "multiplier" annotations:
"For the price of 1 Opus call, Jev runs [N] times"

**6. The Scoreboard**
Full table: 5 rows (tasks) × 3 columns (models).
Each cell: accuracy% / confidence% / latency / cost.
Color cells: green=best, red=worst per row.

**7. The Verdict**
Overall winner by mean accuracy across all 5 tasks.
Big emoji + one-liner. Generated dynamically from results:
- Best accuracy → 🏆
- Best calibration → 🎯
- Best value (accuracy/cost) → 💰
- Speed demon → ⚡

### Animations
- IntersectionObserver for scroll-triggered entrance
- Numbers count up from 0
- Bars grow with ease-out
- Keep it snappy — under 800ms per animation

---

## Implementation Notes

1. **Hardcode all 100 test cases** (20 per task). Make them genuinely hard.
   No softballs. Each case: `{"id": int, "text": str, "ground_truth": dict}`.

2. **Jev via Python SDK is cleanest.** `pip install typesafe-sdk`.
   Env var: `TYPESAFE_API_KEY`. If early access is unavailable,
   the runner should catch the error and skip gracefully.

3. **Claude structured output:** Use `temperature=0`. System prompt demands
   JSON with confidence. Parse with `json.loads()`, handle malformed JSON
   with a retry (once) or score as 0.

4. **For Claude confidence:** The prompt must explicitly say
   "Include a confidence field (0.0–1.0) for each decision."
   This is self-reported, not calibrated — that's the point.

5. **Timing:** `time.perf_counter()` around the API call. Just the round-trip.

6. **Error handling:** If a model fails on a case, mark it null. Report renders
   with whatever completed. Don't crash the whole run.

7. **CLI:**
   ```bash
   python run.py                    # All 15 runs
   python run.py --model jev        # Jev only
   python run.py --task bouncer     # One task, all models
   python report.py                 # Generate HTML from results.json
   ```

8. **The HTML must be self-contained.** No external JS libs except Google Fonts.
   Vanilla CSS animations. Embed results.json inline.
