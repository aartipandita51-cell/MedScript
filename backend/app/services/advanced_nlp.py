from transformers import pipeline

ner = pipeline("ner", model="d4data/biomedical-ner-all")

def extract_entities_advanced(text):
    results = ner(text)

    symptoms = set()
    medicines = set()

    for r in results:
        word = r["word"].lower()

        if r["entity_group"] in ["DISEASE", "SYMPTOM"]:
            symptoms.add(word)

        if r["entity_group"] == "DRUG":
            medicines.add(word)

    return {
        "symptoms": list(symptoms),
        "medicines": list(medicines)
    }