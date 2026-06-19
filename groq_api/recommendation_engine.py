import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_AR = """أنت طبيب قلب متخصص. مهمتك تقديم توصيات مخصصة لكل مريض بناءً على بياناته الشخصية وعوامل الخطر لديه.

القواعد:
- قدم 4-6 توصيات محددة وعملية
- كن محدداً: بدل "اهتم بنظامك الغذائي" → "قلل الملح إلى أقل من 5 غرام يومياً"
- راعِ عوامل الخطر المحددة لهذا المريض
- رتب التوصيات حسب الأهمية (الأهم أولاً)
- لا تشخص — فقط قدم نصائح وقائية
- الرد بالعربية
- كل توصية في سطر منفصل تبدأ بـ •
- لا تستخدم إيموجي"""

SYSTEM_PROMPT_EN = """You are a specialized cardiologist. Your task is to provide personalized recommendations for each patient based on their personal data and risk factors.

Rules:
- Provide 4-6 specific, actionable recommendations
- Be specific: instead of "eat healthy" → "reduce sodium intake to less than 5g per day"
- Consider this patient's specific risk factors
- Order recommendations by importance (most important first)
- Do NOT diagnose — only provide preventive advice
- Response in English
- Each recommendation on a separate line starting with •
- Do not use emoji"""


class RecommendationEngine:
    """Generates personalized recommendations using Groq LLM"""

    def __init__(self, groq_client):
        self.groq_client = groq_client

    def recommend(self, assessment: Dict, facts: Dict, language: str = 'ar') -> Optional[List[str]]:
        """
        Generate personalized recommendations

        Args:
            assessment: Final assessment dict
            facts: Patient facts
            language: 'ar' or 'en'

        Returns:
            List of recommendation strings, or None if Groq unavailable
        """
        if not self.groq_client or not self.groq_client.is_available:
            return None

        system_prompt = SYSTEM_PROMPT_AR if language == 'ar' else SYSTEM_PROMPT_EN
        user_message = self._build_message(assessment, facts, language)

        result = self.groq_client.chat(
            system_prompt=system_prompt,
            user_message=user_message,
            temperature=0.4,
            max_tokens=600
        )

        if not result:
            return None

        return self._parse_recommendations(result)

    def _build_message(self, assessment: Dict, facts: Dict, language: str) -> str:
        """Build data message for Groq"""
        risk_level = assessment.get('final_risk_level', 'UNKNOWN')

        risk_factors = []
        age = facts.get('Age')
        if age and int(str(age).split('.')[0]) > 50:
            risk_factors.append('Age > 50' if language == 'en' else 'العمر أكبر من 50')

        bp = facts.get('BloodPressure', '')
        if bp:
            try:
                systolic = int(str(bp).split('/')[0])
                if systolic >= 140:
                    risk_factors.append('High blood pressure' if language == 'en' else 'ضغط دم مرتفع')
            except (ValueError, IndexError):
                pass

        chol = facts.get('Cholesterol')
        if chol and float(str(chol)) > 240:
            risk_factors.append('High cholesterol' if language == 'en' else 'كوليسترول مرتفع')

        if str(facts.get('FastingBS', '0')) == '1':
            risk_factors.append('High fasting blood sugar' if language == 'en' else 'سكر دم مرتفع')

        if str(facts.get('ExerciseAngina', '')).upper() == 'Y':
            risk_factors.append('Exercise-induced angina' if language == 'en' else 'ألم صدر مع المجهود')

        chest_pain = facts.get('ChestPain', '')
        if chest_pain in ['TA', 'ATA']:
            risk_factors.append('Chest pain present' if language == 'en' else 'ألم صدر موجود')

        sex = facts.get('Sex', '')
        age_val = int(str(age).split('.')[0]) if age else 0

        if language == 'ar':
            rf_text = "\n".join([f"- {rf}" for rf in risk_factors]) if risk_factors else "- لا توجد عوامل خطر واضحة"
            return f"""بيانات المريض:
- العمر: {age or 'غير معروف'}
- الجنس: {sex or 'غير معروف'}
- ضغط الدم: {bp or 'غير معروف'}
- الكوليسترول: {chol or 'غير معروف'}
- مستوى الخطر النهائي: {risk_level}

عوامل الخطر المكتشفة:
{rf_text}

قدم توصيات مخصصة لهذا المريض."""
        else:
            rf_text = "\n".join([f"- {rf}" for rf in risk_factors]) if risk_factors else "- No obvious risk factors"
            return f"""Patient Data:
- Age: {age or 'Unknown'}
- Sex: {sex or 'Unknown'}
- Blood Pressure: {bp or 'Unknown'}
- Cholesterol: {chol or 'Unknown'}
- Final Risk Level: {risk_level}

Detected Risk Factors:
{rf_text}

Provide personalized recommendations for this patient."""

    def _parse_recommendations(self, text: str) -> List[str]:
        """Parse bullet-point recommendations from Groq response"""
        lines = text.strip().split('\n')
        recommendations = []

        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Remove bullet markers
            for prefix in ['•', '-', '*', '·']:
                if line.startswith(prefix):
                    line = line[len(prefix):].strip()
                    break
            # Remove numbered prefixes like "1." or "1)"
            if len(line) > 2 and line[0].isdigit() and line[1] in '.):':
                line = line[2:].strip()

            if line and len(line) > 5:
                recommendations.append(line)

        return recommendations[:6]
