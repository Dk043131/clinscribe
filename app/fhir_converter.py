"""
HL7 FHIR (Fast Healthcare Interoperability Resources) R4 Bundle Generator.
Converts structured clinical SOAP records into compliant FHIR JSON resources.
"""

import uuid
from datetime import datetime
from typing import Dict, Any

class FHIRBundleConverter:
    @staticmethod
    def create_bundle(patient_id: str, soap_data: Dict[str, Any]) -> Dict[str, Any]:
        bundle_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        entries = []

        # 1. Patient Resource
        entries.append({
            "fullUrl": f"urn:uuid:{patient_id}",
            "resource": {
                "resourceType": "Patient",
                "id": patient_id,
                "active": True
            }
        })

        # 2. Encounter Resource
        encounter_id = str(uuid.uuid4())
        entries.append({
            "fullUrl": f"urn:uuid:{encounter_id}",
            "resource": {
                "resourceType": "Encounter",
                "id": encounter_id,
                "status": "finished",
                "class": {
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                    "code": "AMB",
                    "display": "ambulatory"
                },
                "subject": { "reference": f"urn:uuid:{patient_id}" },
                "period": { "start": timestamp }
            }
        })

        # 3. Observations (Vitals)
        vitals = soap_data.get("objective", {}).get("vitals", {})
        for vital_name, vital_val in vitals.items():
            obs_id = str(uuid.uuid4())
            entries.append({
                "fullUrl": f"urn:uuid:{obs_id}",
                "resource": {
                    "resourceType": "Observation",
                    "id": obs_id,
                    "status": "final",
                    "code": {
                        "text": vital_name.replace("_", " ").title()
                    },
                    "subject": { "reference": f"urn:uuid:{patient_id}" },
                    "valueString": str(vital_val),
                    "effectiveDateTime": timestamp
                }
            })

        # 4. Condition / Assessment
        condition_id = str(uuid.uuid4())
        entries.append({
            "fullUrl": f"urn:uuid:{condition_id}",
            "resource": {
                "resourceType": "Condition",
                "id": condition_id,
                "clinicalStatus": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                        "code": "active"
                    }]
                },
                "verificationStatus": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                        "code": "confirmed"
                    }]
                },
                "subject": { "reference": f"urn:uuid:{patient_id}" },
                "note": [{ "text": soap_data.get("assessment", "") }]
            }
        })

        return {
            "resourceType": "Bundle",
            "id": bundle_id,
            "type": "transaction",
            "timestamp": timestamp,
            "entry": entries
        }
