"""
Groq-Powered Smart NER — استخراج ذكي للبيانات الطبية
Extracts multiple medical fields from free-form patient text using Groq LLM.
Falls back gracefully if Groq is unavailable.
"""

import json
import re
import logging
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

# الحقول الطبية الـ 11 مع أنواعها ونطاقاتها
FIELD_SCHEMA = {
    "Age": {"type": "int", "min": 1, "max": 120},
    "Sex": {"type": "choice", "values": ["Male", "Female"]},
    "ChestPain": {"type": "choice", "values": ["TA", "ATA", "NAP", "ASY"]},
    "BloodPressure": {"type": "pattern", "pattern": r"^\d{2,3}/\d{2,3}$"},
    "Cholesterol": {"type": "int", "min": 50, "max": 600},
    "FastingBS": {"type": "choice", "values": [0, 1]},
    "RestingECG": {"type": "choice", "values": ["Normal", "ST", "LVH"]},
    "MaxHR": {"type": "int", "min": 60, "max": 220},
    "ExerciseAngina": {"type": "choice", "values": ["Y", "N"]},
    "Oldpeak": {"type": "float", "min": 0.0, "max": 10.0},
    "ST_Slope": {"type": "choice", "values": ["Up", "Flat", "Down"]},
}

SYSTEM_PROMPT = """You are a medical data extraction system. Extract structured medical fields from patient text.
The patient may write in Arabic or English. Extract ALL fields you can identify.

Fields to extract (use EXACTLY these names and value formats):

1. Age: integer (1-120)
   - Arabic examples: "عمري 45", "عندي 55 سنة"
   - English: "I am 45 years old", "age 55"

2. Sex: MUST be exactly "Male" or "Female"
   - Arabic: "ذكر" → "Male", "أنثى" → "Female", "رجل" → "Male", "امرأة" → "Female"

3. ChestPain: MUST be one of: "TA", "ATA", "NAP", "ASY"
   - TA = Typical Angina (ألم صدر نموذجي، ذبحة صدرية نموذجية)
   - ATA = Atypical Angina (ألم صدر غير نموذجي)
   - NAP = Non-Anginal Pain (ألم غير ذبحي)
   - ASY = Asymptomatic (بدون أعراض)
   - "عندي ألم بالصدر" without details → "ATA"
   - "ما عندي ألم" / "no chest pain" → "ASY"
   - "ألم شديد عند المجهود" → "TA"

4. BloodPressure: format "systolic/diastolic" (e.g., "140/90")
   - "ضغطي 150 على 90" → "150/90"
   - "blood pressure 130/85" → "130/85"

5. Cholesterol: integer mg/dL (50-600)
   - "الكوليسترول 250" → 250

6. FastingBS: 0 or 1
   - 0 = Normal (سكر طبيعي, ≤120 mg/dL)
   - 1 = High (سكر مرتفع, >120 mg/dL)
   - "عندي سكر" / "مريض سكر" → 1
   - "السكر طبيعي" → 0

7. RestingECG: MUST be one of: "Normal", "ST", "LVH"
   - Normal = تخطيط طبيعي
   - ST = شذوذ ST-T
   - LVH = تضخم البطين الأيسر

8. MaxHR: integer (60-220) — Maximum heart rate achieved
   - "أقصى نبض 155" → 155

9. ExerciseAngina: MUST be "Y" or "N"
   - "ألم مع المشي/الرياضة/المجهود" → "Y"
   - "ما يجيني ألم مع الرياضة" → "N"

10. Oldpeak: float (0.0-10.0) — ST depression value
    - "انخفاض ST بمقدار 1.5" → 1.5

11. ST_Slope: MUST be one of: "Up", "Flat", "Down"
    - Up = صاعد, Flat = مسطح, Down = نازل

CRITICAL RULES:
- Return ONLY a valid JSON object. No extra text, no markdown.
- Only include fields you are CONFIDENT about from the text.
- Do NOT guess or assume values not mentioned.
- Use the EXACT field names and value formats shown above.

Example input: "أنا رجل عمري 55 سنة وعندي ضغط 150/90 وألم بالصدر"
Example output: {"Age": 55, "Sex": "Male", "BloodPressure": "150/90", "ChestPain": "ATA"}"""


