from .rule_based import HIGH_KEYWORDS, MEDIUM_KEYWORDS, LOW_KEYWORDS, fuzzy_match_score
from .ml_model import ml_score

def preprocess(text):
    return text.strip().lower() if text else ""

def final_classification(text):
    text = preprocess(text)

    fuzzy = fuzzy_match_score(text)
    
    try:
        ml = ml_score(text)
    except:
        ml = 0

    # --------- تحديد المستوى حسب الكلمات مباشرة ---------
    text_lower = text.lower()
    level = None

    # تحقق أولاً من High Keywords
    if any(k.lower() in text_lower for k in HIGH_KEYWORDS):
        level = "HIGH"
    elif any(k.lower() in text_lower for k in MEDIUM_KEYWORDS):
        level = "MEDIUM"
    elif any(k.lower() in text_lower for k in LOW_KEYWORDS):
        level = "LOW"
    
    # --------- إذا ما طابق أي كلمة، نستخدم score كخطة بديلة ---------
    if not level:
        # وزن أفضل للـ fuzzy
        final_score = (0.3 * fuzzy) + (0.7 * ml)
        if final_score >= 0.85:
            level = "HIGH"
        elif final_score >= 0.5:
            level = "MEDIUM"
        else:
            level = "LOW"
    else:
        # إذا تم تحديد Level بالكلمة، نقدر نحسب final_score متوسط للتقرير
        final_score = (0.3 * fuzzy) + (0.7 * ml)

    return {
        "fuzzy_score": fuzzy,
        "ml_score": ml,
        "final_score": final_score,
        "level": level
    }
