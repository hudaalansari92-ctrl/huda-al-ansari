import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_AR = """أنت طبيب قلب متخصص. مهمتك شرح نتائج تقييم خطر أمراض القلب للمريض بلغة بسيطة ومفهومة.

القواعد:
- اشرح ما تعنيه الأرقام والنتائج بلغة بسيطة
- لا تشخص المريض — أنت تشرح فقط ما تعنيه البيانات
- استخدم لغة مطمئنة لكن صادقة
- اذكر عوامل الخطر الموجودة بوضوح
- اقترح الخطوة التالية (مراجعة طبيب، فحوصات إضافية، إلخ)
- الرد يجب أن يكون بالعربية
- الرد يجب أن يكون مختصراً (3-5 جمل)
- لا تستخدم مصطلحات طبية معقدة"""

SYSTEM_PROMPT_EN = """You are a specialized cardiologist. Your task is to explain heart disease risk assessment results to the patient in simple, understandable language.

Rules:
- Explain what the numbers and results mean in simple language
- Do NOT diagnose the patient — only explain what the data indicates
- Use reassuring but honest language
- Clearly mention existing risk factors
- Suggest next steps (see a doctor, additional tests, etc.)
- Response must be in English
- Keep it concise (3-5 sentences)
- Avoid complex medical terminology"""


class ResultInterpreter:
    """Interprets medical assessment results using Groq LLM"""

    def __init__(self, groq_client):
        self.groq_client = groq_client

    def interpret(self, assessment: Dict, facts: Dict, language: str = 'ar') -> Optional[str]:
        """
        Generate a simple interpretation of the assessment results

        Args:
            assessment: Final assessment dict from decision engine
            facts: Patient facts (age, bp, cholesterol, etc.)
            language: 'ar' or 'en'

        Returns:
            Simple text explanation or None if Groq unavailable
        """
        if not self.groq_client or not self.groq_client.is_available:
            return None

        system_prompt = SYSTEM_PROMPT_AR if language == 'ar' else SYSTEM_PROMPT_EN

        user_message = self._build_message(assessment, facts, language)

        result = self.groq_client.chat(
            system_prompt=system_prompt,
            user_message=user_message,
            temperature=0.3,
            max_tokens=500
        )

        return result

    def _build_message(self, assessment: Dict, facts: Dict, language: str) -> str:
        """Build the data message to send to Groq"""
        risk_level = assessment.get('final_risk_level', 'UNKNOWN')
        confidence = assessment.get('confidence', 0)
        reasoning = assessment.get('reasoning_ar' if language == 'ar' else 'reasoning_en', '')

        sources = assessment.get('sources', {})
        ml_prob = sources.get('ml_model', {}).get('probability', 0)
        domain_risk = sources.get('domain_rules', {}).get('risk_level', 'UNKNOWN')

        facts_summary = []
        field_labels = {
            'Age': ('العمر', 'Age'),
            'Sex': ('الجنس', 'Sex'),
            'ChestPain': ('ألم الصدر', 'Chest Pain'),
            'BloodPressure': ('ضغط الدم', 'Blood Pressure'),
            'Cholesterol': ('الكوليسترول', 'Cholesterol'),
            'FastingBS': ('سكر الدم', 'Fasting Blood Sugar'),
            'RestingECG': ('تخطيط القلب', 'Resting ECG'),
            'MaxHR': ('أقصى نبض', 'Max Heart Rate'),
            'ExerciseAngina': ('ألم مع المجهود', 'Exercise Angina'),
            'Oldpeak': ('انخفاض ST', 'ST Depression'),
            'ST_Slope': ('منحنى ST', 'ST Slope')
        }

        idx = 0 if language == 'ar' else 1
        for field, value in facts.items():
            if value is not None and field in field_labels:
                label = field_labels[field][idx]
                facts_summary.append(f"- {label}: {value}")

        facts_text = "\n".join(facts_summary) if facts_summary else "No data available"

        if language == 'ar':
            return f"""بيانات المريض:
{facts_text}

نتيجة التقييم:
- مستوى الخطر: {risk_level}
- درجة الثقة: {confidence:.0%}
- احتمالية ML: {ml_prob:.0%}
- تقييم القواعد الطبية: {domain_risk}
- السبب: {reasoning}

اشرح هذه النتائج للمريض بلغة بسيطة."""
        else:
            return f"""Patient Data:
{facts_text}

Assessment Result:
- Risk Level: {risk_level}
- Confidence: {confidence:.0%}
- ML Probability: {ml_prob:.0%}
- Domain Rules Assessment: {domain_risk}
- Reasoning: {reasoning}

Explain these results to the patient in simple language."""
