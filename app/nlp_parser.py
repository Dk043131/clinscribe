"""
Clinical NLP Parsing Engine
Transforms conversational doctor-patient clinical dialogues into structured SOAP notes.
"""

import re
from typing import Dict, Any, List

class ClinicalSOAPParser:
    def __init__(self):
        self.vitals_pattern = re.compile(
            r'(?:bp|blood pressure)[:\s]+(\d{2,3}/\d{2,3})|'
            r'(?:hr|pulse|heart rate)[:\s]+(\d{2,3})|'
            r'(?:temp|temperature)[:\s]+(\d{2,3}(?:\.\d)?)|'
            r'(?:spo2|o2 sat)[:\s]+(\d{2,3})%?',
            re.IGNORECASE
        )

    def parse_dialogue(self, transcript: str) -> Dict[str, Any]:
        """
        Parses raw consultation transcript into Subjective, Objective, Assessment, and Plan (SOAP).
        """
        lines = [l.strip() for l in transcript.split('\n') if l.strip()]
        
        subjective_notes = []
        objective_notes = []
        assessment_notes = []
        plan_notes = []
        vitals_detected = {}

        for line in lines:
            lower = line.lower()
            
            # Check for vitals
            v_match = self.vitals_pattern.search(line)
            if v_match:
                if v_match.group(1): vitals_detected['blood_pressure'] = v_match.group(1)
                if v_match.group(2): vitals_detected['heart_rate'] = f"{v_match.group(2)} bpm"
                if v_match.group(3): vitals_detected['temperature'] = f"{v_match.group(3)} °F"
                if v_match.group(4): vitals_detected['spo2'] = f"{v_match.group(4)}%"
                objective_notes.append(line)
                continue

            # Section Heuristics
            if any(k in lower for k in ['complain', 'pain', 'hurts', 'felt', 'states', 'headache', 'fever', 'nausea', 'sore']):
                subjective_notes.append(line)
            elif any(k in lower for k in ['exam', 'lungs', 'clear', 'throat', 'erythema', 'normal', 'sound', 'labs', 'tested']):
                objective_notes.append(line)
            elif any(k in lower for k in ['diagnos', 'likely', 'secondary to', 'impression', 'acute', 'chronic', 'syndrome']):
                assessment_notes.append(line)
            elif any(k in lower for k in ['prescrib', 'take', 'mg', 'daily', 'follow up', 'return', 'order', 'refer', 'advised']):
                plan_notes.append(line)
            else:
                subjective_notes.append(line)

        return {
            "subjective": "\n".join(subjective_notes) or "Patient presents for routine follow-up.",
            "objective": {
                "vitals": vitals_detected,
                "physical_exam": "\n".join(objective_notes) or "General appearance: Alert and oriented x3."
            },
            "assessment": "\n".join(assessment_notes) or "Clinical presentation consistent with primary complaint.",
            "plan": "\n".join(plan_notes) or "Supportive care and follow-up as indicated."
        }
