

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json
import logging
from dataclasses import asdict

# استيراد المكونات
from core.self_dialog_manager import SelfDialogManager, InternalThought
from core.priority_scorer import PriorityScorer, QuestionPriority
from core.dynamic_question_selector import DynamicQuestionSelector, Question
from nlp.biobert_ner import BioBERTNER
from engine.domain_rules_engine import DomainRulesEngine

# New ML components (v6.0.0)
from engine.advanced_features import features_generator
from engine.ml_predictor import ml_predictor
from engine.final_decision_engine import final_decision_engine

# Groq API components (v7.0.0)
from groq_api.groq_client import GroqClient
from groq_api.result_interpreter import ResultInterpreter
from groq_api.recommendation_engine import RecommendationEngine

# Smart Conversation components (v8.0.0)
from groq_api.groq_ner import GroqNER
from groq_api.conversation_manager import SmartConversationManager

logger = logging.getLogger('integrated_chatbot')


class IntegratedSelfReasoningChatbot:
    """
    الـ Chatbot الذي يتحدث مع نفسه ويحدث نفسه
    يجمع:
    - Self-Dialog Manager (الحوار الذاتي)
    - Priority Scorer (حساب الأولويات)
    - Dynamic Question Selector (اختيار الأسئلة)
    """
    
    def __init__(self, language: str = 'ar', groq_api_key: str = None):
        """
        تهيئة الـ Chatbot المتكامل

        Args:
            language: اللغة الافتراضية ('ar' أو 'en')
            groq_api_key: مفتاح Groq API (اختياري)
        """
        self.language = language

        # المكونات الأساسية
        self.dialog_manager = SelfDialogManager(language)
        self.priority_scorer = PriorityScorer()
        self.question_selector = DynamicQuestionSelector()

        # المكونات الجديدة - BioBERT NER & Domain Rules
        self.biobert_ner = BioBERTNER()
        self.domain_rules = DomainRulesEngine()

        # Groq API components (v7.0.0)
        self.groq_client = GroqClient(api_key=groq_api_key)
        self.result_interpreter = ResultInterpreter(self.groq_client)
        self.recommendation_engine = RecommendationEngine(self.groq_client)

        # Smart Conversation components (v8.0.0)
        self.groq_ner = GroqNER(self.groq_client)
        self.conversation_manager = SmartConversationManager(self.groq_client, language)

        # حالة الجلسة
        self.session_id = str(datetime.now().timestamp())
        self.facts: Dict = {}
        self.inferences: Dict = {}
        self.current_risk_level = 'LOW'
        self.confidence_score = 0.0
        self.conversation_history: List[Dict] = []
        self.answered_fields: List[str] = []

        # حالة Domain Assessment
        self.domain_assessment = None

        logger.info(f"تم إنشاء جلسة جديدة: {self.session_id}")
        if self.groq_client.is_available:
            logger.info("Groq API connected successfully")
    
    def process_answer(self, field_name: str, answer_value: str) -> Dict:
        """
        معالجة إجابة المستخدم والتحدث مع النفس
        
        Args:
            field_name: اسم الحقل
            answer_value: قيمة الإجابة
            
        Returns:
            قاموس يحتوي على:
            - الفكرة الداخلية
            - الاستنتاجات
            - التحديثات
            - السؤال التالي
        """
        logger.info(f"معالجة الإجابة: {field_name} = {answer_value}")
        
        # الخطوة 1: تطبيع القيمة (تحويل الأرقام من string إلى int/float)
        normalized_value = self._normalize_value(field_name, answer_value)
        
        # الخطوة 2: تخزين الحقيقة
        self.facts[field_name] = normalized_value
        self.answered_fields.append(field_name)
        logger.info(f"تم تخزين الحقيقة: {field_name} = {normalized_value}")
        
        # الخطوة 3: الحوار الذاتي - تحليل الإجابة
        thought = self.dialog_manager.analyze_answer(
            field_name,
            normalized_value,
            self.facts
        )
        
        # الخطوة 3: الاستنتاج من الحقائق
        inference = self.dialog_manager.infer_from_facts(self.facts)
        
        # الخطوة 3.5: تقييم Domain Rules (إذا كانت البيانات كافية)
        domain_assessment = self.get_domain_assessment()
        
        # الخطوة 4: تحديث مستوى الخطر
        self.current_risk_level = self._calculate_risk_level()
        self.confidence_score = self._calculate_confidence()
        
        # الخطوة 5: التحقق من التحذيرات
        warning = None
        if self._should_warn():
            warning = self.dialog_manager.trigger_warning(
                'critical_symptoms',
                self._get_warning_severity(),
                {'field': field_name, 'value': answer_value}
            )
        
        # الخطوة 6: اتخاذ قرار عن السؤال التالي
        decision = self.dialog_manager.make_decision(self.facts, self.inferences)
        
        # الخطوة 7: حساب الأولويات الجديدة
        priorities = self.priority_scorer.calculate_priorities(
            self.facts,
            self.current_risk_level,
            self.answered_fields
        )
        
        # الخطوة 8: اختيار السؤال التالي
        next_question = self._select_next_question(priorities)
        
        # بناء الاستجابة الكاملة
        response = {
            'step': len(self.conversation_history) + 1,
            'field_processed': field_name,
            'internal_thought': {
                'thought': thought.thought,
                'category': thought.category,
                'confidence': thought.confidence
            },
            'inference': {
                'thought': inference.thought,
                'confidence': inference.confidence
            },
            'current_status': {
                'risk_level': self.current_risk_level,
                'confidence_score': self.confidence_score,
                'facts_collected': len(self.answered_fields),
                'total_facts': 11
            },
            'domain_assessment': domain_assessment if domain_assessment else None,
            'warning': {
                'triggered': warning is not None,
                'message': warning.thought if warning else None
            } if warning else None,
            'decision': {
                'message': decision.thought
            },
            'next_question': next_question if next_question else {
                'message': 'تم جمع جميع المعلومات اللازمة',
                'message_en': 'All required information collected'
            },
            'progress': {
                'percentage': int((len(self.answered_fields) / 11) * 100),
                'answered': len(self.answered_fields),
                'remaining': 11 - len(self.answered_fields)
            }
        }
        
        # حفظ في السجل
        self.conversation_history.append(response)
        
        return response
    
    def extract_fields_from_text(self, text: str) -> Dict:
        """
        استخراج المعلومات الطبية من النص الحر باستخدام BioBERT NER
        
        Args:
            text: النص المدخل
            
        Returns:
            قاموس بالحقول المستخرجة
        """
        logger.info(f"Extracting fields from text using BioBERT NER")
        
        # استخدام BioBERT NER لاستخراج المعلومات
        entities = self.biobert_ner.extract_entities(text)
        
        result = {
            'extracted': [],
            'unprocessed': []
        }
        
        # معالجة المعلومات المستخرجة
        for field_name, field_value in entities.items():
            # تحويل أسماء الحقول للنظام
            field_ar = self._get_field_arabic_name(field_name)
            
            result['extracted'].append({
                'field': field_name,
                'field_ar': field_ar,
                'value': field_value,
                'confidence': self.biobert_ner.get_entity_confidence(field_name, field_value)
            })
            
            # تخزين في facts (مع تطبيع القيمة)
            normalized_value = self._normalize_value(field_name, field_value)
            self.facts[field_name] = normalized_value
            if field_name not in self.answered_fields:
                self.answered_fields.append(field_name)
        
        logger.info(f"Extracted {len(result['extracted'])} fields using BioBERT")
        return result
    
    def get_domain_assessment(self) -> Optional[Dict]:
        """
        تقييم شامل باستخدام Domain Rules Engine
        
        WORKFLOW:
        1. Check if all 11 fields are complete
        2. If complete → Apply domain_rules.json
        3. Return full assessment with:
           - Binary features
           - Continuous features
           - Triggered rules
           - Medical insights
        
        Returns:
            تقييم كامل إذا اكتملت جميع الحقول
        """
        # تطبيق Domain Rules Engine الجديد
        result = self.domain_rules.process_complete_data(self.facts)
        
        if result['status'] == 'incomplete':
            # لم تكتمل جميع الحقول بعد
            return None
        
        # اكتملت جميع الحقول! لدينا تقييم كامل
        self.domain_assessment = result
        
        # تحديث مستوى الخطر من Domain Rules
        insights = result['insights']
        risk_level = insights['risk_level']  # Low/Medium/High

        # تحويل risk_level إلى صيغة موحدة (LOW/MODERATE/HIGH/CRITICAL)
        risk_mapping = {'Low': 'LOW', 'Medium': 'MODERATE', 'High': 'HIGH'}
        self.current_risk_level = risk_mapping.get(risk_level, 'LOW')
        
        # حساب confidence بناءً على عدد القواعد المُطبقة
        triggered_count = insights['triggered_rules_count']
        self.confidence_score = min(0.95, 0.7 + (triggered_count * 0.01))
        
        logger.info(f"Domain assessment complete: {risk_level}, {triggered_count} rules triggered")
        return result
    
    # ──────────────────────────────────────────────────────────────────
    #  Context-aware extraction
    # ──────────────────────────────────────────────────────────────────
    # When the chatbot has just asked for a specific field, the patient
    # often replies with a short / partial answer that the field-agnostic
    # NER pipeline cannot parse on its own ("كلا", "120", "Chol 310",
    # "نبضات قلبي 120"). This helper interprets such an answer in the
    # context of the asked field so the conversation does not loop on
    # the same question.
    _YES_WORDS = {
        'نعم', 'أيوا', 'أيوة', 'أيوه', 'اي', 'إي', 'بلى', 'يوجد',
        'موجود', 'أعاني', 'صحيح', 'yes', 'y', 'yeah', 'yep', 'true',
    }
    _NO_WORDS = {
        'لا', 'كلا', 'كلّا', 'مافي', 'ما في', 'ما يوجد', 'ما عندي',
        'ما أعاني', 'لا أعاني', 'لا يوجد', 'لا أشكي', 'no', 'n',
        'nope', 'never', 'false',
    }
    _NORMAL_WORDS = {
        'طبيعي', 'عادي', 'سليم', 'بخير', 'مظبوط', 'مضبوط', 'تمام',
        'normal', 'fine', 'healthy', 'ok', 'good',
    }

    # Arabic diacritics, tatweel, and the various alif / ya / ta-marbuta
    # forms that patients often type interchangeably. Stripping them lets a
    # short reply like "كلّاْ" / "أنْثى" / "الذكَر" match the canonical
    # keywords we look for ("كلا" / "أنثى" / "الذكر").
    _AR_DIACRITICS = 'ًٌٍَُِّْٰٕٖٓٔٗ٘'
    _AR_TATWEEL = 'ـ'

    @classmethod
    def _normalize_ar(cls, text: str) -> str:
        """Lower-case + strip Arabic diacritics + unify common letter
        variants so dialect / typo spellings still match our keywords."""
        if not text:
            return ''
        s = str(text)
        # Remove tashkeel
        for ch in cls._AR_DIACRITICS:
            s = s.replace(ch, '')
        # Remove tatweel
        s = s.replace(cls._AR_TATWEEL, '')
        # Unify alif forms (أ إ آ ٱ ا → ا)
        for ch in 'أإآٱ':
            s = s.replace(ch, 'ا')
        # Unify ya forms (ى → ي) and ta-marbuta (ة → ه)
        s = s.replace('ى', 'ي').replace('ة', 'ه')
        # Drop trailing punctuation noise that breaks substring matches
        s = s.replace('،', ' ').replace('؟', ' ').replace('!', ' ')
        return s.lower()

    @classmethod
    def _has_word(cls, text_lower: str, words) -> bool:
        norm = cls._normalize_ar(text_lower)
        for w in words:
            if cls._normalize_ar(w) in norm:
                return True
        return False

    # ──────────────────────────────────────────────────────────────────
    # Helpers used by _smart_extract_for_field
    # ──────────────────────────────────────────────────────────────────
    @staticmethod
    def _arabic_to_western_digits(s: str) -> str:
        """٠١٢٣٤٥٦٧٨٩ -> 0123456789 (Eastern Arabic-Indic + Persian)."""
        table = str.maketrans('٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹', '01234567890123456789')
        return s.translate(table)

    @staticmethod
    def _first_int(text: str, lo: int, hi: int):
        """First integer in [lo, hi] found in `text`, else None."""
        import re as _re
        for m in _re.finditer(r'\d+', text):
            try:
                v = int(m.group(0))
            except ValueError:
                continue
            if lo <= v <= hi:
                return v
        return None

    @staticmethod
    def _first_float(text: str, lo: float, hi: float):
        """First float in [lo, hi] found in `text`, else None."""
        import re as _re
        for m in _re.finditer(r'\d+(?:\.\d+)?', text):
            try:
                v = float(m.group(0))
            except ValueError:
                continue
            if lo <= v <= hi:
                return v
        return None

    def _smart_extract_for_field(self, field_name: str, raw_text: str):
        """Interpret `raw_text` as an answer to a question about
        `field_name`. Returns the extracted value, or None.

        Each clinical field has its own ruleset combining:
          - numeric extraction with a valid clinical range,
          - dialectal Arabic / English keyword lookups (with diacritics
            and alif / ya / ta-marbuta normalised away),
          - explicit handling of "normal / healthy" answers,
          - explicit handling of negations and the qualitative scale
            (low / moderate / high) when the patient does not give a
            precise number.
        """
        import re as _re
        if raw_text is None:
            return None
        text = str(raw_text).strip()
        if not text:
            return None

        # Convert Arabic-Indic / Persian digits so numeric checks work uniformly.
        text = self._arabic_to_western_digits(text)
        # `text_lower` is the Arabic-normalised + lower-cased form used by
        # every substring check below.
        text_lower = self._normalize_ar(text)
        # "غير طبيعي" / "non-normal" / "abnormal" must override the plain
        # NORMAL check, otherwise the trailing word "طبيعي" is mistaken
        # for a healthy reply.
        _abnormal_markers = ('غير طبيعي', 'غير عادي', 'ليس طبيعي', 'ليس عادي',
                             'abnormal', 'not normal', 'non-normal')
        is_abnormal = any(m in text_lower for m in _abnormal_markers)
        is_normal = (not is_abnormal) and self._has_word(text_lower, self._NORMAL_WORDS)
        is_no     = self._has_word(text_lower, self._NO_WORDS)
        is_yes    = self._has_word(text_lower, self._YES_WORDS)

        # ─────────────────────── 1. Age ───────────────────────
        if field_name == 'Age':
            v = self._first_int(text, 1, 120)
            if v is not None:
                return v
            if 'طفل' in text_lower or 'child' in text_lower:
                return 10
            if 'شاب' in text_lower or 'young' in text_lower:
                return 25
            if 'كبير' in text_lower or 'مسن' in text_lower or 'elderly' in text_lower or 'old' in text_lower:
                return 70
            return None

        # ─────────────────────── 2. Sex ───────────────────────
        if field_name == 'Sex':
            stripped = text_lower.strip()
            if (stripped in ('f', 'female')
                    or 'انثي' in text_lower or 'امراه' in text_lower
                    or 'بنت' in text_lower or 'سيده' in text_lower
                    or 'female' in text_lower or 'woman' in text_lower):
                return 'Female'
            if (stripped in ('m', 'male')
                    or 'ذكر' in text_lower or 'رجل' in text_lower
                    or 'ولد' in text_lower or 'male' in text_lower
                    or 'man' in text_lower):
                return 'Male'
            return None

        # ─────────────────────── 3. ChestPain ───────────────────────
        if field_name == 'ChestPain':
            if is_no or is_normal:
                return 'ASY'
            if ('asy' in text_lower or 'asymptomatic' in text_lower
                    or 'بدون اعراض' in text_lower or 'ما اشكي' in text_lower):
                return 'ASY'
            if ('غير نموذجي' in text_lower or 'atypical' in text_lower
                    or text_lower.strip() == 'ata'):
                return 'ATA'
            if ('غير ذبحه' in text_lower or 'non-anginal' in text_lower
                    or 'ليس ذبحه' in text_lower or text_lower.strip() == 'nap'):
                return 'NAP'
            if ('نموذجي' in text_lower or 'typical' in text_lower
                    or 'ذبحه صدريه' in text_lower or 'angina' in text_lower
                    or text_lower.strip() == 'ta'):
                return 'TA'
            if ('الم' in text_lower or 'pain' in text_lower
                    or 'يوجعني' in text_lower or 'وجع' in text_lower):
                return 'TA'
            return None

        # ─────────────────────── 4. BloodPressure ───────────────────────
        if field_name == 'BloodPressure':
            # Two numbers — accept "/", "على", "on", "\".
            m = _re.search(r'(\d{2,3})\s*(?:[/\\]|على|\bon\b)\s*(\d{2,3})',
                           text, _re.IGNORECASE)
            if m:
                s, d = int(m.group(1)), int(m.group(2))
                if 70 <= s <= 250 and 30 <= d <= 150:
                    return f"{s}/{d}"
            v = self._first_int(text, 70, 250)
            if v is not None:
                return f"{v}/{max(50, v - 40)}"
            if is_normal or is_no:
                return "120/80"
            if ('مرتفع' in text_lower or 'عالي' in text_lower
                    or 'high' in text_lower or 'hypertension' in text_lower):
                return "150/95"
            if ('منخفض' in text_lower or 'low' in text_lower
                    or 'hypotension' in text_lower):
                return "95/60"
            return None

        # ─────────────────────── 5. Cholesterol ───────────────────────
        if field_name == 'Cholesterol':
            v = self._first_int(text, 80, 700)
            if v is not None:
                return v
            if 'مرتفع' in text_lower or 'عالي' in text_lower or 'high' in text_lower:
                return 260
            if 'منخفض' in text_lower or 'low' in text_lower:
                return 150
            if is_normal or is_no:
                return 180
            return None

        # ─────────────────────── 6. FastingBS ───────────────────────
        if field_name == 'FastingBS':
            # Normal / no FIRST so "سكري عادي" isn't mis-read as "diabetic".
            if is_normal or is_no:
                return 0
            if ('مرتفع' in text_lower or 'عالي' in text_lower
                    or 'high' in text_lower or 'diabetic' in text_lower
                    or 'مريض سكر' in text_lower or 'سكري' in text_lower
                    or 'سكر' in text_lower):
                return 1
            v = self._first_int(text, 40, 600)
            if v is not None:
                return 1 if v > 120 else 0
            return None

        # ─────────────────────── 7. RestingECG ───────────────────────
        if field_name == 'RestingECG':
            if is_normal or is_no:
                return 'Normal'
            if ('lvh' in text_lower or 'تضخم البطين' in text_lower
                    or 'تضخم' in text_lower or 'ventricular hypertrophy' in text_lower):
                return 'LVH'
            if ('st-t' in text_lower or 'st wave' in text_lower
                    or 'موجه' in text_lower or 'اضطراب' in text_lower
                    or text_lower.strip() == 'st'):
                return 'ST'
            # "غير طبيعي" / "abnormal" without a more specific marker
            # defaults to ST-T abnormality (the most common ECG finding).
            if is_abnormal:
                return 'ST'
            return None

        # ─────────────────────── 8. MaxHR ───────────────────────
        if field_name == 'MaxHR':
            v = self._first_int(text, 40, 250)
            if v is not None:
                return v
            if ('مرتفع' in text_lower or 'سريع' in text_lower
                    or 'high' in text_lower or 'fast' in text_lower):
                return 180
            if ('منخفض' in text_lower or 'بطيء' in text_lower
                    or 'low' in text_lower or 'slow' in text_lower):
                return 110
            if is_normal or is_no:
                return 150
            return None

        # ─────────────────────── 9. ExerciseAngina ───────────────────────
        if field_name == 'ExerciseAngina':
            # NO first — "لا أعاني عند الرياضة" is the dominant clinical reply.
            if is_no or is_normal:
                return 'N'
            if is_yes:
                return 'Y'
            return None

        # ─────────────────────── 10. Oldpeak ───────────────────────
        if field_name == 'Oldpeak':
            v = self._first_float(text, 0.0, 10.0)
            if v is not None:
                return v
            if is_normal or is_no:
                return 0.0
            if 'شديد' in text_lower or 'severe' in text_lower:
                return 3.0
            if 'متوسط' in text_lower or 'moderate' in text_lower:
                return 1.5
            if 'خفيف' in text_lower or 'mild' in text_lower:
                return 0.5
            return None

        # ─────────────────────── 11. ST_Slope ───────────────────────
        if field_name == 'ST_Slope':
            if 'up' in text_lower or 'صاعد' in text_lower or 'upslop' in text_lower:
                return 'Up'
            if ('down' in text_lower or 'هابط' in text_lower
                    or 'منحدر' in text_lower or 'downslop' in text_lower):
                return 'Down'
            if 'flat' in text_lower or 'مسطح' in text_lower or is_normal:
                return 'Flat'
            return None

        return None

    def _normalize_value(self, field_name: str, value):
        """
        تطبيع القيمة - تحويل الأرقام من string إلى int/float
        
        Args:
            field_name: اسم الحقل (استخدام أسماء BioBERT الموحدة)
            value: القيمة (قد تكون string أو int أو float)
            
        Returns:
            القيمة المطبّعة (int/float للحقول الرقمية، string للباقي)
        """
        # إذا كانت القيمة بالفعل رقماً، أرجعها كما هي
        if isinstance(value, (int, float)):
            return value
        
        # الحقول الرقمية (أسماء BioBERT الموحدة)
        numeric_fields = ['Age', 'Cholesterol', 'MaxHR', 'Oldpeak', 'FastingBS']
        
        if field_name in numeric_fields:
            try:
                # محاولة تحويلها إلى int أولاً
                if '.' not in str(value):
                    return int(value)
                else:
                    return float(value)
            except (ValueError, TypeError):
                # إذا فشل التحويل، أرجع القيمة كما هي
                return value
        
        # الحقول غير الرقمية - أرجعها كـ string
        return str(value)
    
    def _get_field_arabic_name(self, field_name: str) -> str:
        """تحويل اسم الحقل للعربية - أسماء موحدة"""
        mapping = {
            'Age': 'العمر',
            'Sex': 'الجنس',
            'ChestPain': 'ألم الصدر',
            'BloodPressure': 'ضغط الدم',
            'Cholesterol': 'الكوليسترول',
            'FastingBS': 'سكر الدم الصائم',
            'RestingECG': 'تخطيط القلب',
            'MaxHR': 'معدل نبض القلب الأقصى',
            'ExerciseAngina': 'ألم مع المجهود',
            'Oldpeak': 'انخفاض ST',
            'ST_Slope': 'ميل ST'
        }
        return mapping.get(field_name, field_name)
    
    def _safe_int(self, value, default=0) -> int:
        """تحويل آمن للقيمة إلى عدد صحيح"""
        try:
            if isinstance(value, (int, float)):
                return int(value)
            if isinstance(value, str):
                import re
                numbers = re.findall(r'\d+', value)
                if numbers:
                    return int(numbers[0])
            return default
        except:
            return default
    
    def _calculate_risk_level(self) -> str:
        """حساب مستوى الخطر بناءً على الحقائق المجمعة"""
        # استخدام Domain Rules إذا كان التقييم متاحاً
        if self.domain_assessment:
            # New structure: domain_assessment['insights']['risk_level']
            if isinstance(self.domain_assessment, dict):
                if 'insights' in self.domain_assessment:
                    risk_level = self.domain_assessment['insights'].get('risk_level', 'UNKNOWN')
                    # Map from 'Low'/'Medium'/'High' to old format
                    risk_mapping = {'Low': 'LOW', 'Medium': 'MODERATE', 'High': 'HIGH'}
                    return risk_mapping.get(risk_level, 'LOW')
                # Old structure fallback
                elif 'risk_level' in self.domain_assessment:
                    return self.domain_assessment['risk_level']
        
        # الطريقة القديمة كـ fallback
        risk_count = 0
        
        # عد عوامل الخطر
        if self._safe_int(self.facts.get('Age', 0)) > 50:
            risk_count += 1
        
        if self.facts.get('ChestPain') == 'Yes':
            risk_count += 2  # وزن أعلى
        
        if self._is_high_bp(self.facts.get('BloodPressure')):
            risk_count += 1
        
        if self._is_high_chol(self.facts.get('Cholesterol')):
            risk_count += 1
        
        if self.facts.get('ExerciseAngina') in ['Yes', 'Y', 1, '1']:
            risk_count += 1

        if self.facts.get('FastingBS') in ['Yes', 'Y', 1, '1']:
            risk_count += 1
        
        # تصنيف المستوى
        if risk_count >= 4:
            return 'CRITICAL'
        elif risk_count >= 3:
            return 'HIGH'
        elif risk_count >= 2:
            return 'MODERATE'
        else:
            return 'LOW'
    
    def _is_high_bp(self, bp_value) -> bool:
        """هل ضغط الدم مرتفع؟"""
        try:
            if isinstance(bp_value, str):
                systolic = int(bp_value.split('/')[0])
                return systolic >= 140
        except:
            pass
        return False
    
    def _is_high_chol(self, chol_value) -> bool:
        """هل الكوليسترول مرتفع؟"""
        try:
            chol = float(chol_value) if isinstance(chol_value, (int, float, str)) else 0
            return chol > 240
        except:
            pass
        return False
    
    def _calculate_confidence(self) -> float:
        """حساب درجة الثقة"""
        # استخدام Domain Rules confidence إذا كان متاحاً
        if self.domain_assessment and 'confidence' in self.domain_assessment:
            return self.domain_assessment['confidence']
        
        # الطريقة القديمة كـ fallback
        facts_count = len(self.answered_fields)
        base_confidence = min(0.3 + (facts_count * 0.055), 0.95)
        
        # زيادة الثقة إذا كانت الأجوبة واضحة
        high_quality_facts = sum(1 for f in self.answered_fields 
                                if f in ['ChestPain', 'BloodPressure', 'Cholesterol'])
        
        confidence = base_confidence + (high_quality_facts * 0.05)
        return min(confidence, 1.0)
    
    def _should_warn(self) -> bool:
        """هل يجب تحذير المستخدم؟"""
        # تحذير إذا كان هناك ألم صدر شديد
        if self.facts.get('ChestPain') == 'Yes':
            return True
        
        # تحذير إذا كان ضغط الدم حرج
        if self._is_critical_bp(self.facts.get('BloodPressure')):
            return True
        
        # تحذير إذا كان هناك 3+ عوامل خطر
        if self.current_risk_level == 'CRITICAL':
            return True
        
        return False
    
    def _is_critical_bp(self, bp_value) -> bool:
        """هل ضغط الدم حرج جداً؟"""
        try:
            if isinstance(bp_value, str):
                systolic, diastolic = map(int, bp_value.split('/'))
                return systolic >= 180 or diastolic >= 120
        except:
            pass
        return False
    
    def _get_warning_severity(self) -> str:
        """تحديد شدة التحذير"""
        if self.current_risk_level == 'CRITICAL':
            return 'critical'
        elif self.current_risk_level == 'HIGH':
            return 'high'
        else:
            return 'medium'
    
    def _select_next_question(self, priorities: List[QuestionPriority]) -> Optional[Dict]:
        """اختيار السؤال التالي"""
        if not priorities:
            return None
        
        # في حالة الخطر العالي، اختر أسئلة حرجة
        if self.current_risk_level in ['CRITICAL', 'HIGH']:
            critical = [p for p in priorities if p.is_critical]
            if critical:
                priorities = critical
        
        # اختر السؤال
        next_q = self.question_selector.select_next_question(
            priorities,
            self.facts,
            self.language
        )
        
        return next_q
    
    def set_groq_api_key(self, api_key: str):
        """Update Groq API key at runtime"""
        self.groq_client.set_api_key(api_key)
        self.result_interpreter = ResultInterpreter(self.groq_client)
        self.recommendation_engine = RecommendationEngine(self.groq_client)
        self.groq_ner = GroqNER(self.groq_client)
        self.conversation_manager = SmartConversationManager(self.groq_client, self.language)
        logger.info(f"Groq API key updated, available: {self.groq_client.is_available}")

    @property
    def conversation_mode(self) -> str:
        """Return current conversation mode: 'smart' or 'classic'"""
        return "smart" if self.groq_client.is_available else "classic"

    def process_smart_input(self, text: str) -> Dict:
        """
        معالجة النص الحر من المريض — الوضع الذكي (v8.0.0)

        1. يستخرج الحقول باستخدام Groq NER (+ BioBERT كاحتياط)
        2. يخزن الحقول ويحدث الحالة
        3. يولد رد طبيب طبيعي باستخدام ConversationManager

        Args:
            text: ما كتبه المريض (نص حر بالعربية أو الإنجليزية)

        Returns:
            Dict مع: mode, extracted_fields, doctor_response, progress, warning, next_field
        """
        logger.info(f"Smart input processing: '{text[:60]}...'")

        # === الخطوة 0: تفسير سياقي للسؤال المطروح ===
        # If the previous turn asked for a specific field, try a smart
        # context-aware interpretation first. This catches short replies
        # like "كلا", "120", "Chol 310" that the generic NER may miss.
        context_extracted = {}
        last_asked = getattr(self, '_last_asked_field', None)
        if last_asked and last_asked not in self.answered_fields:
            ctx_value = self._smart_extract_for_field(last_asked, text)
            if ctx_value is not None:
                context_extracted[last_asked] = ctx_value
                logger.info(f"Context-aware extraction: {last_asked} = {ctx_value}")

        # === الخطوة 1: استخراج الحقول ===
        # Try Groq NER first
        groq_extracted = self.groq_ner.extract(text)

        # Try BioBERT as supplement/fallback
        biobert_extracted = self.biobert_ner.extract_entities(text)

        # Merge: context > Groq > BioBERT, then fill gaps
        merged_extracted = {}
        all_fields = set(
            list(context_extracted.keys())
            + list(groq_extracted.keys())
            + list(biobert_extracted.keys())
        )

        for field in all_fields:
            if field in self.answered_fields:
                continue  # Skip already answered
            if field in context_extracted:
                merged_extracted[field] = context_extracted[field]
            elif field in groq_extracted:
                merged_extracted[field] = groq_extracted[field]
            elif field in biobert_extracted:
                merged_extracted[field] = biobert_extracted[field]

        logger.info(f"Merged extraction: {len(merged_extracted)} new fields "
                    f"(Groq: {len(groq_extracted)}, BioBERT: {len(biobert_extracted)})")

        # === الخطوة 2: تخزين الحقول ===
        extracted_details = []
        for field_name, value in merged_extracted.items():
            normalized = self._normalize_value(field_name, value)
            self.facts[field_name] = normalized
            if field_name not in self.answered_fields:
                self.answered_fields.append(field_name)

            extracted_details.append({
                'field': field_name,
                'field_ar': self._get_field_arabic_name(field_name),
                'value': normalized,
                'source': 'groq' if field_name in groq_extracted else 'biobert'
            })

        # === الخطوة 3: تحديث الحالة ===
        self.current_risk_level = self._calculate_risk_level()
        self.confidence_score = self._calculate_confidence()

        # Internal dialog for each extracted field
        last_thought = None
        for detail in extracted_details:
            thought = self.dialog_manager.analyze_answer(
                detail['field'], detail['value'], self.facts
            )
            last_thought = thought

        inference = self.dialog_manager.infer_from_facts(self.facts)

        # Domain assessment check
        domain_assessment = self.get_domain_assessment()

        # === الخطوة 4: تحديد الحقل التالي ===
        remaining_fields = [f for f in
            ['Age', 'Sex', 'ChestPain', 'BloodPressure', 'Cholesterol',
             'FastingBS', 'RestingECG', 'MaxHR', 'ExerciseAngina', 'Oldpeak', 'ST_Slope']
            if f not in self.answered_fields
        ]

        priorities = self.priority_scorer.calculate_priorities(
            self.facts, self.current_risk_level, self.answered_fields
        )

        next_field = None
        next_question_classic = None
        if priorities:
            next_field = priorities[0].field_name
            next_question_classic = self._select_next_question(priorities)

        # Remember which field the chatbot is about to ask for, so the
        # next turn can interpret short answers in this context.
        self._last_asked_field = next_field

        # === الخطوة 5: Warning check ===
        warning = None
        if self._should_warn():
            warning = self.dialog_manager.trigger_warning(
                'critical_symptoms',
                self._get_warning_severity(),
                {'text': text}
            )

        # === الخطوة 6: توليد رد الطبيب الذكي ===
        doctor_response = None
        mode = "smart"

        if next_field and self.groq_client.is_available:
            doctor_response = self.conversation_manager.generate_response_with_question(
                patient_message=text,
                extracted_fields=merged_extracted,
                collected_facts=self.facts,
                remaining_fields=remaining_fields,
                next_field=next_field,
                risk_level=self.current_risk_level
            )
        elif not remaining_fields and self.groq_client.is_available:
            # All fields collected
            doctor_response = self.conversation_manager._generate_completion_message(self.facts)

        # Fallback to classic if Groq conversation fails
        if not doctor_response:
            mode = "classic"
            logger.info("Falling back to classic mode for this turn")

        # === بناء الاستجابة ===
        response = {
            'mode': mode,
            'step': len(self.conversation_history) + 1,
            'extracted_fields': extracted_details,
            'doctor_response': doctor_response,
            'next_field': next_field,
            'next_question': next_question_classic,  # Classic fallback
            'internal_thought': {
                'thought': last_thought.thought if last_thought else '',
                'category': last_thought.category if last_thought else 'analysis',
                'confidence': last_thought.confidence if last_thought else 0
            },
            'inference': {
                'thought': inference.thought,
                'confidence': inference.confidence
            },
            'current_status': {
                'risk_level': self.current_risk_level,
                'confidence_score': self.confidence_score,
                'facts_collected': len(self.answered_fields),
                'total_facts': 11
            },
            'domain_assessment': domain_assessment,
            'warning': {
                'triggered': warning is not None,
                'message': warning.thought if warning else None
            },
            'progress': {
                'percentage': int((len(self.answered_fields) / 11) * 100),
                'answered': len(self.answered_fields),
                'remaining': 11 - len(self.answered_fields)
            },
            'all_complete': len(remaining_fields) == 0
        }

        self.conversation_history.append(response)
        return response

    def get_smart_greeting(self) -> Optional[str]:
        """
        Get the initial doctor greeting for smart mode.
        Returns None if Groq is unavailable.
        """
        return self.conversation_manager.generate_greeting()

    def get_current_status(self) -> Dict:
        """الحصول على الحالة الحالية"""
        return {
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'language': self.language,
            'facts_count': len(self.answered_fields),
            'risk_level': self.current_risk_level,
            'confidence': self.confidence_score,
            'conversation_length': len(self.conversation_history),
            'internal_monologue': self.dialog_manager.get_internal_monologue()
        }
    
    def get_final_assessment(self) -> Dict:
        """
        الحصول على التقييم النهائي الشامل
        
        يدمج:
        1. Domain Rules Analysis
        2. Advanced Features Generation
        3. ML Model Prediction
        4. Final Decision (Rule-Based Decision Tree)
        
        Returns:
            التقييم الشامل النهائي
        """
        if len(self.answered_fields) < 8:  # يجب جمع معظم الحقائق
            return {
                'status': 'incomplete',
                'message': 'لم يتم جمع معلومات كافية',
                'facts_collected': len(self.answered_fields),
                'facts_needed': 11
            }
        
        logger.info("Generating comprehensive final assessment with ML integration")
        
        # 1. Domain Rules Analysis (موجود بالفعل)
        domain_assessment = self.domain_assessment if self.domain_assessment else {}
        
        # 2. Generate Advanced Features
        try:
            advanced_features = features_generator.generate(self.facts)
            features_summary = features_generator.get_feature_summary(advanced_features)
            logger.info(f"Generated {len(advanced_features.columns)} advanced features")
        except Exception as e:
            logger.error(f"Error generating advanced features: {e}")
            advanced_features = None
            features_summary = {}
        
        # 3. ML Model Prediction
        try:
            if advanced_features is not None:
                ml_prediction = ml_predictor.predict(advanced_features)
                logger.info(f"ML Prediction: {ml_prediction.get('prediction')} "
                          f"(prob: {ml_prediction.get('probability', 0):.2%})")
            else:
                ml_prediction = {'probability': 0.0, 'prediction': 'Unknown', 
                               'confidence': 0.0, 'risk_level': 'UNKNOWN',
                               'source': 'Error'}
        except Exception as e:
            logger.error(f"Error in ML prediction: {e}")
            ml_prediction = {'probability': 0.0, 'prediction': 'Unknown',
                           'confidence': 0.0, 'risk_level': 'UNKNOWN',
                           'source': 'Error'}
        
        # 4. Final Decision using Rule-Based Decision Tree
        try:
            if advanced_features is not None:
                final_decision = final_decision_engine.make_decision(
                    domain_assessment,
                    ml_prediction,
                    advanced_features
                )
                logger.info(f"Final Decision: {final_decision.get('final_risk_level')}")
            else:
                final_decision = self._generate_fallback_decision(domain_assessment)
        except Exception as e:
            logger.error(f"Error in final decision: {e}")
            final_decision = self._generate_fallback_decision(domain_assessment)
        
        # مزامنة مستوى الخطر مع القرار النهائي
        if final_decision and 'final_risk_level' in final_decision:
            self.current_risk_level = final_decision['final_risk_level']

        # 5. Groq AI Enhancement (v7.0.0)
        groq_interpretation = None
        groq_recommendations = None

        if self.groq_client.is_available and final_decision:
            try:
                groq_interpretation = self.result_interpreter.interpret(
                    final_decision, self.facts, self.language
                )
                logger.info("Groq interpretation generated")
            except Exception as e:
                logger.error(f"Error generating Groq interpretation: {e}")

            try:
                groq_recommendations = self.recommendation_engine.recommend(
                    final_decision, self.facts, self.language
                )
                logger.info("Groq recommendations generated")
            except Exception as e:
                logger.error(f"Error generating Groq recommendations: {e}")

        # بناء التقييم الشامل
        assessment = {
            'status': 'complete',

            # القسم 1: Domain Rules Analysis
            'domain_rules': domain_assessment,

            # القسم 2: Advanced Features
            # NumberOfVesselsColored is auto-injected as 0 to keep the
            # Keras model's input shape happy (see advanced_features.py).
            # Exclude it from the user-facing count so the displayed
            # number matches the 58-feature figure used everywhere else
            # in the documentation (11 base + 41 advanced + 6 frequency).
            'advanced_features': {
                'summary': features_summary,
                'total_features': sum(
                    1 for c in (advanced_features.columns if advanced_features is not None else [])
                    if c != 'NumberOfVesselsColored'
                )
            },

            # القسم 3: ML Model Prediction
            'ml_prediction': ml_prediction,

            # القسم 4: Final Decision
            'final_decision': final_decision,

            # القسم 5: Groq AI Enhancement (v7.0.0)
            'groq_interpretation': groq_interpretation,
            'groq_recommendations': groq_recommendations,
            'groq_available': self.groq_client.is_available,

            # معلومات عامة
            'metadata': {
                'facts_collected': len(self.answered_fields),
                'facts_summary': self.facts,
                'session_id': self.session_id,
                'timestamp': datetime.now().isoformat(),
                'version': '7.0.0'
            }
        }

        return assessment
    
    def _generate_fallback_decision(self, domain_assessment: Dict) -> Dict:
        """
        توليد قرار احتياطي في حالة فشل ML
        
        Args:
            domain_assessment: تقييم القواعد الطبية
            
        Returns:
            قرار احتياطي بسيط
        """
        # The domain engine returns its risk_level inside
        # domain_assessment['insights'] (capitalised as Low / Medium / High).
        # Read it from the correct location and normalise to upper-case so
        # the downstream risk_mapping always finds it.
        insights = domain_assessment.get('insights', {}) or {}
        domain_risk_raw = (
            insights.get('risk_level')
            or domain_assessment.get('risk_level')
            or 'UNKNOWN'
        )
        domain_risk = str(domain_risk_raw).upper()

        # تحويل من Domain risk لـ Final risk
        risk_mapping = {
            'CRITICAL': 'HIGH',
            'HIGH': 'HIGH',
            'MEDIUM': 'MODERATE',
            'MODERATE': 'MODERATE',
            'LOW': 'LOW',
            'UNKNOWN': 'MODERATE'
        }

        final_risk = risk_mapping.get(domain_risk, 'MODERATE')
        
        return {
            'final_risk_level': final_risk,
            'final_risk_level_ar': self._translate_risk_level(final_risk),
            'confidence': 0.60,
            'reasoning_en': f'Based on domain rules analysis only (ML unavailable)',
            'reasoning_ar': f'بناءً على القواعد الطبية فقط (ML غير متاح)',
            'sources': {
                'domain_rules': {
                    'risk_level': domain_risk
                }
            },
            'recommendations': domain_assessment.get('insights', {}).get('recommendations_ar', []),
            'metadata': {
                'fallback': True,
                'domain_risk': domain_risk
            }
        }
    
    def _translate_risk_level(self, risk_level: str) -> str:
        """ترجمة مستوى الخطر للعربية"""
        translations = {
            'CRITICAL': 'حرج',
            'HIGH': 'عالي',
            'MODERATE': 'متوسط',
            'LOW': 'منخفض'
        }
        return translations.get(risk_level, risk_level)
    
    def _generate_diagnosis(self) -> str:
        """توليد التشخيص"""
        if self.current_risk_level == 'CRITICAL':
            return 'احتمالية عالية جداً لأمراض القلب - يجب استشارة طبيب فوراً'
        elif self.current_risk_level == 'HIGH':
            return 'احتمالية عالية لأمراض القلب - يجب استشارة طبيب متخصص'
        elif self.current_risk_level == 'MODERATE':
            return 'احتمالية متوسطة لأمراض القلب - يجب متابعة دقيقة'
        else:
            return 'احتمالية منخفضة لأمراض القلب - استمر في نمط حياة صحي'

    def _calculate_risk_score(self) -> float:
        """حساب درجة الخطر من 0-10"""
        risk_scores = {
            'CRITICAL': 8.5,
            'HIGH': 6.5,
            'MODERATE': 4.0,
            'LOW': 2.0
        }
        return risk_scores.get(self.current_risk_level, 0)
    
    def _generate_recommendations(self) -> List[str]:
        """توليد التوصيات"""
        recommendations = []
        
        if self.current_risk_level in ['CRITICAL', 'HIGH']:
            recommendations.append("استشارة طبيب قلب متخصص بشكل عاجل")
            recommendations.append("إجراء فحوصات إضافية (ECG، Stress test)")
        
        if self.facts.get('ChestPain') == 'Yes':
            recommendations.append("تجنب المجهود الشديد والتوتر")
        
        if self._is_high_chol(self.facts.get('Cholesterol')):
            recommendations.append("تحسين نمط التغذية وتقليل الدهون")
            recommendations.append("قد يحتاج لأدوية لخفض الكوليسترول")
        
        if self._is_high_bp(self.facts.get('BloodPressure')):
            recommendations.append("مراقبة ضغط الدم بانتظام")
            recommendations.append("تقليل الملح والتوتر")
        
        if self.facts.get('FastingBloodSugar') == 'Yes':
            recommendations.append("مراجعة طبيب الغدد الصماء للسكري")
        
        if not recommendations:
            recommendations.append("الاستمرار في نمط حياة صحي")
            recommendations.append("المتابعة الدورية مع الطبيب")
        
        return recommendations
    
    def _generate_full_reasoning(self) -> str:
        """توليد التفسير الكامل للتشخيص"""
        reasoning = " التحليل الكامل:\n"
        reasoning += "=" * 50 + "\n"
        
        # عوامل الخطر الموجودة
        risk_factors = []
        
        if self._safe_int(self.facts.get('Age', 0)) > 50:
            risk_factors.append(f" العمر: {self.facts['Age']} سنة (> 50)")
        
        if self.facts.get('ChestPain') == 'Yes':
            risk_factors.append(" ألم في الصدر (علامة تحذيرية)")
        
        if self._is_high_bp(self.facts.get('BloodPressure')):
            risk_factors.append(f" ضغط دم مرتفع: {self.facts['BloodPressure']}")
        
        if self._is_high_chol(self.facts.get('Cholesterol')):
            risk_factors.append(f" كوليسترول مرتفع: {self.facts['Cholesterol']}")
        
        if self.facts.get('ExerciseInducedAngina') == 'Yes':
            risk_factors.append(" ألم مع المجهود")
        
        if self.facts.get('FastingBloodSugar') == 'Yes':
            risk_factors.append(" سكر الدم مرتفع")
        
        reasoning += "\n".join(risk_factors) if risk_factors else " لا توجد عوامل خطر واضحة"
        
        reasoning += "\n\n" + "=" * 50 + "\n"
        reasoning += f"النتيجة النهائية: {self._generate_diagnosis()}\n"
        reasoning += f"درجة الخطر: {self.current_risk_level} ({self._calculate_risk_score():.1f}/10)\n"
        reasoning += f"درجة الثقة: {self.confidence_score:.0%}\n"
        
        return reasoning
    
    def export_session(self) -> Dict:
        """تصدير جلسة كاملة"""
        return {
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'language': self.language,
            'facts': self.facts,
            'risk_level': self.current_risk_level,
            'confidence': self.confidence_score,
            'conversation_history': self.conversation_history,
            'assessment': self.get_final_assessment(),
            'internal_monologue': self.dialog_manager.get_internal_monologue()
        }
    
    def save_session(self, filepath: str):
        """حفظ الجلسة في ملف"""
        import json
        
        session_data = self.export_session()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"تم حفظ الجلسة في: {filepath}")


