import difflib
import re

MEDICAL_TERMS = [
    "fever", "headache", "cough", "cold", "pain",
    "weakness", "fatigue", "infection", "throat",
    "paracetamol", "ibuprofen", "aspirin",
    "azithromycin", "amoxicillin", "dolo", "crocin"
]

COMMON_WORDS = {
    "i", "have", "been", "for", "the", "and", "is", "are",
    "a", "an", "to", "of", "in", "on", "with", "that",
    "this", "it", "very", "more", "less", "should",
    "can", "you", "doctor", "okay"
}


def correct_word(word):
    # skip short or common words
    if word in COMMON_WORDS or len(word) <= 3:
        return word

    matches = difflib.get_close_matches(word, MEDICAL_TERMS, n=1, cutoff=0.85)
    return matches[0] if matches else word


def correct_medical_text(text: str):
    # ✅ preserve punctuation
    tokens = re.findall(r"\w+|[.,!?]", text)

    corrected_tokens = []

    for token in tokens:
        if re.match(r"\w+", token):  # word
            corrected = correct_word(token.lower())
            corrected_tokens.append(corrected)
        else:
            corrected_tokens.append(token)  # punctuation

    # ✅ rebuild sentence properly
    sentence = " ".join(corrected_tokens)

    # fix spacing before punctuation
    sentence = re.sub(r"\s+([.,!?])", r"\1", sentence)

    # capitalize first letter
    sentence = sentence.capitalize()

    return sentence