"""
Smart Conversation Manager — إدارة المحادثة الذكية
Generates natural doctor-like conversation using Groq LLM.
The PriorityScorer still decides WHAT to ask — this module decides HOW to ask it.
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# أوصاف الحقول للمحادثة — تساعد الطبيب يفهم شنو يسأل
FIELD_DESCRIPTIONS = {
    "Age": {
        "ar": "عمر المريض",
        "en": "patient's age"
    },
    "Sex": {
        "ar": "جنس المريض (ذكر/أنثى)",
        "en": "patient's sex (male/female)"
    },
    "ChestPain": {
        "ar": "هل يعاني من ألم في الصدر ونوعه",
        "en": "chest pain presence and type"
    },
    "BloodPressure": {
        "ar": "ضغط الدم (الانقباضي/الانبساطي)",
        "en": "blood pressure (systolic/diastolic)"
    },
    "Cholesterol": {
        "ar": "مستوى الكوليسترول في الدم",
        "en": "blood cholesterol level"
    },
    "FastingBS": {
        "ar": "مستوى سكر الدم الصائم",
        "en": "fasting blood sugar level"
    },
    "RestingECG": {
        "ar": "نتيجة تخطيط القلب أثناء الراحة",
        "en": "resting ECG result"
    },
    "MaxHR": {
        "ar": "أقصى معدل لنبض القلب",
        "en": "maximum heart rate achieved"
    },
    "ExerciseAngina": {
        "ar": "هل يحصل ألم صدر أثناء المجهود البدني",
        "en": "exercise-induced chest pain (angina)"
    },
    "Oldpeak": {
        "ar": "قيمة انخفاض مقطع ST في التخطيط",
        "en": "ST depression value (oldpeak)"
    },
    "ST_Slope": {
        "ar": "اتجاه منحنى ST في التخطيط",
        "en": "ST slope direction during exercise"
    },
}

SYSTEM_PROMPT_AR = """أنت طبيب قلب متخصص تجري مقابلة مع مريض لتقييم خطر أمراض القلب.
أسلوبك: مهني، متعاطف، يستخدم لغة بسيطة ومفهومة.

المعلومات المطلوبة التي تحتاج جمعها:
{remaining_fields_text}

المعلومات التي جمعتها حتى الآن:
{collected_facts_text}

السؤال التالي الأهم هو عن: {next_field_description}

القواعد:
- اعترف بما قاله المريض أولاً (شكراً، أفهم، إلخ)
- إذا المريض ذكر معلومات مهمة (ضغط مرتفع، ألم، إلخ) علّق عليها بإيجاز
- ثم اسأل عن الحقل التالي بأسلوب طبيعي ومحادثة عادية
- لا تذكر أسماء تقنية (مثل "ChestPain" أو "ST_Slope")
- اسأل سؤال واحد فقط في كل رد
- الرد يكون 2-3 جمل فقط
- لا تشخص المريض — فقط اجمع المعلومات
- لا تستخدم إيموجي
- الرد بالعربية فقط"""

SYSTEM_PROMPT_EN = """You are a specialized cardiologist conducting a patient interview to assess heart disease risk.
Style: professional, empathetic, using simple and clear language.

Information you still need to collect:
{remaining_fields_text}

Information collected so far:
{collected_facts_text}

The next most important question is about: {next_field_description}

Rules:
- First acknowledge what the patient said (thank you, I understand, etc.)
- If the patient mentioned important info (high BP, pain, etc.) briefly comment on it
- Then ask about the next field naturally, as in a normal conversation
- Do NOT mention technical field names (like "ChestPain" or "ST_Slope")
- Ask only ONE question per response
- Keep response to 2-3 sentences only
- Do NOT diagnose the patient — only collect information
- Do not use emoji
- Response in English only"""

GREETING_PROMPT_AR = """أنت مساعد ذكي تبدأ محادثة مع مستخدم جديد لتقييم خطر أمراض القلب.

رحّب بالمستخدم بأسلوب دافئ ومهني، واطلب منه أن يخبرك عن نفسه (العمر والجنس) أو أي شكوى يعاني منها.
لا تذكر اسم النظام، ولا تقدّم نفسك كطبيب أو دكتور — فقط ترحيب مباشر وودود ثم اطلب المعلومات.
اجعل الرد 2-3 جمل فقط. لا تستخدم إيموجي. الرد بالعربية."""

GREETING_PROMPT_EN = """You are an intelligent assistant starting a conversation with a new user to assess heart disease risk.

