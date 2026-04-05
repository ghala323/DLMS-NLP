from rapidfuzz import fuzz

HIGH_KEYWORDS = [
    "تقسيم الإرث", "تقسيم التركة", "حصر الورثة", "وثيقة إرث",
    "شهادة وفاة", "مبلغ مستحق", "سداد دين", "فدية صيام",
    "زكاة فطرة", "قضاء", "كفارات", "إقرار مديونية",
    "إقرار أمانات", "وثيقة وصية", "وصية شرعية", "إقرار زكاة",
    "إقرار كفارات", "إقرار فدية",
]

MEDIUM_KEYWORDS = [
    "رقم هوية", "رقم الهوية الوطنية", "هوية وطنية", "بطاقة الهوية",
    "رقم السجل المدني", "بيانات الهوية", "إثبات هوية",
    "حساب بنكي", "رقم الحساب", "بطاقة بنكية", "بطاقة ائتمان",
    "بطاقة مصرفية", "بيانات الحساب", "كشف حساب", "رقم الآيبان", "IBAN",
    "تحويل بنكي", "وثيقة رسمية", "وثيقة قانونية", "عقد رسمي",
    "عقد بيع", "عقد إيجار", "اتفاقية", "إقرار قانوني",
    "تفويض رسمي", "توكيل شرعي", "وكالة شرعية", "صك ملكية",
    "رقم الصك", "العقار", "عقار", "ملكية عقار", "أرض",
    "قطعة أرض", "ملكية الأرض", "وصية", "وصية شرعية",
    "تركة مالية", "تركة عقارية", "مجمع تجاري", "عقد شراكة",
]

LOW_KEYWORDS = [
    "فاتورة كهرباء", "فاتورة ماء", "فاتورة هاتف", "وصل استلام",
    "نموذج طلب", "تقرير شهري", "إيصال دفع", "شهادة حضور",
    "مراسلة بريدية", "مذكرة داخلية",
]

THRESHOLD = 0.8


def preprocess(text):
    return text.strip().lower() if text else ""


def fuzzy_match_score(text, keyword_list):
    text = preprocess(text)
    scores = []
    for keyword in keyword_list:
        score = fuzz.token_set_ratio(text, keyword) / 100
        if keyword.lower() in text:
            score += 0.1
        score = min(score, 1.0)
        scores.append(score)
    return max(scores) if scores else 0.0


def classify_rule_based(text):
    """Classify text into High/Medium/Low based on keyword matching."""
    high_score   = fuzzy_match_score(text, HIGH_KEYWORDS)
    medium_score = fuzzy_match_score(text, MEDIUM_KEYWORDS)
    low_score    = fuzzy_match_score(text, LOW_KEYWORDS)

    scores = {"High": high_score, "Medium": medium_score, "Low": low_score}
    best = max(scores, key=scores.get)

    if scores[best] < THRESHOLD:
        return "Unclassified", scores
    return best, scores
