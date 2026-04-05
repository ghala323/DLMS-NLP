from .rule_based import (
    HIGH_KEYWORDS, MEDIUM_KEYWORDS, LOW_KEYWORDS,
    fuzzy_match_score, classify_rule_based
)
from .ml_model import classify_ml


def preprocess(text):
    return text.strip().lower() if text else ""


def final_classification(text):
    """
    Hybrid classifier combining rule-based fuzzy matching and TF-IDF ML model.
    Returns a dict with scores and final level (High/Medium/Low).
    """
    text = preprocess(text)

    # Rule-based scores per category
    fuzzy_high   = fuzzy_match_score(text, HIGH_KEYWORDS)
    fuzzy_medium = fuzzy_match_score(text, MEDIUM_KEYWORDS)
    fuzzy_low    = fuzzy_match_score(text, LOW_KEYWORDS)

    # ML scores per category
    ml_label, ml_confidence = classify_ml(text)
    ml_high   = ml_confidence if ml_label == "High"   else 0.0
    ml_medium = ml_confidence if ml_label == "Medium" else 0.0
    ml_low    = ml_confidence if ml_label == "Low"    else 0.0

    # Combined scores: 70% rule-based, 30% ML
    score_high   = round((0.7 * fuzzy_high)   + (0.3 * ml_high),   4)
    score_medium = round((0.7 * fuzzy_medium) + (0.3 * ml_medium), 4)
    score_low    = round((0.7 * fuzzy_low)    + (0.3 * ml_low),    4)

    scores = {"High": score_high, "Medium": score_medium, "Low": score_low}
    level = max(scores, key=scores.get)

    # Fallback if all scores are very low
    if scores[level] < 0.2:
        level = "Low"

    return {
        "level":        level,
        "fuzzy_score":  max(fuzzy_high, fuzzy_medium, fuzzy_low),
        "ml_label":     ml_label,
        "ml_score":     round(ml_confidence, 4),
        "final_score":  scores[level],
        "score_high":   score_high,
        "score_medium": score_medium,
        "score_low":    score_low,
    }
