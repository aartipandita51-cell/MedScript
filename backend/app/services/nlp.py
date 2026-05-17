import re

SYMPTOMS = [
    "fever", "cough", "cold", "headache",
    "throat pain", "weakness", "fatigue", "body pain"
]

MEDICINES = [
    "paracetamol", "ibuprofen", "azithromycin",
    "amoxicillin", "cough syrup", "dolo", "crocin"
]

def extract_medical_entities(text):
    text = text.lower()
    sentences = re.split(r"[.]", text)

    symptoms = set()
    medicines = []
    advice = []
    diagnosis = []

    for sentence in sentences:
        sentence = sentence.strip()

        # ✅ Symptoms
        if any(p in sentence for p in ["i have", "i feel", "suffering"]):
            for s in SYMPTOMS:
                if s in sentence:
                    symptoms.add(s)

        # ✅ Medicines with dosage
        for med in MEDICINES:
            if med in sentence:
                dose = re.search(rf"{med}.*?(mg|ml)?.*?(once|twice|daily)", sentence)
                medicines.append(dose.group(0) if dose else med)

        # ✅ Advice
        if any(p in sentence for p in ["drink", "rest", "avoid", "sleep"]):
            advice.append(sentence)

        # ✅ Diagnosis
        if any(p in sentence for p in ["viral", "infection", "flu"]):
            diagnosis.append(sentence)

    return {
        "symptoms": list(symptoms),
        "medicines": medicines,
        "advice": advice,
        "diagnosis": diagnosis
    }