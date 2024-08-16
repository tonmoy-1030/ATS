from pdf2image import convert_from_path
from pytesseract import image_to_string
import docx2txt
from PyPDF2 import PdfReader
import os
import win32com.client



class TextConverter:
    @staticmethod
    def _split_and_filter_lines(text):
        lines = text.split('\n')
        return [line for line in lines if line.strip()]

    @staticmethod
    def pypdf_to_text(self, path):
        extracted_text = []
        reader = PdfReader(path)
        for page in reader.pages:
            print(page.extract_text())
            non_empty_lines = TextConverter._split_and_filter_lines(page.extract_text())
            extracted_text.extend(non_empty_lines)
        return extracted_text

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
            print(f"PDF conversion error: {e}")
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
            # Generate the output DOCX file path
            docx_file_path = os.path.splitext(doc_file_path)[0] + '_converted.docx'
            print(docx_file_path)
        
            print(os.path.abspath(doc_file_path))
            # Convert DOC to DOCX
            word = win32com.client.Dispatch('Word.Application')
            doc = word.Documents.Open(os.path.abspath(doc_file_path))
            doc.SaveAs(os.path.abspath(docx_file_path), FileFormat=16)  # 16 corresponds to the DOCX format
            doc.Close()
            word.Quit()
            

            # # Check if the DOCX file was created
            # if not os.path.exists(docx_file_path):
            #     raise RuntimeError("Failed to create DOCX file")

            # Extract text from DOCX
            text = docx2txt.process(os.path.abspath(docx_file_path))
            lines = TextConverter._split_and_filter_lines(text)

            # Remove the temporary DOCX file
            # os.remove(docx_file_path)

            return lines

        except Exception as e:
            return f"Error during conversion: {str(e)}"
