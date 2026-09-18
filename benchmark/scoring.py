import math

from tasks import PRIORITY_ORDER


def score_question(qname: str, predicted_value, expected_value, scoring_type: str) -> float:
    if predicted_value is None:
        return 0.0

    if scoring_type == "exact":
        if isinstance(expected_value, bool):
            return 1.0 if bool(predicted_value) == expected_value else 0.0
        return 1.0 if str(predicted_value).lower() == str(expected_value).lower() else 0.0

    if scoring_type == "continuous":
        try:
            return max(0.0, 1.0 - abs(float(predicted_value) - float(expected_value)))
        except (ValueError, TypeError):
            return 0.0

    if scoring_type == "within_one":
        pred_str = str(predicted_value).upper()
        exp_str = str(expected_value).upper()
        if pred_str == exp_str:
            return 1.0
        try:
            pi = PRIORITY_ORDER.index(pred_str)
            ei = PRIORITY_ORDER.index(exp_str)
            return 0.5 if abs(pi - ei) == 1 else 0.0
        except ValueError:
            return 0.0

    return 0.0


def score_case(task: dict, result: dict, case: dict) -> dict:
    """Score a single case. Returns {question_scores, score, confidence}."""
    answers = result["answers"]
    gt = case["ground_truth"]
    scoring = task["scoring"]

    question_scores = {}
    confidences = []

    for q in task["questions"]:
        qname = q["name"]
        if qname not in answers:
            question_scores[qname] = 0.0
            continue

        predicted = answers[qname]["value"]
        expected = gt[qname]
        question_scores[qname] = score_question(qname, predicted, expected, scoring[qname])
        confidences.append(answers[qname]["confidence"])

    score = sum(question_scores.values()) / len(question_scores) if question_scores else 0.0
    confidence = sum(confidences) / len(confidences) if confidences else 0.0

    return {
        "question_scores": question_scores,
        "score": score,
        "confidence": confidence,
    }


def compute_ece(predictions: list[dict], num_bins: int = 5) -> float:
    """Expected Calibration Error across a list of {confidence, score} dicts."""
    bins = [[] for _ in range(num_bins)]
    for p in predictions:
        conf = p["confidence"]
        idx = min(int(conf * num_bins), num_bins - 1)
        bins[idx].append(p)

    ece = 0.0
    total = len(predictions)
    if total == 0:
        return 0.0

    for b in bins:
        if not b:
            continue
        avg_conf = sum(p["confidence"] for p in b) / len(b)
        avg_acc = sum(p["score"] for p in b) / len(b)
        ece += (len(b) / total) * abs(avg_acc - avg_conf)

    return ece


def compute_calibration_curve(predictions: list[dict], num_bins: int = 5) -> list[dict]:
    """Returns [{bin_center, avg_confidence, avg_accuracy, count}] for plotting."""
    bins = [[] for _ in range(num_bins)]
    for p in predictions:
        idx = min(int(p["confidence"] * num_bins), num_bins - 1)
        bins[idx].append(p)

    curve = []
    for i, b in enumerate(bins):
        center = (i + 0.5) / num_bins
        if b:
            curve.append({
                "bin_center": center,
                "avg_confidence": sum(p["confidence"] for p in b) / len(b),
                "avg_accuracy": sum(p["score"] for p in b) / len(b),
                "count": len(b),
            })
        else:
            curve.append({
                "bin_center": center,
                "avg_confidence": None,
                "avg_accuracy": None,
                "count": 0,
            })
    return curve
