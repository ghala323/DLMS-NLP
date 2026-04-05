"""
Retrain the TF-IDF classifier on labeled documents in documentstest/.
Run this whenever new labeled documents are added:
    python train_tfidf.py
"""
import os
import sys
import pickle
import django

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

from pdf2image import convert_from_path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

POPPLER_PATH = r"C:\Users\acer\Desktop\poppler\poppler-25.12.0\Library\bin"
DOCS_DIR = os.path.join(os.path.dirname(__file__), "documentstest")
MODEL_OUT = os.path.join(os.path.dirname(__file__), "nlp_engine", "tfidf_classifier.pkl")

LABEL_MAP = {"HIGH": "High", "MEDIUM": "Medium", "LOW": "Low"}

def extract_text(pdf_path):
    text = ""
    try:
        images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
        for img in images:
            text += pytesseract.image_to_string(img, lang="ara") + " "
    except Exception as e:
        print(f"  OCR error for {pdf_path}: {e}")
    return text.strip()

def get_label(filename):
    name = os.path.basename(filename).upper()
    for key in LABEL_MAP:
        if name.startswith(key):
            return LABEL_MAP[key]
    return None

def main():
    print("Scanning documentstest/ for labeled PDFs...")
    texts, labels = [], []

    for fname in sorted(os.listdir(DOCS_DIR)):
        if not fname.lower().endswith(".pdf"):
            continue
        label = get_label(fname)
        if not label:
            print(f"  Skipping (no label): {fname}")
            continue
        path = os.path.join(DOCS_DIR, fname)
        print(f"  [{label}] {fname}")
        text = extract_text(path)
        if text:
            texts.append(text)
            labels.append(label)
        else:
            print(f"  Warning: empty text for {fname}")

    print(f"\nTotal: {len(texts)} documents")
    print(f"  High: {labels.count('High')} | Medium: {labels.count('Medium')} | Low: {labels.count('Low')}")

    if len(set(labels)) < 2:
        print("ERROR: Need at least 2 categories to train. Add more documents.")
        return

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(2, 4),
            max_features=5000,
            sublinear_tf=True,
        )),
        ("clf", LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            C=1.0,
        )),
    ])

    pipeline.fit(texts, labels)
    y_pred = pipeline.predict(texts)

    print("\n===== Training Report =====")
    print(classification_report(labels, y_pred, zero_division=0))

    with open(MODEL_OUT, "wb") as f:
        pickle.dump(pipeline, f)
    print(f"Model saved to: {MODEL_OUT}")

if __name__ == "__main__":
    main()
