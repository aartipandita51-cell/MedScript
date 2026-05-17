from transformers import pipeline
import re

generator = pipeline("text2text-generation", model="google/flan-t5-small")


def generate_report(text, entities):
    prompt = f"""
You are a medical assistant.

Convert the following conversation into a STRICT SOAP format.

Rules:
- Always include all sections
- Always use bullet points (-)
- Do NOT skip any section
- Do NOT add extra text outside format

Text:
{text}

Format:

Subjective:
- ...

Objective:
- ...

Assessment:
...

Plan:
Medicines:
- ...

Advice:
- ...

Symptoms: {entities.get("symptoms", [])}
Medicines: {entities.get("medicines", [])}
"""

    output = generator(prompt, max_length=512, do_sample=False)[0]["generated_text"]

    # ---------- Parsing ----------
    def extract_section(text, start, end=None):
        try:
            if end:
                pattern = rf"{start}\s*:([\s\S]*?){end}\s*:"
            else:
                pattern = rf"{start}\s*:([\s\S]*)"

            match = re.search(pattern, text, re.IGNORECASE)
            return match.group(1).strip() if match else ""
        except:
            return ""

    def extract_list(section_text):
        return [
            line.replace("-", "").strip()
            for line in section_text.split("\n")
            if line.strip().startswith("-")
        ]

    subjective_text = extract_section(output, "Subjective", "Objective")
    objective_text = extract_section(output, "Objective", "Assessment")
    assessment_text = extract_section(output, "Assessment", "Plan")
    plan_text = extract_section(output, "Plan")

    medicines_text = extract_section(plan_text, "Medicines", "Advice")
    advice_text = extract_section(plan_text, "Advice")

    report = {
        "subjective": extract_list(subjective_text) or entities.get("symptoms", []) or [text[:100]],
        "objective": extract_list(objective_text) or ["No measurable clinical signs reported"],
        "assessment": assessment_text.strip() if len(assessment_text) > 10 else "Likely mild or viral condition",
        "plan": {
            "medicines": extract_list(medicines_text) or entities.get("medicines", []),
            "advice": extract_list(advice_text) or [
                "Take adequate rest",
                "Stay hydrated",
                "Consult doctor if symptoms persist"
            ]
        }
    }

    return report