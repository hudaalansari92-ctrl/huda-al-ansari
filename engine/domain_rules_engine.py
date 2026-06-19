

import json
import logging
from typing import Dict, List, Tuple, Optional
from pathlib import Path

logger = logging.getLogger('domain_rules_engine')


class DomainRulesEngine:
    """
    Domain Rules Engine
    
    WORKFLOW:
    1. BioBERT extracts 11 fields
    2. Check if all fields complete
    3. If complete → Apply domain_rules.json
    4. Generate medical insights
    """
    
    def __init__(self, rules_file: str = 'domain_rules.json'):
        """تهيئة محرك القواعد"""
        self.rules_file = Path(rules_file)
        self.rules = self._load_rules()
        logger.info(f"Domain Rules Engine initialized with {len(self.rules.get('rules', []))} rules")
    
    def _load_rules(self) -> Dict:
        """تحميل القواعد من domain_rules.json"""
        try:
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                rules = json.load(f)
            logger.info(f"Loaded {rules['model_configuration']['total_rules']} rules")
            return rules
        except Exception as e:
            logger.error(f"Error loading rules: {e}")
            return {}
    
    def are_all_fields_complete(self, facts: Dict) -> Tuple[bool, List[str]]:
        """
        التحقق من اكتمال جميع الحقول الـ 11
        
        Args:
            facts: الحقول المُستخرجة
            
        Returns:
            (bool, list): (هل مكتمل؟, الحقول الناقصة)
        """
        required_fields = [
            'Age', 'Sex', 'ChestPain', 'BloodPressure', 'Cholesterol',
            'FastingBS', 'RestingECG', 'MaxHR', 'ExerciseAngina',
            'Oldpeak', 'ST_Slope'
        ]
        
        missing_fields = [field for field in required_fields if field not in facts]
        is_complete = len(missing_fields) == 0
        
        return is_complete, missing_fields
    
    def calculate_binary_features(self, facts: Dict) -> Dict[str, int]:
        """
        حساب Binary Features من domain_rules.json
        
        Binary Features (31 feature):
        - Age categories: age_very_young, age_young, age_middle, age_senior, age_elderly
        - Cholesterol: cholesterol_optimal, cholesterol_borderline, cholesterol_high, cholesterol_very_high
        - Blood Pressure: bp_normal, bp_elevated, bp_stage1, bp_stage2, bp_crisis
        - Exercise: exercise_poor, exercise_fair, exercise_good, exercise_excellent
        - Gender risk: male_high_risk, female_high_risk, female_postmenopausal
        - ST: st_normal, st_mild, st_moderate, st_severe
        - Metabolic: metabolic_bp, metabolic_chol, metabolic_diabetes
        - ... etc
        """
        binary_features = {}
        
        # Age categories
        age = facts.get('Age', 0)
        binary_features['age_very_young'] = 1 if age < 30 else 0
        binary_features['age_young'] = 1 if 30 <= age < 45 else 0
        binary_features['age_middle'] = 1 if 45 <= age < 55 else 0
        binary_features['age_senior'] = 1 if 55 <= age < 70 else 0
        binary_features['age_elderly'] = 1 if age >= 70 else 0
        
        # Cholesterol categories
        chol = facts.get('Cholesterol', 0)
        binary_features['cholesterol_optimal'] = 1 if chol < 200 else 0
        binary_features['cholesterol_borderline'] = 1 if 200 <= chol < 240 else 0
        binary_features['cholesterol_high'] = 1 if 240 <= chol < 300 else 0
        binary_features['cholesterol_very_high'] = 1 if chol >= 300 else 0
        
        # Blood Pressure categories
        bp = facts.get('BloodPressure', '0/0')
        if '/' in str(bp):
            systolic = int(bp.split('/')[0])
            diastolic = int(bp.split('/')[1])
        else:
            systolic, diastolic = 0, 0
        
        binary_features['bp_normal'] = 1 if systolic < 120 and diastolic < 80 else 0
        binary_features['bp_elevated'] = 1 if 120 <= systolic < 130 and diastolic < 80 else 0
        binary_features['bp_stage1'] = 1 if (130 <= systolic < 140) or (80 <= diastolic < 90) else 0
        binary_features['bp_stage2'] = 1 if systolic >= 140 or diastolic >= 90 else 0
        binary_features['bp_crisis'] = 1 if systolic >= 180 or diastolic >= 120 else 0
        
        # Exercise capacity (based on MaxHR)
        max_hr = facts.get('MaxHR', 0)
        predicted_max_hr = 220 - age
        hr_percentage = (max_hr / predicted_max_hr) if predicted_max_hr > 0 else 0
        
        binary_features['exercise_poor'] = 1 if hr_percentage < 0.70 else 0
        binary_features['exercise_fair'] = 1 if 0.70 <= hr_percentage < 0.85 else 0
        binary_features['exercise_good'] = 1 if 0.85 <= hr_percentage < 0.95 else 0
        binary_features['exercise_excellent'] = 1 if hr_percentage >= 0.95 else 0
        
        # Gender risk
        sex = facts.get('Sex', '')
        binary_features['male_high_risk'] = 1 if sex == 'Male' and age >= 45 else 0
        binary_features['female_high_risk'] = 1 if sex == 'Female' and age >= 55 else 0
        binary_features['female_postmenopausal'] = 1 if sex == 'Female' and age >= 50 else 0
        
        # ST Depression categories
        oldpeak = facts.get('Oldpeak', 0)
        binary_features['st_normal'] = 1 if oldpeak == 0 else 0
        binary_features['st_mild'] = 1 if 0 < oldpeak <= 1.0 else 0
        binary_features['st_moderate'] = 1 if 1.0 < oldpeak <= 2.0 else 0
        binary_features['st_severe'] = 1 if oldpeak > 2.0 else 0
        
        # Metabolic syndrome indicators
        binary_features['metabolic_bp'] = 1 if systolic >= 130 or diastolic >= 85 else 0
        binary_features['metabolic_chol'] = 1 if chol >= 200 else 0
        binary_features['metabolic_diabetes'] = 1 if facts.get('FastingBS', 0) == 1 else 0
        
        return binary_features
    
    def calculate_continuous_features(self, facts: Dict) -> Dict[str, float]:
        """
        حساب Continuous Features من domain_rules.json
        
        Continuous Features (9 features):
        - age_risk_score
        - predicted_max_hr
        - hr_reserve_ratio
        - hr_reserve
        - framingham_risk_score
        - age_cholesterol_norm
        - age_bp_norm
        - cholesterol_bp_norm
        - chest_pain_severity
        """
        continuous_features = {}
        
        age = facts.get('Age', 0)
        max_hr = facts.get('MaxHR', 0)
        chol = facts.get('Cholesterol', 0)
        bp = facts.get('BloodPressure', '0/0')
        
        if '/' in str(bp):
            systolic = int(bp.split('/')[0])
        else:
            systolic = 0
        
        # Age risk score (normalized)
        continuous_features['age_risk_score'] = age / 70.0  # Normalize to 0-1
        
        # Predicted max HR
        predicted_max_hr = 220 - age
        continuous_features['predicted_max_hr'] = predicted_max_hr
        
        # HR reserve and ratio
        hr_reserve = predicted_max_hr - max_hr
        continuous_features['hr_reserve'] = hr_reserve
        continuous_features['hr_reserve_ratio'] = (max_hr / predicted_max_hr) if predicted_max_hr > 0 else 0
        
        # Framingham risk score (simplified)
        framingham = 0
        if age >= 45:
            framingham += 1
        if chol >= 240:
            framingham += 1
        if systolic >= 140:
            framingham += 1
        if facts.get('FastingBS', 0) == 1:
            framingham += 1
        continuous_features['framingham_risk_score'] = framingham
        
        # Normalized ratios
        continuous_features['age_cholesterol_norm'] = (age / 70.0) * (chol / 400.0)
        continuous_features['age_bp_norm'] = (age / 70.0) * (systolic / 200.0)
        continuous_features['cholesterol_bp_norm'] = (chol / 400.0) * (systolic / 200.0)
        
        # Chest pain severity
        chest_pain = facts.get('ChestPain', '')
        chest_pain_scores = {'ASY': 0, 'NAP': 1, 'ATA': 2, 'TA': 3}
        continuous_features['chest_pain_severity'] = chest_pain_scores.get(chest_pain, 0)
        
        return continuous_features
    
    def apply_rules(self, binary_features: Dict[str, int]) -> List[Dict]:
        """
        تطبيق القواعد المركبة من domain_rules.json
        
        Rules format:
        {
            "rule_id": "R1",
            "condition": "male_high_risk=1 AND cholesterol_high=1",
            "feature_name": "male_high_risk+cholesterol_high",
            "confidence": 0.95,
            "lift": 1.5,
            ...
        }
        """
        triggered_rules = []
        
        rules = self.rules.get('rules', [])
        
        for rule in rules:
            condition = rule.get('condition', '')
            
            # Parse condition (e.g., "male_high_risk=1 AND cholesterol_high=1")
            if self._evaluate_condition(condition, binary_features):
                triggered_rules.append({
                    'rule_id': rule['rule_id'],
                    'condition': condition,
                    'confidence': rule.get('confidence', 0),
                    'lift': rule.get('lift', 0),
                    'weight': rule.get('weight', 0),
                    'feature_name': rule.get('feature_name', '')
                })
        
        # Sort by weight (importance)
        triggered_rules.sort(key=lambda x: x['weight'], reverse=True)
        
        return triggered_rules
    
    def _evaluate_condition(self, condition: str, features: Dict[str, int]) -> bool:
        """
        Evaluate a boolean rule condition against the binary feature map.

        Supported operators (with the usual logical precedence
        NOT > AND > OR) and parentheses for grouping:

            feature=value
            NOT feature=value
            cond1 AND cond2
            cond1 OR cond2
            (cond1 OR cond2) AND cond3

        Examples
        --------
            "male_high_risk=1 AND cholesterol_high=1"
            "bp_stage2=1 OR bp_crisis=1"
            "NOT exercise_excellent=1 AND cholesterol_high=1"
            "(bp_stage1=1 OR bp_stage2=1) AND NOT exercise_excellent=1"

        Backward compatibility: any rule using only "feature=value" or
        plain "A AND B" continues to evaluate exactly as before.
        """
        try:
            return self._eval_boolean_expression(condition, features)
        except Exception:
            # On any parse error, fall back to the old AND-only behaviour
            # so we never break a rule that worked previously.
            return self._eval_and_only(condition, features)

    # ------------------------------------------------------------------
    #  Legacy AND-only evaluator (kept as a safety net).
    # ------------------------------------------------------------------
    @staticmethod
    def _eval_and_only(condition: str, features: Dict[str, int]) -> bool:
        for cond in condition.split(' AND '):
            cond = cond.strip()
            if '=' not in cond:
                continue
            feature, value = cond.split('=', 1)
            if features.get(feature.strip(), 0) != int(value.strip()):
                return False
        return True

    # ------------------------------------------------------------------
    #  Recursive-descent parser for AND / OR / NOT / parentheses.
    # ------------------------------------------------------------------
    @classmethod
    def _eval_boolean_expression(cls, condition: str, features: Dict[str, int]) -> bool:
        tokens = cls._tokenize_condition(condition)
        pos = [0]

        def peek():
            return tokens[pos[0]] if pos[0] < len(tokens) else None

        def consume(expected=None):
            tok = peek()
            if expected is not None and tok != expected:
                raise ValueError(f"expected {expected!r}, got {tok!r}")
            pos[0] += 1
            return tok

        def parse_atom():
            tok = peek()
            if tok == '(':
                consume('(')
                val = parse_or()
                consume(')')
                return val
            if tok == 'NOT':
                consume('NOT')
                return not parse_atom()
            # leaf: feature=value
            if tok is None or tok in ('AND', 'OR', ')'):
                raise ValueError(f"unexpected token {tok!r}")
            consume()
            if '=' not in tok:
                raise ValueError(f"bad atomic condition: {tok!r}")
            feature, value = tok.split('=', 1)
            return features.get(feature.strip(), 0) == int(value.strip())

        def parse_and():
            val = parse_atom()
            while peek() == 'AND':
                consume('AND')
                val = parse_atom() and val
            return val

        def parse_or():
            val = parse_and()
            while peek() == 'OR':
                consume('OR')
                val = parse_and() or val
            return val

        result = parse_or()
        if peek() is not None:
            raise ValueError(f"trailing token {peek()!r}")
        return result

    @staticmethod
    def _tokenize_condition(condition: str) -> list:
        """Split a condition string into tokens, preserving (, ), AND, OR, NOT."""
        # Add spaces around parentheses so split() picks them up.
        s = condition.replace('(', ' ( ').replace(')', ' ) ')
        raw = s.split()
        # Re-merge "feature = value" atoms in case the user spaced the '='.
        tokens, i = [], 0
        while i < len(raw):
            t = raw[i]
            if t in ('AND', 'OR', 'NOT', '(', ')'):
                tokens.append(t)
                i += 1
                continue
            # Merge "feature", "=", "value" if separated
            if i + 2 < len(raw) and raw[i + 1] == '=':
                tokens.append(f"{t}={raw[i + 2]}")
                i += 3
                continue
            tokens.append(t)
            i += 1
        return tokens
    
    def generate_medical_insights(
        self,
        facts: Dict,
        binary_features: Dict[str, int],
        continuous_features: Dict[str, float],
        triggered_rules: List[Dict]
    ) -> Dict:
        """
        توليد التفسيرات الطبية بناءً على القواعد
        
        Returns:
            Dict with:
            - risk_level: Low/Medium/High
            - risk_factors: List of risk factors
            - recommendations: List of recommendations
            - triggered_rules_summary: Summary of important rules
        """
        insights = {
            'risk_level': 'Low',
            'risk_factors_ar': [],
            'risk_factors_en': [],
            'recommendations_ar': [],
            'recommendations_en': [],
            'triggered_rules_count': len(triggered_rules),
            'top_rules': []
        }
        
        # Determine risk level based on triggered rules
        high_risk_count = sum(1 for rule in triggered_rules if rule['confidence'] >= 0.9)
        
        if high_risk_count >= 5:
            insights['risk_level'] = 'High'
            insights['risk_level_ar'] = 'عالي'
        elif high_risk_count >= 2:
            insights['risk_level'] = 'Medium'
            insights['risk_level_ar'] = 'متوسط'
        else:
            insights['risk_level'] = 'Low'
            insights['risk_level_ar'] = 'منخفض'
        
        # Extract risk factors from binary features
        if binary_features.get('cholesterol_high', 0) == 1:
            insights['risk_factors_ar'].append('كوليسترول مرتفع')
            insights['risk_factors_en'].append('High cholesterol')
        
        if binary_features.get('bp_stage2', 0) == 1:
            insights['risk_factors_ar'].append('ضغط دم مرتفع (المرحلة 2)')
            insights['risk_factors_en'].append('High blood pressure (Stage 2)')
        
        if binary_features.get('metabolic_diabetes', 0) == 1:
            insights['risk_factors_ar'].append('سكري')
            insights['risk_factors_en'].append('Diabetes')
        
        if binary_features.get('male_high_risk', 0) == 1:
            insights['risk_factors_ar'].append('ذكر فوق 45 سنة (عامل خطر)')
            insights['risk_factors_en'].append('Male over 45 (risk factor)')
        
        if binary_features.get('st_moderate', 0) == 1 or binary_features.get('st_severe', 0) == 1:
            insights['risk_factors_ar'].append('انخفاض ST ملحوظ')
            insights['risk_factors_en'].append('Significant ST depression')
        
        # Generate recommendations
        if insights['risk_level'] in ['Medium', 'High']:
            insights['recommendations_ar'] = [
                'استشارة طبيب القلب فوراً',
                'إجراء فحوصات إضافية',
                'مراقبة ضغط الدم يومياً',
                'نظام غذائي صحي للقلب',
                'ممارسة الرياضة بإشراف طبي'
            ]
            insights['recommendations_en'] = [
                'Consult a cardiologist immediately',
                'Conduct additional tests',
                'Monitor blood pressure daily',
                'Follow heart-healthy diet',
                'Exercise under medical supervision'
            ]
        else:
            insights['recommendations_ar'] = [
                'الحفاظ على نمط حياة صحي',
                'فحوصات دورية سنوية',
                'ممارسة الرياضة المنتظمة',
                'نظام غذائي متوازن'
            ]
            insights['recommendations_en'] = [
                'Maintain healthy lifestyle',
                'Annual check-ups',
                'Regular exercise',
                'Balanced diet'
            ]
        
        # Top triggered rules
        insights['top_rules'] = triggered_rules[:5]  # Top 5 most important rules
        
        return insights
    
    def process_complete_data(self, facts: Dict) -> Dict:
        """
        معالجة البيانات الكاملة وتطبيق القواعد
        
        MAIN WORKFLOW:
        1. Check if all 11 fields are complete
        2. Calculate binary features
        3. Calculate continuous features
        4. Apply domain rules
        5. Generate medical insights
        
        Args:
            facts: جميع الحقول الـ 11
            
        Returns:
            Dict with all features, rules, and insights
        """
        # Step 1: Check completeness
        is_complete, missing = self.are_all_fields_complete(facts)
        
        if not is_complete:
            return {
                'status': 'incomplete',
                'missing_fields': missing,
                'message_ar': f'ينقص {len(missing)} حقل لإكمال التحليل',
                'message_en': f'{len(missing)} fields missing for complete analysis'
            }
        
        # Step 2: Calculate binary features
        binary_features = self.calculate_binary_features(facts)
        
        # Step 3: Calculate continuous features
        continuous_features = self.calculate_continuous_features(facts)
        
        # Step 4: Apply rules
        triggered_rules = self.apply_rules(binary_features)
        
        # Step 5: Generate insights
        insights = self.generate_medical_insights(
            facts,
            binary_features,
            continuous_features,
            triggered_rules
        )
        
        logger.info(f"Processed complete data: {len(triggered_rules)} rules triggered")
        
        return {
            'status': 'complete',
            'binary_features': binary_features,
            'continuous_features': continuous_features,
            'triggered_rules': triggered_rules,
            'insights': insights
        }
