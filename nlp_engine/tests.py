from django.test import TestCase
from .ml_model import ml_score
from .rule_based import is_sensitive
from .hybrid import final_classification

from sklearn.metrics import classification_report
from PIL import Image, ImageOps
import pytesseract
from pdf2image import convert_from_path
import os


class SensitivityTestCase(TestCase):

    def test_files_classification(self):

        # -----------------------------
        # ملفات (صور + PDF + TXT)
        # -----------------------------
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
        # التصنيفات الحقيقية
        y_true = [
            "HIGH",
            "HIGH",
            "MEDIUM",
            "HIGH",
            "HIGH",
            "HIGH",
            "HIGH",
            "HIGH",
            "HIGH",
            "MEDIUM",
            "MEDIUM",
            "MEDIUM",
            "MEDIUM",
            "MEDIUM",
            "LOW",
            "LOW",
            "LOW",
            
        ]

        # -----------------------------
        # قوائم التوقعات
        # -----------------------------
        y_pred_ml = []
        y_pred_rule = []
        y_pred_hybrid = []

        # -----------------------------
        # OCR للصور
        # -----------------------------
        def extract_text_from_image(image_path):
            image = Image.open(image_path)
            gray = ImageOps.grayscale(image)  # تحويل إلى grayscale
            text = pytesseract.image_to_string(gray, lang="ara+eng")
            return ' '.join(text.split())  # تنظيف النص

        # -----------------------------
        # OCR للـ PDF
        # -----------------------------
        def extract_text_from_pdf(pdf_path):
            text = ""
            images = convert_from_path(pdf_path)
            for img in images:
                gray = ImageOps.grayscale(img)  # تحويل إلى grayscale
                page_text = pytesseract.image_to_string(gray, lang="ara+eng")
                text += page_text + " "
            return ' '.join(text.split())

        # -----------------------------
        # قراءة ملفات TXT
        # -----------------------------
        def extract_text_from_txt(txt_path):
            with open(txt_path, "r", encoding="utf-8") as file:
                text = file.read()
            return ' '.join(text.split())

        # -----------------------------
        # تحديد نوع الملف
        # -----------------------------
        def extract_text(file_path):
            extension = os.path.splitext(file_path)[1].lower()
            if extension == ".pdf":
                return extract_text_from_pdf(file_path)
            elif extension == ".txt":
                return extract_text_from_txt(file_path)
            else:
                return extract_text_from_image(file_path)

        # -----------------------------
        # تحليل كل ملف
        # -----------------------------
        for file_path in test_files:
            text = extract_text(file_path)
            print("Extracted Text:", text)

            # -------- ML --------
            score_ml = ml_score(text)
            if score_ml > 0.6:
                level_ml = "HIGH"
            elif score_ml > 0.3:
                level_ml = "MEDIUM"
            else:
                level_ml = "LOW"
            y_pred_ml.append(level_ml)

            # ----- Rule Based -----
            sensitive, score_rule = is_sensitive(text)
            if score_rule > 0.6:
                level_rule = "HIGH"
            elif score_rule > 0.3:
                level_rule = "MEDIUM"
            else:
                level_rule = "LOW"
            y_pred_rule.append(level_rule)

            # ------- Hybrid -------
            hybrid_result = final_classification(text)
            level_hybrid = hybrid_result["level"].upper()
            y_pred_hybrid.append(level_hybrid)

        # -----------------------------
        # تقرير الدقة
        # -----------------------------
        labels = ["LOW", "MEDIUM", "HIGH"]

        print("\n===== ML Report =====")
        print(classification_report(y_true, y_pred_ml, labels=labels))

        print("\n===== Rule Based Report =====")
        print(classification_report(y_true, y_pred_rule, labels=labels))

        print("\n===== Hybrid Report =====")
        print(classification_report(y_true, y_pred_hybrid, labels=labels))