class GroqNER:
    """
    Smart NER using Groq LLM — extracts medical fields from free-form text.
    Falls back to empty dict if Groq is unavailable.
    """

    def __init__(self, groq_client):
        self.groq_client = groq_client

    def extract(self, text: str) -> Dict[str, Any]:
        """
        Extract medical fields from free-form patient text.

        Args:
            text: Patient's free-form message (Arabic or English)

        Returns:
            Dict of validated extracted fields. Empty dict if extraction fails.
            Example: {"Age": 45, "BloodPressure": "150/90", "ChestPain": "ATA"}
        """
        if not text or not text.strip():
            return {}

        if not self.groq_client or not self.groq_client.is_available:
            logger.warning("Groq not available for Smart NER")
            return {}

        try:
            response = self.groq_client.chat(
                system_prompt=SYSTEM_PROMPT,
                user_message=text.strip(),
                temperature=0.1,
                max_tokens=300
            )

            if not response:
                logger.warning("Empty response from Groq NER")
                return {}

            parsed = self._parse_response(response)
            validated = self._validate_fields(parsed)

            logger.info(f"Smart NER extracted {len(validated)} fields from: '{text[:50]}...'")
            return validated

        except Exception as e:
            logger.error(f"Smart NER extraction failed: {e}")
            return {}

    def _parse_response(self, response: str) -> Dict:
        """Parse JSON from Groq response, handle malformed JSON."""
        response = response.strip()

        # Try direct JSON parse
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # Try extracting JSON from markdown code block
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try extracting any JSON object
        json_match = re.search(r'\{[^{}]*\}', response)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        logger.warning(f"Could not parse Groq NER response: {response[:100]}")
        return {}

    def _validate_fields(self, extracted: Dict) -> Dict:
        """Validate each extracted field against known schema."""
        validated = {}

        for field, value in extracted.items():
            if field not in FIELD_SCHEMA:
                logger.debug(f"Ignoring unknown field: {field}")
                continue

            schema = FIELD_SCHEMA[field]
            validated_value = self._validate_single_field(field, value, schema)

            if validated_value is not None:
                validated[field] = validated_value
            else:
                logger.debug(f"Validation failed for {field}={value}")

        return validated

    def _validate_single_field(self, field: str, value: Any, schema: Dict) -> Optional[Any]:
        """Validate a single field value against its schema."""
        field_type = schema["type"]

        if field_type == "int":
            try:
                val = int(float(str(value)))
                if schema["min"] <= val <= schema["max"]:
                    return val
            except (ValueError, TypeError):
                pass
            return None

        elif field_type == "float":
            try:
                val = round(float(str(value)), 1)
                if schema["min"] <= val <= schema["max"]:
                    return val
            except (ValueError, TypeError):
                pass
            return None

        elif field_type == "choice":
            # Handle both string and numeric choices
            valid_values = schema["values"]
            # Try exact match
            if value in valid_values:
                return value
            # Try string conversion
            str_val = str(value).strip()
            for v in valid_values:
                if str(v).lower() == str_val.lower():
                    return v
            return None

        elif field_type == "pattern":
            str_val = str(value).strip()
            if re.match(schema["pattern"], str_val):
                # Additional BP validation
                if field == "BloodPressure":
                    parts = str_val.split("/")
                    sys_val = int(parts[0])
                    dia_val = int(parts[1])
                    if 60 <= sys_val <= 250 and 30 <= dia_val <= 150:
                        return str_val
                    return None
                return str_val
            return None

        return None
