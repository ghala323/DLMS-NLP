import os
import pickle

MODEL_PATH = os.path.join(os.path.dirname(__file__), "tfidf_classifier.pkl")
_pipeline = None


def load_pipeline():
    global _pipeline
    if _pipeline is None:
        with open(MODEL_PATH, "rb") as f:
            _pipeline = pickle.load(f)
    return _pipeline


def classify_ml(text):
    """
    Classify Arabic text using TF-IDF + Logistic Regression.
    Returns (label, score) where label is High/Medium/Low/Unclassified.
    """
    if not text or not text.strip():
        return "Unclassified", 0.0
    try:
        pipeline = load_pipeline()
        label = pipeline.predict([text])[0]
        proba = pipeline.predict_proba([text])[0]
        classes = list(pipeline.classes_)
        score = float(proba[classes.index(label)])
        return label, score
    except Exception as e:
        print(f"classify_ml error: {e}")
        return "Unclassified", 0.0
