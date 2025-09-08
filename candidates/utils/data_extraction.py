import os
import phonenumbers
import re

TARGET_STRINGS = ['of', 'Résumé of', 'resume', 'cv', 'curriculum vitae', 'Powered By Bdjobs.Com', 'Page 1-2']


class DataExtraction:
    EMAIL_REGEX = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"

    def __init__(self, email="Not Found", phone="Not Found", name=None, index_target=None):
        self.email = email
        self.phone = phone
        self.name = name
        self.index_target = index_target

    def extract_name(self, text):
        if not isinstance(text, list):
            raise ValueError("Input text must be a list of lines.")
        for i, line in enumerate(text[:5]):
            if any(word.lower() in line.lower() for word in TARGET_STRINGS):
                self.index_target = i
                break  # Stop checking after the first match
        if self.index_target is not None and self.index_target + 1 < len(text):
            self.name = text[self.index_target + 1]
        else:
            self.name = text[0] if text else "Not Found"
        return self.name.title()

    def extract_phonenumbers(self, text):
        if not isinstance(text, list):
            raise ValueError("Input text must be a list of lines.")
        page_text = "\n".join(text)
        numbers = phonenumbers.PhoneNumberMatcher(text=page_text, region="BD")
        for number in numbers:
            self.phone = phonenumbers.format_number(number.number, phonenumbers.PhoneNumberFormat.E164)
            break  # Get the first number and break
        else:
            # Explicitly set "Not Found" if no phone numbers are detected
            self.phone = "Not Found"
        return self.phone


    def extract_emails(self, text):
        if not isinstance(text, list):
            raise ValueError("Input text must be a list of lines.")
        page_text = "\n".join(text)
        emails = re.findall(self.EMAIL_REGEX, page_text)
        self.email = emails[0] if emails else "Not Found"
        return self.email

    @staticmethod
    def extract_file_name(path):
        if isinstance(path, str):
            file_name = os.path.basename(path)
        elif hasattr(path, 'name'):
            file_name = os.path.basename(path.name)
        else:
            raise ValueError("Path must be a string or an object with a 'name' attribute.")
        return file_name
