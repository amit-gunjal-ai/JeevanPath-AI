import re
from deep_translator import GoogleTranslator

DEVANAGARI_PATTERN = re.compile(r'[\u0900-\u097F]')


def contains_devanagari(text):
    return bool(DEVANAGARI_PATTERN.search(text))


def translate_to_english(text):
    if not contains_devanagari(text):
        return text

    try:
        return GoogleTranslator(source="auto", target="en").translate(text)
    except Exception as e:
        print(f"Translation failed, using original text as fallback: {e}")
        return text