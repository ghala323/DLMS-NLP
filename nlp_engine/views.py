from rest_framework.decorators import api_view
from rest_framework.response import Response
from .rule_based import classify_rule_based, fuzzy_match_score
from .ml_model import classify_ml
from .hybrid import final_classification
from .models import AnalysisResult


@api_view(["POST"])
def test_fuzzy(request):
    """Test rule-based classification on raw text."""
    text = request.data.get("text", "").strip()
    if not text:
        return Response({"error": "No text provided"}, status=400)

    label, scores = classify_rule_based(text)
    return Response({
        "text":        text,
        "label":       label,
        "score_high":  scores["High"],
        "score_medium":scores["Medium"],
        "score_low":   scores["Low"],
    })


@api_view(["POST"])
def test_ml(request):
    """Test ML classification on raw text."""
    text = request.data.get("text", "").strip()
    if not text:
        return Response({"error": "No text provided"}, status=400)

    label, score = classify_ml(text)
    return Response({
        "text":  text,
        "label": label,
        "score": score,
    })


@api_view(["POST"])
def classify(request):
    """
    Full hybrid classification endpoint.
    Accepts: { "text": "..." }
    Returns: level, scores, and saves result to DB.
    """
    text = request.data.get("text", "").strip()
    if not text:
        return Response({"error": "No text provided"}, status=400)

    result = final_classification(text)

    try:
        AnalysisResult.objects.create(
            text=text,
            fuzzy_score=result["fuzzy_score"],
            ml_score=result["ml_score"],
            final_score=result["final_score"],
            level=result["level"],
        )
    except Exception as e:
        print(f"DB save warning: {e}")

    return Response(result)


@api_view(["POST"])
def test_hybrid(request):
    """Alias for /classify — kept for backwards compatibility."""
    return classify(request)
