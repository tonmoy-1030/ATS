import locale

# Set the locale for India
locale.setlocale(locale.LC_ALL, 'en_IN')

def format_number(num):
    return locale.format_string("%d", num, grouping=True)



def convert_to_words(num):
    if num == 0:
        return "zero"

    ones = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
    teens = ["ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]

    def _convert_hundreds(n):
        words = ""
        if n >= 100:
            words += ones[n // 100] + " hundred "
            n %= 100
        if n >= 10 and n <= 19:
            words += teens[n - 10] + " "
            n = 0
        elif n >= 20:
            words += tens[n // 10] + " "
            n %= 10
        if n >= 1 and n <= 9:
            words += ones[n] + " "
        return words.strip()

    words = ""
    if num >= 10000000:
        words += _convert_hundreds(num // 10000000) + " crore "
        num %= 10000000
    if num >= 100000:
        words += _convert_hundreds(num // 100000) + " lakh "
        num %= 100000
    if num >= 1000:
        words += _convert_hundreds(num // 1000) + " thousand "
        num %= 1000
    if num > 0:
        words += _convert_hundreds(num)

    return words.strip().title()

