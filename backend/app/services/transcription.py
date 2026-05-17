import whisper

model = whisper.load_model("small")  # 🔥 upgrade model

def transcribe_audio(file_path: str, language: str = "en"):
    if language == "hi":
        # ✅ Direct Hindi speech → English text
        result = model.transcribe(file_path, task="translate")
    else:
        result = model.transcribe(file_path)

    return result["text"]