# مثال على الاستخدام
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "="*70)
    print(" SELF-REASONING CHATBOT - Integrated Demo")
    print("="*70 + "\n")
    
    # إنشاء الـ Chatbot
    chatbot = IntegratedSelfReasoningChatbot(language='ar')
    
    # محاكاة حوار كامل
    answers = [
        ('Age', '55'),
        ('Sex', 'Male'),
        ('ChestPain', 'Yes'),
        ('BloodPressure', '145/90'),
        ('Cholesterol', '280'),
        ('FastingBloodSugar', 'Yes'),
        ('RestingECG', 'Abnormal'),
        ('MaxHeartRate', '95'),
    ]
    
    for field, value in answers:
        print(f"\n المستخدم: {field} = {value}")
        print("" * 70)
        
        # معالجة الإجابة
        response = chatbot.process_answer(field, value)
        
        # عرض النتائج
        print(f"\n الفكرة الداخلية:")
        print(f"   {response['internal_thought']['thought']}")
        
        print(f"\n الاستنتاج:")
        print(f"   {response['inference']['thought']}")
        
        print(f"\n الحالة الحالية:")
        print(f"   مستوى الخطر: {response['current_status']['risk_level']}")
        print(f"   ثقة: {response['current_status']['confidence_score']:.0%}")
        print(f"   {response['current_status']['facts_collected']}/{response['current_status']['total_facts']} معلومات")
        
        if response.get('warning') and response['warning']['triggered']:
            print(f"\n تحذير:")
            print(f"   {response['warning']['message']}")
        
        if response['next_question']:
            print(f"\n السؤال التالي:")
            print(f"   {response['next_question'].get('question', response['next_question'].get('message'))}")
    
    # التقييم النهائي
    print("\n" + "="*70)
    print(" التقييم النهائي")
    print("="*70 + "\n")
    
    assessment = chatbot.get_final_assessment()
    
    print(assessment.get('reasoning', ''))
    print("\n" + "="*70)
    print(" الجلسة انتهت بنجاح!")
    print("="*70 + "\n")
