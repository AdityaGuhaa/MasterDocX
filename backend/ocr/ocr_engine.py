import pytesseract
from PIL import Image
import os
from typing import List
from api.settings import settings


class OCREngine:
    def __init__(self):
        """Initialize OCR engine"""
        # You may need to specify the path to tesseract executable
        # pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'  # Linux
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows
        pass

    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from a single image"""
        try:
            # Open image
            image = Image.open(image_path)

            # Perform OCR
            text = pytesseract.image_to_string(image)

            return text
        except Exception as e:
            raise Exception(f"OCR failed for image {image_path}: {str(e)}")

    def extract_text_from_images(self, image_paths: List[str]) -> str:
        """Extract text from multiple images"""
        full_text = ""
        for image_path in image_paths:
            text = self.extract_text_from_image(image_path)
            full_text += text + "\n\n"
        return full_text

    def extract_text_from_pdf_pages(self, pdf_path: str) -> str:
        """Extract text from PDF pages using OCR"""
        try:
            from pdf2image import convert_from_path

            # Convert PDF to images
            images = convert_from_path(pdf_path)

            # Extract text from each image
            full_text = ""
            for i, image in enumerate(images):
                text = pytesseract.image_to_string(image)
                full_text += f"--- Page {i+1} ---\n{text}\n\n"

            return full_text
        except Exception as e:
            raise Exception(f"OCR failed for PDF {pdf_path}: {str(e)}")