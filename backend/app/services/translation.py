from deep_translator import GoogleTranslator

def translate_to_english(text: str):
    return GoogleTranslator(source='auto', target='en').translate(text)