from sqlalchemy import Column, Integer, String, Text
from database import Base

class Consultation(Base):
    __tablename__ = "consultations"

    id = Column(Integer, primary_key=True, index=True)
    raw_transcript = Column(Text)
    corrected_transcript = Column(Text)
    symptoms = Column(String)
    medicines = Column(String)
    report = Column(Text)