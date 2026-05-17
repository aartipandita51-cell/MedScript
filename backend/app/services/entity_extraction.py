import re

def extract_entities_advanced(text: str):
    medicines = re.findall(r'\b(?:paracetamol|ibuprofen|aspirin)\b', text.lower())
    symptoms = re.findall(r'\b(?:fever|cough|pain|headache)\b', text.lower())

    return {
        "medicines": list(set(medicines)),
        "symptoms": list(set(symptoms))
    }