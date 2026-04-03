import os
from PIL import Image
import pytesseract
from pdf2image import convert_from_path

# إضافة العربي
import arabic_reshaper
from bidi.algorithm import get_display


def extract_text_from_image(image_path):
    """
    OCR للصورة.
    يقرأ النصوص بالعربية والإنجليزية.
    """
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang="ara+eng")

        #  إصلاح اتجاه العربي
        text = arabic_reshaper.reshape(text)
        text = get_display(text)

        return text.strip()
    except Exception as e:
        print(f"OCR Error (Image): {e}")
        return ""


def extract_text_from_pdf(pdf_path):
    """
    OCR للملفات PDF.
    يحول كل صفحة لصورة ثم يقرأ النص.
    """
    try:
        text = ""
        images = convert_from_path(pdf_path)

        for img in images:
            page_text = pytesseract.image_to_string(img, lang="ara+eng")

            # إصلاح اتجاه العربي لكل صفحة
            page_text = arabic_reshaper.reshape(page_text)
            page_text = get_display(page_text)

            text += page_text + "\n"

        return text.strip()
    except Exception as e:
        print(f"OCR Error (PDF): {e}")
        return ""


def extract_text_from_txt(txt_path):
    """
    قراءة ملفات النصوص العادية (.txt)
    """
    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            text = f.read()

            #  حتى النصوص نصلحها (احتياط)
            text = arabic_reshaper.reshape(text)
            text = get_display(text)

            return text.strip()
    except Exception as e:
        print(f"Read TXT Error: {e}")
        return ""


def perform_ocr(file_path):
    """
    تحديد نوع الملف وتشغيل OCR المناسب.
    """
    extension = os.path.splitext(file_path)[1].lower()

    if extension in [".jpg", ".jpeg", ".png"]:
        return extract_text_from_image(file_path)

    elif extension == ".pdf":
        return extract_text_from_pdf(file_path)

    elif extension == ".txt":
        return extract_text_from_txt(file_path)

    else:
        print(f"Unsupported file type: {extension}")
        return ""
