from rest_framework.decorators import api_view
from rest_framework.response import Response
from .rule_based import fuzzy_match_score, is_sensitive
from .ml_model import ml_score, is_sensitive_ml
from .hybrid import final_classification
from .models import AnalysisResult


@api_view(['POST'])
def test_fuzzy(request):
    text = request.data.get('text', '').strip()
    if not text:
        return Response({"error": "No text provided"}, status=400)

    fuzzy = fuzzy_match_score(text)
    is_rule, _ = is_sensitive(text)

    return Response({
        "text": text,
        "fuzzy_score": fuzzy,
        "is_sensitive_rule": is_rule
    })


@api_view(['POST'])
def test_ml(request):
    text = request.data.get('text', '').strip()
    if not text:
        return Response({"error": "No text provided"}, status=400)

    ml = ml_score(text)
    is_ml, _ = is_sensitive_ml(text)

    return Response({
        "text": text,
        "ml_score": ml,
        "is_sensitive_ml": is_ml
    })


@api_view(['POST'])
def test_hybrid(request):
    """
    تحلل النص باستخدام الHybrid:
    - أولاً Rule-based
    - بعدين ML
    - تحسب Final Score
    - تحدد المستوى Level
    - تخزن في قاعدة البيانات
    """
    text = request.data.get('text', '').strip()
    if not text:
        return Response({"error": "No text provided"}, status=400)

    result = final_classification(text)

    # حفظ النتيجة في DB مع حماية ضد الأخطاء
    try:
        AnalysisResult.objects.create(
            text=text,
            fuzzy_score=result['fuzzy_score'],
            ml_score=result['ml_score'],
            final_score=result['final_score'],
            level=result['level']
        )
    except Exception as e:
        return Response({"error": f"Database error: {str(e)}"}, status=500)

    return Response(result)
