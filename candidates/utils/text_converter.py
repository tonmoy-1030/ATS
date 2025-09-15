from pdf2image import convert_from_path
from pytesseract import image_to_string
import docx2txt
from PyPDF2 import PdfReader
import subprocess

class TextConverter:
    @staticmethod
    def _split_and_filter_lines(text):
        lines = text.split('\n')
        return [line for line in lines if line.strip()]

    @staticmethod
    def pypdf_to_text(path):
        try:
            extracted_text = []
            reader = PdfReader(path)
            for page in reader.pages:
                non_empty_lines = TextConverter._split_and_filter_lines(page.extract_text())
                extracted_text.extend(non_empty_lines)
            return extracted_text
        except Exception as e:
            print(f"PyPDF conversion error: {e}")
            return []

    @staticmethod
    def pdf_to_text(path):
        try:
            extracted_text = []
            images = convert_from_path(path)
            for image in images:
                image_text = image_to_string(image)
                non_empty_lines = TextConverter._split_and_filter_lines(image_text)
                extracted_text.extend(non_empty_lines)
            return extracted_text
        except Exception as e:
            print(f"PDF conversion error: {e}")
            return []

    @staticmethod
    def img_to_text(path):
        try:
            extracted_text = []
            image_text = image_to_string(path)
            non_empty_lines = TextConverter._split_and_filter_lines(image_text)
            extracted_text.extend(non_empty_lines)
            return extracted_text
        except Exception as e:
            print(f"Image conversion error: {e}")
            return []

    @staticmethod
    def docx_to_text(path):
        try:
            text = docx2txt.process(path)
            lines = TextConverter._split_and_filter_lines(text)
            return lines
        except Exception as e:
            print(f"DOCX conversion error: {e}")
            return []

    @staticmethod
    def doc_to_text(doc_file_path):
        try:
            result = subprocess.run(
                ["antiword", doc_file_path],
                capture_output=True,
                text=True,
                check=True
            )
            
            lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
            return lines
        except FileNotFoundError:
            print("Error: 'antiword' command not found. Please ensure it is installed and in your system's PATH.")
            return []
        except subprocess.CalledProcessError as e:
            print(f"Error extracting DOC text: {e}")
            print(f"Antiword stderr: {e.stderr}")
            return []