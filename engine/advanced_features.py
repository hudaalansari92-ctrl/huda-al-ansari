
import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class AdvancedFeaturesGenerator:
    """
    توليد features متقدمة من الحقول الأساسية
    
    Features المولّدة:
    - Age-based features (5 categories + risk score)
    - Cholesterol-based features (4 levels)
    - Blood pressure features (5 stages)
    - Heart rate features (exercise capacity, reserves)
    - Gender-based risk features
    - ST segment features
    - Metabolic syndrome indicators
    - Framingham risk score
    - Interaction features (age×cholesterol, etc.)
    - Chest pain severity
    - ECG abnormality indicators
    
    Total: ~40 features متقدمة
    """
    
    def __init__(self):
        """تهيئة المولّد"""
        self.feature_names = []
        logger.info("AdvancedFeaturesGenerator initialized")
    
    def generate(self, facts: Dict) -> pd.DataFrame:
        """
        توليد جميع الـ features المتقدمة (58 features للموديل)
        
        Features structure:
        - 12 Base features (raw inputs)
        - 41 Advanced features (calculated)
        - 6 Frequency features (categorical encoding)
        = 58 Total features
        
        Args:
            facts: الحقول الـ 11 الأساسية
            
        Returns:
            DataFrame يحتوي على 58 features بالترتيب الصحيح
        """
        logger.info("Generating 58 features for ML model...")
        
        # تحويل facts إلى DataFrame
        df = self._facts_to_dataframe(facts)
        
        # إنشاء DataFrame للـ features بالترتيب الصحيح
        domain_df = pd.DataFrame(index=df.index)
        
        # ============================================================
        # PART 1: Base Features (12 features)
        # ============================================================
        
        # استخراج القيم الأساسية
        age = pd.to_numeric(df['Age'], errors='coerce')
        cholesterol = pd.to_numeric(df['Cholesterol'], errors='coerce')
        resting_bp = pd.to_numeric(df['BloodPressure'].str.split('/').str[0], errors='coerce')
        max_hr = pd.to_numeric(df['MaxHR'], errors='coerce')
        old_peak = pd.to_numeric(df['Oldpeak'], errors='coerce')
        
        # Base features (في نفس ترتيب feature_names.json)
        domain_df['Age'] = age
        
        # Sex encoding: Male=1, Female=0
        domain_df['Sex'] = (df['Sex'] == 'Male').astype(int)
        
        # ChestPainType encoding: TA=3, ASY=2, NAP=1, ATA=0
        chest_pain_map = {'TA': 3, 'ASY': 2, 'NAP': 1, 'ATA': 0}
        domain_df['ChestPainType'] = df['ChestPain'].map(chest_pain_map).fillna(0)
        
        domain_df['RestingBloodPressure'] = resting_bp
        domain_df['Cholesterol'] = cholesterol
        
        # FastingBloodSugar: already 0/1
        domain_df['FastingBloodSugar'] = pd.to_numeric(df['FastingBS'], errors='coerce')
        
        # RestingECG encoding: ST=2, LVH=1, Normal=0
        ecg_map = {'ST': 2, 'LVH': 1, 'Normal': 0}
        domain_df['RestingECG'] = df['RestingECG'].map(ecg_map).fillna(0)
        
        domain_df['MaxHeartRate'] = max_hr
        
        # ExerciseInducedAngina: Y=1, N=0
        domain_df['ExerciseInducedAngina'] = (df['ExerciseAngina'] == 'Y').astype(int)
        
        domain_df['OldPeak'] = old_peak
        
        # PeakExerciseSTSegmentSlope encoding: Flat=2, Down=1, Up=0
        slope_map = {'Flat': 2, 'Down': 1, 'Up': 0}
        domain_df['PeakExerciseSTSegmentSlope'] = df['ST_Slope'].map(slope_map).fillna(2)
        
        # NumberOfVesselsColored: ميزة قسطرة قلبية (Angiography) غير متاحة في
        # محادثة المريض، لذا تُحقن بقيمة افتراضية 0 للحفاظ على توافق المدخلات
        # مع نموذج Keras الأصلي (تم تدريبه على 12 ميزة).
        domain_df['NumberOfVesselsColored'] = 0
        
        # ============================================================
        # PART 2: Advanced Features (41 features)
        # ============================================================
        
        # 1. Age-based Features
        domain_df['age_very_young'] = (age < 30).astype(int)
        domain_df['age_young'] = ((age >= 30) & (age < 45)).astype(int)
        domain_df['age_middle'] = ((age >= 45) & (age < 60)).astype(int)
        domain_df['age_senior'] = ((age >= 60) & (age < 75)).astype(int)
        domain_df['age_elderly'] = (age >= 75).astype(int)
        domain_df['age_risk_score'] = np.where(age < 45, 0,
                                              np.where(age < 55, 1,
                                                      np.where(age < 65, 2, 3)))
        
        # 2. Cholesterol-based Features
        domain_df['cholesterol_optimal'] = (cholesterol < 200).astype(int)
        domain_df['cholesterol_borderline'] = ((cholesterol >= 200) & (cholesterol < 240)).astype(int)
        domain_df['cholesterol_high'] = (cholesterol >= 240).astype(int)
        domain_df['cholesterol_very_high'] = (cholesterol >= 300).astype(int)
        
        # 3. Blood Pressure Features
        domain_df['bp_normal'] = (resting_bp < 120).astype(int)
        domain_df['bp_elevated'] = ((resting_bp >= 120) & (resting_bp < 130)).astype(int)
        domain_df['bp_stage1'] = ((resting_bp >= 130) & (resting_bp < 140)).astype(int)
        domain_df['bp_stage2'] = (resting_bp >= 140).astype(int)
        domain_df['bp_crisis'] = (resting_bp >= 180).astype(int)
        
        # 4. Heart Rate Features
        predicted_max_hr = 220 - age
        hr_reserve = max_hr - (220 - age) * 0.6
        hr_reserve_ratio = max_hr / predicted_max_hr
        
        domain_df['predicted_max_hr'] = predicted_max_hr
        domain_df['hr_reserve_ratio'] = hr_reserve_ratio.fillna(0)
        domain_df['hr_reserve'] = hr_reserve.fillna(0)
        domain_df['exercise_poor'] = (hr_reserve_ratio < 0.6).astype(int)
        domain_df['exercise_fair'] = ((hr_reserve_ratio >= 0.6) & (hr_reserve_ratio < 0.8)).astype(int)
        domain_df['exercise_good'] = ((hr_reserve_ratio >= 0.8) & (hr_reserve_ratio < 0.9)).astype(int)
        domain_df['exercise_excellent'] = (hr_reserve_ratio >= 0.9).astype(int)
        
        # 5. Gender-based Risk Features
        domain_df['male_high_risk'] = ((df['Sex'] == 'Male') & (age >= 45)).astype(int)
        domain_df['female_high_risk'] = ((df['Sex'] == 'Female') & (age >= 55)).astype(int)
        domain_df['female_postmenopausal'] = ((df['Sex'] == 'Female') & (age >= 51)).astype(int)
        
        # 6. ST Segment Features
        domain_df['st_normal'] = (old_peak <= 0).astype(int)
        domain_df['st_mild'] = ((old_peak > 0) & (old_peak <= 1.0)).astype(int)
        domain_df['st_moderate'] = ((old_peak > 1.0) & (old_peak <= 2.0)).astype(int)
        domain_df['st_severe'] = (old_peak > 2.0).astype(int)
        
        # 7. Metabolic Syndrome Indicators
        domain_df['metabolic_bp'] = (resting_bp >= 130).astype(int)
        domain_df['metabolic_glucose'] = (df['FastingBS'] == 1).astype(int)
        
        # 8. Framingham Risk Score
        framingham_factors = [
            (df['Sex'] == 'Male').astype(int),
            (age >= 45).astype(int),
            (cholesterol >= 240).astype(int),
            (resting_bp >= 140).astype(int),
            (df['FastingBS'] == 1).astype(int),
            (df['ExerciseAngina'] == 'Y').astype(int),
            (old_peak > 1.0).astype(int)
        ]
        
        domain_df['framingham_risk_score'] = sum(framingham_factors)
        domain_df['high_risk_profile'] = (domain_df['framingham_risk_score'] >= 3).astype(int)
        
        # 9. Interaction Features
        domain_df['age_cholesterol_norm'] = (age * cholesterol) / (100 * 300)
        domain_df['age_bp_norm'] = (age * resting_bp) / (100 * 200)
        domain_df['cholesterol_bp_norm'] = (cholesterol * resting_bp) / (300 * 200)
        
        # 10. Chest Pain Severity
        domain_df['chest_pain_severity'] = domain_df['ChestPainType']  # Already encoded 0-3
        domain_df['typical_angina'] = (df['ChestPain'] == 'TA').astype(int)
        domain_df['asymptomatic'] = (df['ChestPain'] == 'ASY').astype(int)
        
        # 11. ECG Analysis (2 features only - NOT ecg_st to match 41 total)
        domain_df['ecg_abnormal'] = (domain_df['RestingECG'] > 0).astype(int)
        domain_df['ecg_lvh'] = (domain_df['RestingECG'] == 1).astype(int)
        
        # ============================================================
        # PART 3: Frequency Features (6 features)
        # ============================================================
        # These are frequency encoding for categorical variables
        # We'll use simple frequency based on common distributions
        
        # Sex_frequency
        sex_freq = {'Male': 0.6, 'Female': 0.4}
        domain_df['Sex_frequency'] = df['Sex'].map(sex_freq).fillna(0.5)
        
        # ChestPainType_frequency
        chest_freq = {'TA': 0.30, 'ASY': 0.40, 'NAP': 0.20, 'ATA': 0.10}
        domain_df['ChestPainType_frequency'] = df['ChestPain'].map(chest_freq).fillna(0.25)
        
        # FastingBloodSugar_frequency
        fbs_freq = {0: 0.7, 1: 0.3}
        domain_df['FastingBloodSugar_frequency'] = df['FastingBS'].map(fbs_freq).fillna(0.5)
        
        # RestingECG_frequency
        ecg_freq = {'Normal': 0.60, 'ST': 0.25, 'LVH': 0.15}
        domain_df['RestingECG_frequency'] = df['RestingECG'].map(ecg_freq).fillna(0.33)
        
        # ExerciseInducedAngina_frequency
        angina_freq = {'N': 0.6, 'Y': 0.4}
        domain_df['ExerciseInducedAngina_frequency'] = df['ExerciseAngina'].map(angina_freq).fillna(0.5)
        
        # PeakExerciseSTSegmentSlope_frequency
        slope_freq = {'Flat': 0.50, 'Up': 0.30, 'Down': 0.20}
        domain_df['PeakExerciseSTSegmentSlope_frequency'] = df['ST_Slope'].map(slope_freq).fillna(0.33)
        
        # Fill any remaining NaN values
        domain_df = domain_df.fillna(0)
        
        # إعادة ترتيب الأعمدة بنفس ترتيب feature_names.json
        expected_order = self._get_expected_feature_order()
        if expected_order:
            missing = set(expected_order) - set(domain_df.columns)
            extra = set(domain_df.columns) - set(expected_order)
            if missing:
                logger.warning(f"Missing features: {missing}")
                for col in missing:
                    domain_df[col] = 0
            if extra:
                logger.warning(f"Extra features (will be dropped): {extra}")
            domain_df = domain_df[expected_order]

        # حفظ أسماء الـ features
        self.feature_names = list(domain_df.columns)

        logger.info(f"Generated {len(self.feature_names)} features (expected 59)")

        if len(self.feature_names) != 59:
            logger.warning(f"Feature count mismatch! Generated {len(self.feature_names)}, expected 59")

        return domain_df

    @staticmethod
    def _get_expected_feature_order():
        """قراءة ترتيب الميزات المتوقع من ملف النموذج"""
        import os, json
        path = os.path.join(os.path.dirname(__file__), '..', 'models', '1768892326033_feature_names.json')
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def _facts_to_dataframe(self, facts: Dict) -> pd.DataFrame:
        """
        تحويل facts dictionary إلى DataFrame
        
        Args:
            facts: الحقول الـ 11
            
        Returns:
            DataFrame بصف واحد
        """
        # إنشاء dictionary بالقيم
        data = {
            'Age': facts.get('Age', 50),
            'Sex': facts.get('Sex', 'Male'),
            'ChestPain': facts.get('ChestPain', 'ATA'),
            'BloodPressure': facts.get('BloodPressure', '120/80'),
            'Cholesterol': facts.get('Cholesterol', 200),
            'FastingBS': facts.get('FastingBS', 0),
            'RestingECG': facts.get('RestingECG', 'Normal'),
            'MaxHR': facts.get('MaxHR', 150),
            'ExerciseAngina': facts.get('ExerciseAngina', 'N'),
            'Oldpeak': facts.get('Oldpeak', 0.0),
            'ST_Slope': facts.get('ST_Slope', 'Flat')
        }
        
        return pd.DataFrame([data])
    
    def get_feature_summary(self, domain_df: pd.DataFrame) -> Dict:
        """
        الحصول على ملخص الـ features المتقدمة
        
        Args:
            domain_df: DataFrame الـ features
            
        Returns:
            Dictionary بالملخص
        """
        summary = {}
        
        # Age category
        if domain_df['age_very_young'].iloc[0] == 1:
            summary['age_category'] = 'Very Young (<30)'
        elif domain_df['age_young'].iloc[0] == 1:
            summary['age_category'] = 'Young (30-45)'
        elif domain_df['age_middle'].iloc[0] == 1:
            summary['age_category'] = 'Middle Age (45-60)'
        elif domain_df['age_senior'].iloc[0] == 1:
            summary['age_category'] = 'Senior (60-75)'
        else:
            summary['age_category'] = 'Elderly (75+)'
        
        # Cholesterol level
        if domain_df['cholesterol_optimal'].iloc[0] == 1:
            summary['cholesterol_level'] = 'Optimal (<200)'
        elif domain_df['cholesterol_borderline'].iloc[0] == 1:
            summary['cholesterol_level'] = 'Borderline (200-240)'
        elif domain_df['cholesterol_high'].iloc[0] == 1:
            summary['cholesterol_level'] = 'High (240-300)'
        else:
            summary['cholesterol_level'] = 'Very High (≥300)'
        
        # BP stage
        if domain_df['bp_normal'].iloc[0] == 1:
            summary['bp_stage'] = 'Normal (<120)'
        elif domain_df['bp_elevated'].iloc[0] == 1:
            summary['bp_stage'] = 'Elevated (120-130)'
        elif domain_df['bp_stage1'].iloc[0] == 1:
            summary['bp_stage'] = 'Stage 1 (130-140)'
        elif domain_df['bp_stage2'].iloc[0] == 1:
            summary['bp_stage'] = 'Stage 2 (≥140)'
        else:
            summary['bp_stage'] = 'Crisis (≥180)'
        
        # Exercise capacity
        if domain_df['exercise_poor'].iloc[0] == 1:
            summary['exercise_capacity'] = 'Poor'
        elif domain_df['exercise_fair'].iloc[0] == 1:
            summary['exercise_capacity'] = 'Fair'
        elif domain_df['exercise_good'].iloc[0] == 1:
            summary['exercise_capacity'] = 'Good'
        else:
            summary['exercise_capacity'] = 'Excellent'
        
        # Framingham risk
        score = int(domain_df['framingham_risk_score'].iloc[0])
        summary['framingham_score'] = f"{score}/7"
        summary['framingham_risk'] = 'High' if score >= 3 else 'Low-Moderate'
        
        # ST depression
        if domain_df['st_normal'].iloc[0] == 1:
            summary['st_depression'] = 'Normal (≤0)'
        elif domain_df['st_mild'].iloc[0] == 1:
            summary['st_depression'] = 'Mild (0-1.0)'
        elif domain_df['st_moderate'].iloc[0] == 1:
            summary['st_depression'] = 'Moderate (1.0-2.0)'
        else:
            summary['st_depression'] = 'Severe (>2.0)'
        
        return summary


# Create singleton instance
features_generator = AdvancedFeaturesGenerator()
