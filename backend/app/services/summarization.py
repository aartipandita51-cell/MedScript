from transformers import pipeline

# Use text2text-generation instead of summarization (Transformers v5 fix)
summarizer = pipeline("text2text-generation", model="google/flan-t5-small")
def generate_summary(text: str) -> str:
    if not text or len(text.strip()) == 0:
        return ""

    prompt = f"Summarize the following medical transcription:\n{text}"

    result = summarizer(prompt, max_length=150, min_length=40, do_sample=False)

    return result[0]['generated_text']