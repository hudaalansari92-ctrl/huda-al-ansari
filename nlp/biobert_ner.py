

import re
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger('biobert_ner')


_AR_DIACRITICS = re.compile(r'[ً-ٰٟـ]')

_NORMAL_WORDS = {
    'طبيعي', 'طبيعى', 'طبيعيه', 'طبيعية', 'طبيعيا',
    'عادي', 'عادى', 'عاديه', 'عادية',
    'سليم', 'سليمه', 'سليمة',
    'منيح', 'زين', 'كويس', 'كويسه', 'تمام',
    'normal', 'ok', 'fine', 'healthy', 'good', 'okay',
}

_NORMAL_DEFAULTS = {
    'ChestPain':       'ASY',
    'BloodPressure':   '120/80',
    'Cholesterol':     180,
    'FastingBS':       0,
    'RestingECG':      'Normal',
    'MaxHR':           150,
    'ExerciseAngina':  'N',
    'Oldpeak':         0.0,
    'ST_Slope':        'Up',
}


class BioBERTNER:
    """
    BioBERT Named Entity Recognition - Unified Strategy
    استراتيجية موحدة لاستخراج جميع الحقول الـ 11
    """

    def __init__(self):
        """تهيئة BioBERT NER مع استراتيجية موحدة"""
        self.medical_patterns = self._init_medical_patterns()
        self.medical_keywords = self._init_medical_keywords()
        logger.info("BioBERT NER initialized with unified strategy")

    @staticmethod
    def _normalize_ar(text: str) -> str:
        """
        تطبيع النص العربي:
        - إزالة التشكيل (الحركات)
        - توحيد الألف: أ إ آ ٱ → ا
        - توحيد الياء: ى → ي
        - توحيد التاء المربوطة: ة → ه
        """
        if not text:
            return ''
        text = _AR_DIACRITICS.sub('', text)
        text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ٱ', 'ا')
        text = text.replace('ى', 'ي').replace('ؤ', 'و').replace('ئ', 'ي')
        text = text.replace('ة', 'ه')
        return text.lower().strip()

    @classmethod
    def _is_normal_only(cls, text: str) -> bool:
        """
        هل النص هو فقط كلمة 'طبيعي' / 'normal' بدون أي رقم أو محتوى آخر؟
        """
        if not text:
            return False
        clean = cls._normalize_ar(text)
        if re.search(r'\d', clean):
            return False
        tokens = re.findall(r'[؀-ۿa-z]+', clean)
        if not tokens:
            return False
        meaningful = [t for t in tokens if t not in {'هو', 'هي', 'و', 'يكون', 'is', 'are', 'it', 'the', 'a'}]
        if not meaningful:
            return False
        return all(t in _NORMAL_WORDS for t in meaningful)

    @classmethod
    def _smart_normal_default(cls, field_name: str, text: str):
        """
        إذا كان النص يدل على 'طبيعي' فقط، أرجع القيمة السريرية الافتراضية للحقل.
        وإلا أرجع None لترك المنطق الأصلي يكمل عمله.
        """
        if cls._is_normal_only(text):
            return _NORMAL_DEFAULTS.get(field_name)
        return None
    
    def _init_medical_patterns(self) -> Dict:
        """
        تهيئة Regex Patterns لجميع الحقول الـ 11
        
        UNIFIED PATTERN STRUCTURE:
        كل حقل له مجموعة patterns تبحث عن:
        1. العربية والإنجليزية
        2. مع/بدون علامات ترقيم
        3. أشكال مختلفة للتعبير
        """
        return {
            # 1. Age (العمر)
            'age': [
                r'(?:عمر(?:ي)?|Age)\s*:?\s*(\d{1,3})\s*(?:سنة|year|yr)?',
                r'(\d{1,3})\s*(?:سنة|عام|year|years old)',
                r'أنا\s+(?:عمري)?\s*(\d{1,3})',
                r'I\s+am\s+(\d{1,3})\s*(?:years old)?',
            ],
            
            # 2. Sex (الجنس)
            'sex': [
                r'(?:جنس|الجنس|Sex|Gender)\s*:?\s*(ذكر|أنثى|Male|Female|M|F)',
                r'\b(ذكر|أنثى|رجل|امرأة|Male|Female)\b',
            ],
            
            # 3. ChestPain (ألم الصدر)
            'chest_pain': [
                r'(?:Chest\s+Pain|ألم\s+(?:في\s+)?الصدر)\s*:?\s*(TA|ATA|NAP|ASY|Typical|Atypical|Non-anginal|Asymptomatic)',
                r'\b(TA|ATA|NAP|ASY)\b',
            ],
            
            # 4. Blood Pressure (ضغط الدم)
            'blood_pressure': [
                r'(?:ضغط(?:\s+الدم)?|BP|Blood\s+Pressure)\s*:?\s*(\d{2,3})\s*/\s*(\d{2,3})',
                r'الضغط\s+(\d{2,3})\s+على\s+(\d{2,3})',
                r'(\d{2,3})\s*/\s*(\d{2,3})\s*(?:mmHg)?',
            ],
            
            # 5. Cholesterol (الكوليسترول)
            'cholesterol': [
                r'(?:كوليسترول|Cholesterol|Chol)\s*:?\s*(\d{2,3})',
                r'(?:Total\s+)?Cholesterol\s*:?\s*(\d{2,3})\s*(?:mg/dL)?',
                r'الكوليسترول\s+(\d{2,3})',
            ],
            
            # 6. FastingBS (سكر الدم الصائم)
            'fasting_blood_sugar': [
                r'(?:FBS|Fasting\s+BS|Fasting\s+Blood\s+Sugar)\s*:?\s*(\d{2,3})',
                r'سكر\s+(?:الصيام|الدم\s+صائم|صائم)\s*:?\s*(\d{2,3})',
                r'سكر\s*:?\s*(\d{2,3})',
            ],
            
            # 7. RestingECG (تخطيط القلب)
            'resting_ecg': [
                r'(?:Resting\s+ECG|تخطيط\s+القلب|ECG|رسم\s+القلب)\s*:?\s*(Normal|ST|LVH|طبيعي)',
                r'ECG\s*:?\s*(Normal|ST-T\s+wave|LVH)',
            ],
            
            # 8. MaxHR (معدل نبض القلب الأقصى)
            'max_heart_rate': [
                # English patterns
                r'(?:MaxHR|Max\s+HR)\s*:?\s*(\d{2,3})',
                r'Maximum\s+(?:Heart\s+Rate|HR)\s*:?\s*(\d{2,3})',
                r'Max(?:imum)?\s+Heart\s+Rate\s*:?\s*(\d{2,3})',
                r'Heart\s+rate\s*:?\s*(\d{2,3})',
                
                # Arabic patterns - معدل + نبض/القلب + الأقصى
                r'معدل\s+(?:القلب|النبض|نبض\s+القلب)\s+الأقصى\s*:?\s*(\d{2,3})',
                r'معدل\s+(?:القلب|النبض)\s*:?\s*(\d{2,3})',
                
                # Arabic patterns - أقصى + معدل/نبض
                r'(?:أقصى|أعلى)\s+(?:معدل|نبض|ضربات|نبضات)\s+(?:للقلب|القلب|قلب)\s*:?\s*(\d{2,3})',
                r'(?:أقصى|أعلى)\s+(?:نبض|معدل)\s*:?\s*(\d{2,3})',
                
                # Arabic patterns - نبض + generic
                r'(?:نبض(?:ات)?|ضربات)\s+(?:القلب|قلب)\s*(?:الأقصى|الأعلى)?\s*:?\s*(\d{2,3})',
            ],
            
            # 9. ExerciseAngina (ألم مع المجهود)
            'exercise_angina': [
                r'(?:Exercise\s+Angina|الذبحة\s+مع\s+التمرين)\s*:?\s*(Yes|No|Y|N|نعم|لا)',
            ],
            
            # 10. Oldpeak (انخفاض ST)
            'oldpeak': [
                r'(?:Oldpeak|ST\s+Depression|انخفاض\s+ST)\s*:?\s*(\d+\.?\d*)',
                r'^(\d+\.?\d*)$',  # Accept plain numbers like "2.5" or "1"
                r'(\d+\.?\d*)\s*(?:mm|ملم)?$',  # Accept numbers with optional unit
            ],
            
            # 11. ST_Slope (ميل ST)
            'st_slope': [
                r'(?:ST\s+Slope|ميل\s+ST|Slope)\s*:?\s*(Up|Flat|Down|صاعد|مسطح|هابط)',
            ],
        }
    
    def _init_medical_keywords(self) -> Dict:
        """
        تهيئة Keywords لجميع الحقول الـ 11
        
        UNIFIED KEYWORD STRUCTURE:
        كل حقل له keywords للبحث النصي عندما تفشل patterns
        """
        return {
            # 1. Age - لا يحتاج keywords (أرقام فقط)
            'age': {},
            
            # 2. Sex (الجنس)
            'sex': {
                'male': ['ذكر', 'رجل', 'male', 'm'],
                'female': ['أنثى', 'امرأة', 'female', 'f'],
            },
            
            # 3. ChestPain (ألم الصدر)
            'chest_pain': {
                'indicators': ['ألم', 'صدر', 'chest', 'pain', 'angina'],
                'TA': ['نموذجي', 'typical', 'angina'],
                'ATA': ['غير نموذجي', 'atypical'],
                'NAP': ['غير ذبحة', 'non-anginal'],
                'ASY': [
                    'بدون أعراض', 'asymptomatic', 'لا يوجد',
                    # Explicit denials / "I'm fine" phrasings
                    'لا ألم', 'ما عندي ألم', 'ما يوجعني', 'ما في ألم',
                    'صدري بخير', 'صدري طبيعي', 'لا أعاني', 'no pain',
                    'no chest pain', 'without pain', 'no symptoms',
                    'chest is normal', 'chest is fine', 'صدري سليم',
                ],
                # Standalone "normal/healthy" phrasings that imply ASY
                'normal_aliases': [
                    'طبيعي', 'عادي', 'سليم', 'بخير',
                    'normal', 'fine', 'healthy', 'ok'
                ],
            },
            
            # 4. BloodPressure - أرقام فقط
            'blood_pressure': {},
            
            # 5. Cholesterol - أرقام فقط
            'cholesterol': {},
            
            # 6. FastingBS (سكر الدم الصائم)
            'fasting_blood_sugar': {
                'indicators': ['سكر', 'fbs', 'fasting', 'صائم', 'الصيام', 'blood sugar'],
                'high': ['مرتفع', 'عالي', 'عالية', 'high', '> 120', '>120', 'أكثر من 120'],
                'normal': ['طبيعي', 'عادي', 'normal', '<= 120', '<=120', 'أقل من 120'],
            },
            
            # 7. RestingECG (تخطيط القلب)
            'resting_ecg': {
                'indicators': ['ecg', 'تخطيط', 'رسم', 'القلب'],
                'Normal': ['normal', 'طبيعي', 'عادي'],
                'ST': ['st-t', 'st wave', 'اضطراب', 'موجة'],
                'LVH': ['lvh', 'تضخم البطين', 'البطين الأيسر', 'left ventricular'],
            },
            
            # 8. MaxHR - أرقام فقط
            'max_heart_rate': {},
            
            # 9. ExerciseAngina (ألم مع المجهود)
            'exercise_angina': {
                'indicators': [
                    'exercise angina', 'الذبحة مع التمرين', 'ذبحة مجهود',
                    'ألم عند المجهود', 'ألم مع المجهود', 'ألم عند الرياضة',
                    'ألم مع الرياضة', 'ألم مع النشاط', 'ألم عند النشاط'
                ],
                'yes': ['yes', 'نعم', 'موجود', 'y', 'يوجد', 'أعاني'],
                'no': ['لا يوجد', 'لا أعاني', 'لا توجد', 'no', 'n'],
            },
            
            # 10. Oldpeak - أرقام فقط
            'oldpeak': {},
            
            # 11. ST_Slope (ميل ST)
            'st_slope': {
                'Up': ['up', 'صاعد'],
                'Flat': ['flat', 'مسطح'],
                'Down': ['down', 'هابط', 'منحدر'],
            },
        }
    
    def extract_entities(self, text: str) -> Dict[str, any]:
        """
        استخراج جميع الحقول الـ 11 باستخدام استراتيجية موحدة
        
        UNIFIED EXTRACTION STRATEGY:
        كل حقل يتبع نفس الاستراتيجية:
        1. استدعاء extraction method الخاص به
        2. if value is not None: → تخزين
        
        Args:
            text: النص المُدخل
            
        Returns:
            dict: جميع الحقول المُستخرجة
        """
        entities = {}
        
        # 1. Age (العمر)
        age = self._extract_age(text)
        if age is not None:
            entities['Age'] = age
        
        # 2. Sex (الجنس)
        sex = self._extract_sex(text)
        if sex is not None:
            entities['Sex'] = sex
        
        # 3. ChestPain (ألم الصدر)
        chest_pain = self._extract_chest_pain(text)
        if chest_pain is not None:
            entities['ChestPain'] = chest_pain
        
        # 4. BloodPressure (ضغط الدم)
        bp = self._extract_blood_pressure(text)
        if bp is not None:
            entities['BloodPressure'] = bp
        
        # 5. Cholesterol (الكوليسترول)
        chol = self._extract_cholesterol(text)
        if chol is not None:
            entities['Cholesterol'] = chol
        
        # 6. FastingBS (سكر الدم الصائم)
        fbs = self._extract_fasting_blood_sugar(text)
        if fbs is not None:
            entities['FastingBS'] = fbs
        
        # 7. RestingECG (تخطيط القلب)
        resting_ecg = self._extract_resting_ecg(text)
        if resting_ecg is not None:
            entities['RestingECG'] = resting_ecg
        
        # 8. MaxHR (معدل نبض القلب الأقصى)
        max_hr = self._extract_max_heart_rate(text)
        if max_hr is not None:
            entities['MaxHR'] = max_hr
        
        # 9. ExerciseAngina (ألم مع المجهود)
        ex_angina = self._extract_exercise_angina(text)
        if ex_angina is not None:
            entities['ExerciseAngina'] = ex_angina
        
        # 10. Oldpeak (انخفاض ST)
        oldpeak = self._extract_oldpeak(text)
        if oldpeak is not None:
            entities['Oldpeak'] = oldpeak
        
        # 11. ST_Slope (ميل ST)
        st_slope = self._extract_st_slope(text)
        if st_slope is not None:
            entities['ST_Slope'] = st_slope
        
        logger.info(f"Extracted {len(entities)}/11 entities from text")
        return entities
    
    # ========================================
    # EXTRACTION METHODS - UNIFIED STRATEGY
    # جميع Methods تتبع نفس الاستراتيجية:
    # 1. Try Regex Patterns
    # 2. Try Keyword Matching
    # 3. Normalize Value
    # ========================================
    
    def _extract_age(self, text: str) -> Optional[int]:
        """
        استخراج العمر (Age)
        
        Strategy:
        1. Try regex patterns
        2. Validate range (1-120)
        3. Return int
        """
        for pattern in self.medical_patterns['age']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                age = int(match.group(1))
                if 1 <= age <= 120:
                    return age
        return None
    
    def _extract_sex(self, text: str) -> Optional[str]:
        """
        استخراج الجنس (Sex)
        
        Strategy:
        1. Try regex patterns
        2. Try keyword matching
        3. Normalize to Male/Female
        """
        # Step 1: Try regex patterns
        for pattern in self.medical_patterns['sex']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).lower()
                # Normalize
                if value in ['ذكر', 'رجل', 'male', 'm']:
                    return 'Male'
                elif value in ['أنثى', 'امرأة', 'female', 'f']:
                    return 'Female'
        
        # Step 2: Keyword matching
        text_lower = text.lower()
        if any(keyword in text_lower for keyword in self.medical_keywords['sex']['male']):
            return 'Male'
        elif any(keyword in text_lower for keyword in self.medical_keywords['sex']['female']):
            return 'Female'
        
        return None
    
    def _extract_chest_pain(self, text: str) -> Optional[str]:
        """
        استخراج ألم الصدر (ChestPain)
        
        Strategy:
        1. Try regex patterns for codes (TA/ATA/NAP/ASY)
        2. Try keyword matching for descriptions
        3. Normalize to TA/ATA/NAP/ASY
        """
        # Step 1: Try regex patterns
        for pattern in self.medical_patterns['chest_pain']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).upper()
                # Normalize
                if 'TYPICAL' in value or value == 'TA':
                    return 'TA'
                elif 'ATYPICAL' in value or value == 'ATA':
                    return 'ATA'
                elif 'NON' in value or value == 'NAP':
                    return 'NAP'
                elif 'ASYMPTOMATIC' in value or value == 'ASY':
                    return 'ASY'
        
        # Step 2: Keyword matching
        text_lower = text.lower()
        cp = self.medical_keywords['chest_pain']

        # Step 2a — explicit ASY phrasings ("no chest pain", "صدري بخير")
        # take precedence: a denial is informative even without the word
        # "chest pain" itself.
        if any(kw in text_lower for kw in cp['ASY']):
            return 'ASY'

        # Step 2b — chest-pain mentioned: pick the most specific subtype.
        has_chest_pain = any(kw in text_lower for kw in cp['indicators'])
        if has_chest_pain:
            if any(kw in text_lower for kw in cp['TA']):
                return 'TA'
            elif any(kw in text_lower for kw in cp['ATA']):
                return 'ATA'
            elif any(kw in text_lower for kw in cp['NAP']):
                return 'NAP'
            elif any(kw in text_lower for kw in cp['ASY']):
                return 'ASY'
            # If only "chest pain" is mentioned without a subtype keyword
            # but the patient also says "طبيعي / normal / fine", treat as
            # asymptomatic instead of defaulting to TA.
            elif any(kw in text_lower for kw in cp['normal_aliases']):
                return 'ASY'
            else:
                # Plain "chest pain" with no qualifier — assume typical angina
                return 'TA'

        # Step 3: Smart normal handler — "طبيعي" alone → ASY (no chest pain)
        smart = self._smart_normal_default('ChestPain', text)
        if smart is not None:
            return smart

        return None

    # Sentence-level "the patient said the value is normal/healthy" helper.
    # Returns True if `text` contains a feature-naming keyword AND a
    # normal/healthy keyword. Used for phrasings like "ضغطي طبيعي".
    _NORMAL_KEYWORDS = (
        'طبيعي', 'عادي', 'سليم', 'بخير', 'مظبوط', 'مضبوط',
        'normal', 'fine', 'healthy', 'ok'
    )

    def _mentions_normal(self, text: str, feature_keywords) -> bool:
        text_lower = text.lower()
        if not any(kw in text_lower for kw in feature_keywords):
            return False
        return any(kw in text_lower for kw in self._NORMAL_KEYWORDS)

    def _extract_blood_pressure(self, text: str) -> Optional[str]:
        """
        Extract blood pressure (BloodPressure).
        Strategy:
        1. Numeric "XXX/YYY".
        2. "ضغطي طبيعي / normal blood pressure" → clinical normal 120/80.
        """
        for pattern in self.medical_patterns['blood_pressure']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                systolic = int(match.group(1))
                diastolic = int(match.group(2))
                if 80 <= systolic <= 200 and 40 <= diastolic <= 130:
                    return f"{systolic}/{diastolic}"

        # Sentence-level: "ضغطي طبيعي / normal blood pressure" → 120/80
        if self._mentions_normal(text, ['ضغط', 'bp', 'blood pressure', 'الضغط']):
            return "120/80"

        # Standalone: "طبيعي" alone → 120/80
        smart = self._smart_normal_default('BloodPressure', text)
        if smart is not None:
            return smart

        return None
    
    def _extract_cholesterol(self, text: str) -> Optional[int]:
        """
        استخراج الكوليسترول (Cholesterol)
        
        Strategy:
        1. Try regex patterns
        2. Validate range (100-600)
        3. Return int
        """
        for pattern in self.medical_patterns['cholesterol']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                chol = int(match.group(1))
                if 100 <= chol <= 600:
                    return chol

        # Sentence-level: "كوليسترولي طبيعي" → 180 mg/dL
        if self._mentions_normal(text, ['كوليسترول', 'cholesterol', 'chol']):
            return 180

        # Standalone: "طبيعي" alone → 180 mg/dL
        smart = self._smart_normal_default('Cholesterol', text)
        if smart is not None:
            return smart

        return None

    def _extract_fasting_blood_sugar(self, text: str) -> Optional[int]:
        """
        استخراج سكر الدم الصائم (FastingBS)
        
        Strategy:
        1. Try regex patterns for numbers
        2. Try keyword matching for descriptions (high/normal)
        3. Normalize to 0 (≤120) or 1 (>120)
        """
        text_lower = text.lower()
        
        # Step 1: Try regex patterns for numbers
        for pattern in self.medical_patterns['fasting_blood_sugar']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fbs = int(match.group(1))
                # Normalize to binary: >120 = 1, <=120 = 0
                return 1 if fbs > 120 else 0
        
        # Step 2: Keyword matching for descriptions
        has_indicator = any(kw in text_lower for kw in self.medical_keywords['fasting_blood_sugar']['indicators'])
        
        if has_indicator:
            # Check for "high"
            if any(kw in text_lower for kw in self.medical_keywords['fasting_blood_sugar']['high']):
                return 1
            # Check for "normal"
            elif any(kw in text_lower for kw in self.medical_keywords['fasting_blood_sugar']['normal']):
                return 0

        # Smart normal handler — "طبيعي" alone → 0
        smart = self._smart_normal_default('FastingBS', text)
        if smart is not None:
            return smart

        return None

    def _extract_resting_ecg(self, text: str) -> Optional[str]:
        """
        استخراج تخطيط القلب (RestingECG)
        
        Strategy:
        1. Try regex patterns
        2. Try keyword matching
        3. Normalize to Normal/ST/LVH
        """
        text_lower = text.lower()
        
        # Step 1: Try regex patterns
        for pattern in self.medical_patterns['resting_ecg']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).upper()
                if 'NORMAL' in value or 'طبيعي' in value.lower():
                    return 'Normal'
                elif 'ST' in value:
                    return 'ST'
                elif 'LVH' in value:
                    return 'LVH'
        
        # Step 2: Keyword matching
        # Check for LVH first (most specific - لا يحتاج indicator)
        if any(kw in text_lower for kw in self.medical_keywords['resting_ecg']['LVH']):
            return 'LVH'
        
        # For Normal and ST, check if ECG indicator exists
        has_indicator = any(kw in text_lower for kw in self.medical_keywords['resting_ecg']['indicators'])
        
        if has_indicator:
            # Check for ST
            if any(kw in text_lower for kw in self.medical_keywords['resting_ecg']['ST']):
                return 'ST'
            # Check for Normal
            elif any(kw in text_lower for kw in self.medical_keywords['resting_ecg']['Normal']):
                return 'Normal'

        # Smart normal handler — "طبيعي" alone → Normal
        smart = self._smart_normal_default('RestingECG', text)
        if smart is not None:
            return smart

        return None

    def _extract_max_heart_rate(self, text: str) -> Optional[int]:
        """
        استخراج معدل نبض القلب الأقصى (MaxHR)
        
        Strategy:
        1. Try regex patterns
        2. Validate range (60-220)
        3. Return int
        """
        for pattern in self.medical_patterns['max_heart_rate']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                hr = int(match.group(1))
                if 60 <= hr <= 220:
                    return hr

        # Sentence-level: "نبضي طبيعي / normal heart rate" → 150 bpm
        if self._mentions_normal(
            text,
            ['نبض', 'القلب', 'heart rate', 'max hr', 'maxhr', 'ضربات', 'pulse'],
        ):
            return 150

        # Standalone: "طبيعي" alone → 150 bpm
        smart = self._smart_normal_default('MaxHR', text)
        if smart is not None:
            return smart

        return None

    def _extract_exercise_angina(self, text: str) -> Optional[str]:
        """
        استخراج ألم مع المجهود (ExerciseAngina)
        
        Strategy:
        1. Try regex patterns
        2. Try keyword matching
        3. Normalize to Y/N
        """
        text_lower = text.lower()
        
        # Step 1: Try regex patterns
        for pattern in self.medical_patterns['exercise_angina']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).lower()
                if value in ['yes', 'y', 'نعم']:
                    return 'Y'
                elif value in ['no', 'n', 'لا']:
                    return 'N'
        
        # Step 2: Keyword matching
        has_indicator = any(kw in text_lower for kw in self.medical_keywords['exercise_angina']['indicators'])
        
        if has_indicator:
            # Check for "no" first (more specific - لا يوجد)
            if any(kw in text_lower for kw in self.medical_keywords['exercise_angina']['no']):
                return 'N'
            # Check for "yes"
            elif any(kw in text_lower for kw in self.medical_keywords['exercise_angina']['yes']):
                return 'Y'
            # Default if only indicator found
            else:
                return 'Y'

        # Smart normal handler — "طبيعي" → N (no exercise-induced angina)
        smart = self._smart_normal_default('ExerciseAngina', text)
        if smart is not None:
            return smart

        return None

    def _extract_oldpeak(self, text: str) -> Optional[float]:
        """
        استخراج انخفاض ST (Oldpeak)
        
        Strategy:
        1. Try regex patterns
        2. Validate range (0.0-10.0)
        3. Return float
        """
        for pattern in self.medical_patterns['oldpeak']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                oldpeak = float(match.group(1))
                if 0.0 <= oldpeak <= 10.0:
                    return oldpeak

        # Sentence-level: "ST طبيعي / normal ST depression" → 0.0
        if self._mentions_normal(text, ['st', 'oldpeak', 'انخفاض', 'depression']):
            return 0.0

        # Standalone: "طبيعي" alone → 0.0 mm
        smart = self._smart_normal_default('Oldpeak', text)
        if smart is not None:
            return smart

        return None
    
    def _extract_st_slope(self, text: str) -> Optional[str]:
        """
        استخراج ميل ST (ST_Slope)
        
        Strategy:
        1. Try regex patterns
        2. Try keyword matching
        3. Normalize to Up/Flat/Down
        """
        text_lower = text.lower()
        
        # Step 1: Try regex patterns
        for pattern in self.medical_patterns['st_slope']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).lower()
                if 'up' in value or 'صاعد' in value:
                    return 'Up'
                elif 'flat' in value or 'مسطح' in value:
                    return 'Flat'
                elif 'down' in value or 'هابط' in value or 'منحدر' in value:
                    return 'Down'
        
        # Step 2: Keyword matching
        if any(kw in text_lower for kw in self.medical_keywords['st_slope']['Up']):
            return 'Up'
        elif any(kw in text_lower for kw in self.medical_keywords['st_slope']['Flat']):
            return 'Flat'
        elif any(kw in text_lower for kw in self.medical_keywords['st_slope']['Down']):
            return 'Down'

        # Smart normal handler — "طبيعي" → Up (healthy slope)
        smart = self._smart_normal_default('ST_Slope', text)
        if smart is not None:
            return smart

        return None
    
    def get_entity_confidence(self, entity_name: str, entity_value: any) -> float:
        """
        حساب ثقة الاستخراج (confidence score)
        
        Args:
            entity_name: اسم المعلومة
            entity_value: قيمة المعلومة
            
        Returns:
            نسبة الثقة (0.0 - 1.0)
        """
        # نسبة الثقة الافتراضية
        base_confidence = 0.85
        
        # رفع الثقة للحقول ذات القيم الرقمية الدقيقة
        if entity_name in ['Age', 'Cholesterol', 'MaxHR', 'Oldpeak']:
            return 0.95
        
        # رفع الثقة لضغط الدم (نمط واضح)
        if entity_name == 'BloodPressure' and '/' in str(entity_value):
            return 0.95
        
        return base_confidence
