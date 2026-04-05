import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Tesseract path
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Poppler path
POPPLER_PATH = r'C:\Users\acer\Desktop\poppler\poppler-25.12.0\Library\bin'

# Now import NLP modules
from nlp_engine.ml_model import classify_ml as ml_score
from nlp_engine.rule_based import classify_rule_based
from nlp_engine.hybrid import final_classification
from sklearn.metrics import classification_report
from PIL import Image
from pdf2image import convert_from_path


# ── Test files and their true labels ─────────────────────────
test_files = [
    "documentstest/HIGH (1).pdf",
    "documentstest/HIGH (2).pdf",
    "documentstest/HIGH (3).pdf",
    "documentstest/HIGH (4).pdf",
    "documentstest/HIGH (6).pdf",
    "documentstest/HIGH (8).pdf",
    "documentstest/HIGH (9).pdf",
    "documentstest/HIGH.pdf",
    "documentstest/HIGH5.pdf",
    "documentstest/MEDIUM (2).pdf",
    "documentstest/MEDIUM (3).pdf",
    "documentstest/MEDIUM (4).pdf",
    "documentstest/MEDIUM (5).pdf",
    "documentstest/MEDIUM.pdf",
    "documentstest/LOW (1).pdf",
    "documentstest/LOW (2).pdf",
    "documentstest/LOW (3).pdf",
]

y_true = [
    "HIGH", "HIGH", "HIGH", "HIGH", "HIGH",
    "HIGH", "HIGH", "HIGH", "HIGH",
    "MEDIUM", "MEDIUM", "MEDIUM", "MEDIUM", "MEDIUM",
    "LOW", "LOW", "LOW",
]

# ── Text extraction functions ─────────────────────────────────
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
        for img in images:
            page_text = pytesseract.image_to_string(img, lang="ara")
            text += page_text + " "
    except Exception as e:
        print(f"PDF extraction error for {pdf_path}: {e}")
    return text.strip()

def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)
        return pytesseract.image_to_string(image, lang="ara").strip()
    except Exception as e:
        print(f"Image extraction error: {e}")
        return ""

def extract_text_from_txt(txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        return f.read().strip()

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".txt":
        return extract_text_from_txt(file_path)
    else:
        return extract_text_from_image(file_path)

# ── Run classification on each file ──────────────────────────
y_pred_ml     = []
y_pred_rule   = []
y_pred_hybrid = []

print("Processing files...")
print("=" * 50)

for i, file_path in enumerate(test_files):
    print(f"\n[{i+1}/{len(test_files)}] {file_path}")

    text = extract_text(file_path)
    print(f"Extracted text preview: {text[:100]}...")

    # ML prediction
    _, score_ml = ml_score(text)
    if score_ml > 0.6:
        level_ml = "HIGH"
    elif score_ml > 0.3:
        level_ml = "MEDIUM"
    else:
        level_ml = "LOW"
    y_pred_ml.append(level_ml)

    # Rule-based prediction
    rule_label, _ = classify_rule_based(text)
    level_rule = rule_label.upper()
    y_pred_rule.append(level_rule)

    # Hybrid prediction
    hybrid_result = final_classification(text)
    level_hybrid = hybrid_result["level"].upper()
    y_pred_hybrid.append(level_hybrid)

    print(f"True: {y_true[i]} | ML: {level_ml} | Rule: {level_rule} | Hybrid: {level_hybrid}")

# ── Print classification reports ─────────────────────────────
labels = ["LOW", "MEDIUM", "HIGH"]

print("\n" + "=" * 50)
print("===== ML Model Report =====")
print(classification_report(y_true, y_pred_ml, labels=labels, zero_division=0))

print("===== Rule Based Report =====")
print(classification_report(y_true, y_pred_rule, labels=labels, zero_division=0))

print("===== Hybrid Report =====")
print(classification_report(y_true, y_pred_hybrid, labels=labels, zero_division=0))

print("=" * 50)
print("Testing complete!")