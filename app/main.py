"""
ClinScribe - Clinical SOAP Documentation & FHIR Generator API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from app.nlp_parser import ClinicalSOAPParser
from app.fhir_converter import FHIRBundleConverter

app = FastAPI(
    title="ClinScribe API",
    description="Automated Clinical SOAP Note Generation and HL7 FHIR Standard Resource Mapping",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

parser = ClinicalSOAPParser()

class ConsultationRequest(BaseModel):
    patient_id: Optional[str] = Field(default="PT-90412", description="Unique Patient Identifier")
    transcript: str = Field(..., description="Raw doctor-patient consultation dialogue transcript")

class SOAPResponse(BaseModel):
    patient_id: str
    soap: Dict[str, Any]
    fhir_bundle: Dict[str, Any]

@app.get("/")
def root():
    return {
        "service": "ClinScribe Clinical Documentation Engine",
        "status": "healthy",
        "fhir_version": "HL7 FHIR R4",
        "endpoints": ["/api/v1/generate-soap", "/api/v1/fhir-bundle", "/health"]
    }

@app.post("/api/v1/generate-soap", response_model=SOAPResponse)
def generate_soap_documentation(req: ConsultationRequest):
    if not req.transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript content cannot be empty.")
    
    soap_data = parser.parse_dialogue(req.transcript)
    bundle = FHIRBundleConverter.create_bundle(req.patient_id, soap_data)

    return {
        "patient_id": req.patient_id,
        "soap": soap_data,
        "fhir_bundle": bundle
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}
