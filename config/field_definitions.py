"""
تعريفات الحقول الطبية الموحدة
Unified Medical Field Definitions

هذا الملف هو المرجع الوحيد لأسماء الحقول في كل المشروع.
All modules MUST import field names from here — never hardcode them.
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple


# ═══════════════════════════════════════════════════════════════════════════
# ACC/AHA 2019 Cardiovascular Risk Stratification Thresholds
# Reference: Arnett DK et al., 2019 ACC/AHA Guideline on the Primary
# Prevention of Cardiovascular Disease. Circulation 2019;140(11):e596–e646.
# doi:10.1161/CIR.0000000000000678
# ═══════════════════════════════════════════════════════════════════════════
ACC_AHA_THRESHOLD_MODERATE = 0.05   # 5%   — borderline risk
ACC_AHA_THRESHOLD_HIGH = 0.075      # 7.5% — intermediate-to-high risk
ACC_AHA_THRESHOLD_CRITICAL = 0.20   # 20%  — very high / critical risk


# ═══════════════════════════════════════════════════════════════════════════
# مستويات الخطر الموحدة — تُستخدم في كل الموديولات
# ═══════════════════════════════════════════════════════════════════════════

class RiskLevel(Enum):
    """
    Cardiovascular risk stratification — unified across all system components.

    Thresholds follow the 2019 ACC/AHA Primary Prevention Guideline [1]
    and the 2018 AHA/ACC Cholesterol Management Guideline [2]:

        Low         : prob < 5%       → no/very low CVD risk
        Moderate    : 5%  ≤ prob < 7.5% → borderline risk
        High        : 7.5% ≤ prob < 20% → intermediate-to-high risk
        Critical    : prob ≥ 20%      → very high / established CVD risk

    References
    ----------
    [1] Arnett DK, Blumenthal RS, Albert MA, et al. 2019 ACC/AHA Guideline
        on the Primary Prevention of Cardiovascular Disease. Circulation.
        2019;140(11):e596–e646. doi:10.1161/CIR.0000000000000678
    [2] Grundy SM, Stone NJ, Bailey AL, et al. 2018 AHA/ACC Cholesterol
        Management Guideline. Circulation. 2019;139(25):e1082–e1143.
        doi:10.1161/CIR.0000000000000625
    """

    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    @classmethod
    def from_probability(cls, prob: float) -> "RiskLevel":
        """Map a model probability to a clinical risk category per ACC/AHA 2019."""
        if prob >= ACC_AHA_THRESHOLD_CRITICAL:   # ≥20% → very high / critical
            return cls.CRITICAL
        elif prob >= ACC_AHA_THRESHOLD_HIGH:     # 7.5%–<20% → intermediate-to-high
            return cls.HIGH
        elif prob >= ACC_AHA_THRESHOLD_MODERATE: # 5%–<7.5% → borderline / moderate
            return cls.MODERATE
        return cls.LOW                           # <5% → low risk

    @classmethod
    def from_domain_label(cls, label: str) -> "RiskLevel":
        """تحويل من تسميات Domain Rules (Low/Medium/High) إلى RiskLevel"""
        mapping = {
            "low": cls.LOW,
            "medium": cls.MODERATE,
            "high": cls.HIGH,
            "critical": cls.CRITICAL,
        }
        return mapping.get(label.lower(), cls.LOW)

    def to_arabic(self) -> str:
        return {
            "LOW": "منخفض",
            "MODERATE": "متوسط",
            "HIGH": "عالي",
            "CRITICAL": "حرج",
        }[self.value]

    def to_numeric(self) -> float:
        """قيمة رقمية للمقارنات"""
        return {"LOW": 0.25, "MODERATE": 0.5, "HIGH": 0.75, "CRITICAL": 1.0}[
            self.value
        ]


# ═══════════════════════════════════════════════════════════════════════════
# أسماء الحقول — الطبقة الداخلية vs طبقة النموذج
# ═══════════════════════════════════════════════════════════════════════════

# الأسماء المختصرة المستخدمة داخلياً (NER, domain rules, chatbot, UI)
INTERNAL_FIELDS: List[str] = [
    "Age",
    "Sex",
    "ChestPain",
    "BloodPressure",
    "Cholesterol",
    "FastingBS",
    "RestingECG",
    "MaxHR",
    "ExerciseAngina",
    "Oldpeak",
    "ST_Slope",
]

# الأسماء الكاملة التي يتوقعها نموذج ML (تطابق الـ 11 حقل التي يدخلها المريض)
# ملاحظة: نموذج Keras الأصلي مُدرَّب على 12 ميزة (يتضمن NumberOfVesselsColored
# من فحص القسطرة) ويحقن advanced_features.py القيمة الافتراضية تلقائياً.
MODEL_FIELDS: List[str] = [
    "Age",
    "Sex",
    "ChestPainType",
    "RestingBloodPressure",
    "Cholesterol",
    "FastingBloodSugar",
    "RestingECG",
    "MaxHeartRate",
    "ExerciseInducedAngina",
    "OldPeak",
    "PeakExerciseSTSegmentSlope",
]

# ربط الأسماء الداخلية بأسماء النموذج
INTERNAL_TO_MODEL: Dict[str, str] = {
    "Age": "Age",
    "Sex": "Sex",
    "ChestPain": "ChestPainType",
    "BloodPressure": "RestingBloodPressure",
    "Cholesterol": "Cholesterol",
    "FastingBS": "FastingBloodSugar",
    "RestingECG": "RestingECG",
    "MaxHR": "MaxHeartRate",
    "ExerciseAngina": "ExerciseInducedAngina",
    "Oldpeak": "OldPeak",
    "ST_Slope": "PeakExerciseSTSegmentSlope",
}

MODEL_TO_INTERNAL: Dict[str, str] = {v: k for k, v in INTERNAL_TO_MODEL.items()}


def to_model_name(internal_name: str) -> str:
    """تحويل اسم داخلي إلى اسم النموذج"""
    return INTERNAL_TO_MODEL.get(internal_name, internal_name)


def to_internal_name(model_name: str) -> str:
    """تحويل اسم النموذج إلى اسم داخلي"""
    return MODEL_TO_INTERNAL.get(model_name, model_name)


def convert_facts_to_model(facts: Dict) -> Dict:
    """تحويل facts dict من الأسماء الداخلية إلى أسماء النموذج"""
    return {INTERNAL_TO_MODEL.get(k, k): v for k, v in facts.items()}


def convert_facts_to_internal(facts: Dict) -> Dict:
    """تحويل facts dict من أسماء النموذج إلى الأسماء الداخلية"""
    return {MODEL_TO_INTERNAL.get(k, k): v for k, v in facts.items()}


# ═══════════════════════════════════════════════════════════════════════════
# الثوابت الطبية — مكان واحد لكل العتبات
# ═══════════════════════════════════════════════════════════════════════════

MEDICAL_THRESHOLDS = {
    # العمر
    "age_very_young": 30,
    "age_young": 40,
    "age_middle": 50,
    "age_senior": 60,
    "age_elderly": 70,
    # الكولسترول (mg/dL)
    "cholesterol_optimal": 200,
    "cholesterol_borderline": 240,
    "cholesterol_high": 300,
    # ضغط الدم الانقباضي (mmHg)
    "bp_normal": 120,
    "bp_elevated": 130,
    "bp_stage1": 140,
    "bp_stage2": 180,
    # معدل نبض القلب
    "hr_poor": 100,
    "hr_fair": 130,
    "hr_good": 160,
    # ST Depression
    "st_mild": 1.0,
    "st_moderate": 2.0,
    "st_severe": 3.0,
}

# ═══════════════════════════════════════════════════════════════════════════
# نطاقات القيم المقبولة
# ═══════════════════════════════════════════════════════════════════════════

VALUE_RANGES: Dict[str, Tuple[float, float]] = {
    "Age": (0, 150),
    "BloodPressure": (60, 250),
    "Cholesterol": (50, 600),
    "MaxHR": (30, 250),
    "Oldpeak": (0, 10),
    "FastingBS": (0, 1),
}


def validate_numeric_field(field_name: str, value) -> Optional[float]:
    """التحقق من القيمة الرقمية ضمن النطاق المقبول.
    يرجع القيمة إذا صحيحة، None إذا خارج النطاق أو غير رقمية.
    """
    if field_name not in VALUE_RANGES:
        return None
    try:
        num = float(value)
    except (ValueError, TypeError):
        return None
    lo, hi = VALUE_RANGES[field_name]
    if lo <= num <= hi:
        return num
    return None
