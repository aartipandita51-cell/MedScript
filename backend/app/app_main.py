from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import shutil
import os
import json

from database import SessionLocal, engine
from models import Consultation, Base

from services.transcription import transcribe_audio
from services.translation import translate_to_english
from services.text_correction import correct_medical_text
from services.summarization import generate_summary
from services.nlp import extract_medical_entities
from services.entity_extraction import extract_entities_advanced
from services.report_generator import generate_report

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# -------------------------------
# DB Setup
# -------------------------------
Base.metadata.create_all(bind=engine)

app = FastAPI()

# -------------------------------
# CORS
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Upload folder
# -------------------------------
UPLOAD_FOLDER = "temp_audio"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.get("/")
def home():
    return {"message": "MedScript API is running"}


# -------------------------------
# AUDIO PROCESSING PIPELINE
# -------------------------------
@app.post("/process-audio")
async def process_audio(
    file: UploadFile = File(...),
    language: str = Form("en")
):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 1. Transcription
    raw_text = transcribe_audio(file_path, language)

    # 2. Translation
    translated_text = translate_to_english(raw_text) if language == "hi" else raw_text

    # 3. Correction
    corrected_text = correct_medical_text(translated_text)

    # 4. Entity extraction (safe)
    try:
        basic_entities = extract_medical_entities(corrected_text)
    except Exception:
        basic_entities = {"symptoms": [], "medicines": []}

    try:
        advanced_entities = extract_entities_advanced(corrected_text)
    except Exception:
        advanced_entities = {"symptoms": [], "medicines": [], "advice": []}

    # 5. Merge entities
    entities = {
        "symptoms": list(set(
            basic_entities.get("symptoms", []) +
            advanced_entities.get("symptoms", [])
        )),
        "medicines": list(set(
            basic_entities.get("medicines", []) +
            advanced_entities.get("medicines", [])
        )),
        "advice": advanced_entities.get("advice", [])
    }

    # 6. Generate structured report
    report_dict = generate_report(corrected_text, entities)

    # 🔥 CRITICAL FIX: ensure dict (NOT string)
    if isinstance(report_dict, str):
        try:
            report_dict = json.loads(report_dict)
        except:
            report_dict = {}

    # 🔒 Ensure structure
    report_dict = {
        "subjective": report_dict.get("subjective", []),
        "objective": report_dict.get("objective", []),
        "assessment": report_dict.get("assessment", "No clear diagnosis"),
        "plan": {
            "medicines": report_dict.get("plan", {}).get("medicines", entities["medicines"]),
            "advice": report_dict.get("plan", {}).get("advice", entities["advice"])
        }
    }

    # 7. Summary
    summary = generate_summary(corrected_text)

    # 8. Save to DB
    db = SessionLocal()
    consultation = Consultation(
        raw_transcript=raw_text,
        corrected_transcript=corrected_text,
        symptoms=", ".join(entities["symptoms"]),
        medicines=", ".join(entities["medicines"]),
        report=json.dumps(report_dict)  # ALWAYS save JSON string
    )
    db.add(consultation)
    db.commit()
    db.refresh(consultation)
    db.close()

    # 9. Response
    return {
        "id": consultation.id,
        "raw_transcript": raw_text,
        "corrected_transcript": corrected_text,
        "summary": summary,
        "entities": entities,
        "report": report_dict
    }


# -------------------------------
# HISTORY API (FIXED)
# -------------------------------
@app.get("/history")
def get_history():
    db = SessionLocal()
    records = db.query(Consultation).all()
    db.close()

    response = []

    for r in records:
        # 🔥 HANDLE OLD + NEW DATA
        try:
            report = json.loads(r.report) if isinstance(r.report, str) else r.report
        except:
            report = {}

        response.append({
            "id": r.id,
            "corrected_transcript": r.corrected_transcript,

            "symptoms": r.symptoms.split(",") if r.symptoms else [],
            "medicines": r.medicines.split(",") if r.medicines else [],

            "entities": {
                "symptoms": r.symptoms.split(",") if r.symptoms else [],
                "medicines": r.medicines.split(",") if r.medicines else [],
                "advice": report.get("plan", {}).get("advice", [])
            },

            "summary": r.corrected_transcript[:150] + "...",
            "report": report
        })

    return response


# -------------------------------
# PDF DOWNLOAD
# -------------------------------
@app.get("/download-report/{report_id}")
def download_report(report_id: int):
    db = SessionLocal()
    record = db.query(Consultation).filter(Consultation.id == report_id).first()
    db.close()

    if not record:
        return {"error": "Report not found"}

    try:
        report = json.loads(record.report)
    except:
        report = {}

    file_path = f"report_{report_id}.pdf"

    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()
    content = []

    # Title
    content.append(Paragraph("Medical Consultation Report", styles["Title"]))
    content.append(Spacer(1, 15))

    # Subjective
    content.append(Paragraph("Subjective:", styles["Heading2"]))
    for item in report.get("subjective", []):
        content.append(Paragraph(f"• {item}", styles["Normal"]))

    content.append(Spacer(1, 10))

    # Objective
    content.append(Paragraph("Objective:", styles["Heading2"]))
    for item in report.get("objective", []):
        content.append(Paragraph(f"• {item}", styles["Normal"]))

    content.append(Spacer(1, 10))

    # Assessment
    content.append(Paragraph("Assessment:", styles["Heading2"]))
    content.append(Paragraph(report.get("assessment", "N/A"), styles["Normal"]))

    content.append(Spacer(1, 10))

    # Plan
    content.append(Paragraph("Plan:", styles["Heading2"]))

    content.append(Paragraph("Medicines:", styles["Heading3"]))
    for med in report.get("plan", {}).get("medicines", []):
        content.append(Paragraph(f"• {med}", styles["Normal"]))

    content.append(Spacer(1, 8))

    content.append(Paragraph("Advice:", styles["Heading3"]))
    for adv in report.get("plan", {}).get("advice", []):
        content.append(Paragraph(f"• {adv}", styles["Normal"]))

    doc.build(content)

    return FileResponse(file_path, media_type='application/pdf', filename=file_path)