Greet the user warmly and professionally, asking them to tell you about themselves (age and sex) or any concerns they have.
Do NOT mention the system name, and do NOT present yourself as a doctor or physician — just a direct, friendly greeting followed by the request for information.
Keep response to 2-3 sentences only. Do not use emoji. Response in English."""


class SmartConversationManager:
    """
    Manages natural doctor-patient conversation using Groq LLM.
    The PriorityScorer decides WHAT to ask. This manager decides HOW to ask it.
    """

    def __init__(self, groq_client, language: str = 'ar'):
        self.groq_client = groq_client
        self.language = language
        self.conversation_history: List[Dict[str, str]] = []
        self._max_history = 8  # Keep last 8 messages for context

    def set_language(self, language: str):
        """Update conversation language."""
        self.language = language

    def reset(self):
        """Reset conversation history for new session."""
        self.conversation_history = []

    def generate_greeting(self) -> Optional[str]:
        """
        Generate the opening doctor greeting.

        Returns:
            Greeting text or None if Groq unavailable.
        """
        if not self.groq_client or not self.groq_client.is_available:
            return None

        prompt = GREETING_PROMPT_AR if self.language == 'ar' else GREETING_PROMPT_EN

        try:
            response = self.groq_client.chat(
                system_prompt=prompt,
                user_message="ابدأ المقابلة" if self.language == 'ar' else "Start the interview",
                temperature=0.5,
                max_tokens=200
            )

            if response:
                self.conversation_history.append({
                    "role": "doctor",
                    "content": response
                })
                logger.info("Smart greeting generated")

            return response

        except Exception as e:
            logger.error(f"Failed to generate greeting: {e}")
            return None

    def generate_response_with_question(
        self,
        patient_message: str,
        extracted_fields: Dict,
        collected_facts: Dict,
        remaining_fields: List[str],
        next_field: str,
        risk_level: str = "LOW"
    ) -> Optional[str]:
        """
        Generate a natural doctor response that acknowledges the patient's input
        and asks the next priority question.

        Args:
            patient_message: What the patient just said
            extracted_fields: Fields extracted from this message
            collected_facts: All facts collected so far
            remaining_fields: List of field names still needed
            next_field: The highest-priority field to ask about next
            risk_level: Current risk assessment level

        Returns:
            Natural doctor response text, or None if Groq unavailable.
        """
        if not self.groq_client or not self.groq_client.is_available:
            return None

        if not remaining_fields:
            return self._generate_completion_message(collected_facts)

        # Add patient message to history
        self.conversation_history.append({
            "role": "patient",
            "content": patient_message
        })

        # Build system prompt with context
        system_prompt = self._build_system_prompt(
            collected_facts, remaining_fields, next_field
        )

        # Build user message with context about what was extracted
        user_message = self._build_context_message(
            patient_message, extracted_fields, remaining_fields
        )

        try:
            response = self.groq_client.chat(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.4,
                max_tokens=250
            )

            if response:
                # Add doctor response to history
                self.conversation_history.append({
                    "role": "doctor",
                    "content": response
                })
                # Trim history to max size
                self._trim_history()
                logger.info(f"Smart response generated, asking about: {next_field}")

            return response

        except Exception as e:
            logger.error(f"Failed to generate smart response: {e}")
            return None

    def _build_system_prompt(
        self,
        collected_facts: Dict,
        remaining_fields: List[str],
        next_field: str
    ) -> str:
        """Build the system prompt with current conversation context."""
        lang = self.language
        idx = 'ar' if lang == 'ar' else 'en'

        # Remaining fields descriptions
        remaining_text = "\n".join([
            f"- {FIELD_DESCRIPTIONS.get(f, {}).get(idx, f)}"
            for f in remaining_fields
        ])

        # Collected facts summary
        if collected_facts:
            facts_text = "\n".join([
                f"- {FIELD_DESCRIPTIONS.get(k, {}).get(idx, k)}: {v}"
                for k, v in collected_facts.items()
                if v is not None
            ])
        else:
            facts_text = "لا توجد معلومات بعد" if lang == 'ar' else "No information collected yet"

        # Next field description
        next_desc = FIELD_DESCRIPTIONS.get(next_field, {}).get(idx, next_field)

        template = SYSTEM_PROMPT_AR if lang == 'ar' else SYSTEM_PROMPT_EN

        return template.format(
            remaining_fields_text=remaining_text,
            collected_facts_text=facts_text,
            next_field_description=next_desc
        )

    def _build_context_message(
        self,
        patient_message: str,
        extracted_fields: Dict,
        remaining_fields: List[str]
    ) -> str:
        """Build the context message with patient input and extraction info."""
        lang = self.language
        idx = 'ar' if lang == 'ar' else 'en'

        if extracted_fields:
            fields_info = ", ".join([
                f"{FIELD_DESCRIPTIONS.get(k, {}).get(idx, k)}={v}"
                for k, v in extracted_fields.items()
            ])
            if lang == 'ar':
                return f"""المريض قال: "{patient_message}"
(تم استخراج: {fields_info})
المتبقي: {len(remaining_fields)} حقول
رد على المريض واسأل السؤال التالي."""
            else:
                return f"""Patient said: "{patient_message}"
(Extracted: {fields_info})
Remaining: {len(remaining_fields)} fields
Respond to the patient and ask the next question."""
        else:
            if lang == 'ar':
                return f"""المريض قال: "{patient_message}"
(لم يتم استخراج أي معلومات طبية من هذا الرد)
اطلب من المريض توضيح إجابته أو أعد السؤال بطريقة مختلفة."""
            else:
                return f"""Patient said: "{patient_message}"
(No medical information could be extracted from this response)
Ask the patient to clarify or rephrase the question differently."""

    def _generate_completion_message(self, collected_facts: Dict) -> Optional[str]:
        """Generate a message when all fields are collected."""
        if not self.groq_client or not self.groq_client.is_available:
            return None

        lang = self.language
        if lang == 'ar':
            prompt = """أنت طبيب قلب. اشكر المريض على صبره وأخبره أنك جمعت كل المعلومات المطلوبة
وستقوم الآن بتحليل البيانات وتقديم التقييم. اجعل الرد 2-3 جمل. لا تستخدم إيموجي."""
            msg = "تم جمع جميع المعلومات المطلوبة."
        else:
            prompt = """You are a cardiologist. Thank the patient for their patience and inform them
you have collected all required information and will now analyze the data and provide an assessment.
Keep response to 2-3 sentences. No emoji."""
            msg = "All required information has been collected."

        try:
            return self.groq_client.chat(
                system_prompt=prompt,
                user_message=msg,
                temperature=0.4,
                max_tokens=150
            )
        except Exception as e:
            logger.error(f"Failed to generate completion message: {e}")
            return None

    def _trim_history(self):
        """Keep only the last N messages in conversation history."""
        if len(self.conversation_history) > self._max_history:
            self.conversation_history = self.conversation_history[-self._max_history:]

    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return list(self.conversation_history)
