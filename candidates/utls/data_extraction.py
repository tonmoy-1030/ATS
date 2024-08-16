import os.path
import phonenumbers
import re

TARGET_STRINGS = ['of', 'Résumé of','resume', 'cv', 'curriculum vitae', 'Powered By Bdjobs.Com', 'Page 1-2']


class DataExtraction:
    EMAIL_REGEX = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"

    def __init__(self, email="Not Found", phone="Not Found", name=None, index_target=None):
        self.email = email
        self.phone = phone
        self.name = name
        self.index_target = index_target

    def extract_name(self, text):
        for i, line in enumerate(text[:5]):
            if any(word.lower() in line.lower() for word in TARGET_STRINGS):
                self.index_target = i
        if self.index_target is not None:
            self.name = text[self.index_target + 1]
        else:
            self.name = text[0]
        return self.name.title()

    def extract_phonenumbers(self, text):
        page_text = "\n".join(text)
        numbers = phonenumbers.PhoneNumberMatcher(text=page_text, region="BD")
        for number in numbers:
            self.phone = phonenumbers.format_number(number.number, phonenumbers.PhoneNumberFormat.E164)
            break  # Get the first number and break
        return self.phone

    def extract_emails(self, text):
        page_text = "\n".join(text)  # No need to join lines
        emails = re.findall(self.EMAIL_REGEX, page_text)
        if emails:
            self.email = emails[0]
        return self.email

    @staticmethod
    def extract_file_name(path):
        file_name = path.name
        _, tail = os.path.split(file_name)
        return tail
