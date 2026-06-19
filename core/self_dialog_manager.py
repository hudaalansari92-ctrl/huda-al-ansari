

from typing import Dict, List, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass
import json
import logging

logger = logging.getLogger('self_dialog_manager')


@dataclass
class InternalThought:
    """فكرة داخلية للـ Chatbot"""
    thought: str  # الفكرة بالعربية
    thought_en: str  # الفكرة بالإنجليزية
    category: str  # analysis, inference, decision, warning
    confidence: float  # درجة الثقة (0.0-1.0)
    timestamp: datetime
    language: str = 'ar'  # اللغة المستخدمة


@dataclass
class SelfUpdate:
    """تحديث ذاتي للحالة"""
    update_type: str  # fact_added, inference_made, priority_changed, warning_triggered
    details: Dict
    timestamp: datetime
    impact_level: str  # low, medium, high, critical


class SelfDialogManager:
    """
    مدير الحوار الذاتي
    يدير تفكير الـ Chatbot الداخلي وكيفية تحديث نفسه
    """
    
    def __init__(self, language: str = 'ar'):
        """
        تهيئة مدير الحوار الذاتي
        
        Args:
            language: اللغة الافتراضية ('ar' أو 'en')
        """
        self.language = language
        self.internal_thoughts: List[InternalThought] = []
        self.self_updates: List[SelfUpdate] = []
        self.current_facts: Dict = {}
        self.current_inferences: Dict = {}
        self.current_risk_level: str = 'LOW'
        self.confidence_score: float = 0.0
        
    def analyze_answer(self, 
                      fact_type: str, 
                      fact_value: str,
                      existing_facts: Dict) -> InternalThought:
        """
        تحليل إجابة المستخدم والتحدث مع النفس عنها
        
        Args:
            fact_type: نوع الحقيقة (Age, ChestPain, etc)
            fact_value: قيمة الحقيقة
            existing_facts: الحقائق الموجودة حالياً
            
        Returns:
            InternalThought: فكرة داخلية
        """
        thought_ar = self._generate_thought_ar(fact_type, fact_value, existing_facts)
        thought_en = self._generate_thought_en(fact_type, fact_value, existing_facts)
        
        confidence = self._calculate_thought_confidence(fact_type, fact_value)
        
        internal_thought = InternalThought(
            thought=thought_ar,
            thought_en=thought_en,
            category='analysis',
            confidence=confidence,
            timestamp=datetime.now(),
            language=self.language
        )
        
        self.internal_thoughts.append(internal_thought)
        logger.info(f"[تحليل داخلي] {fact_type}: {thought_ar}")
        
        return internal_thought
    
    def _generate_thought_ar(self, 
                            fact_type: str, 
                            fact_value: str,
                            existing_facts: Dict) -> str:
        """توليد أفكار داخلية بالعربية"""
        thoughts = {
            'Age': {
                'high': f"العمر {fact_value} سنة... هذا أكبر من 50، عامل خطر مهم! ",
                'medium': f"العمر {fact_value} سنة... طبيعي نسبياً",
                'info': f"تم تسجيل العمر: {fact_value} سنة"
            },
            'ChestPain': {
                'yes': "ألم صدر! هذا علامة تحذيرية جداً! ",
                'no': "لا يوجد ألم صدر... ممتاز! ",
                'info': "تم تسجيل معلومة الألم"
            },
            'BloodPressure': {
                'high': f"ضغط دم مرتفع جداً! {fact_value} = حالة حرجة! ",
                'moderate': f"ضغط دم مرتفع قليلاً: {fact_value}",
                'normal': f"ضغط دم طبيعي: {fact_value} "
            },
            'Cholesterol': {
                'high': f"كوليسترول مرتفع جداً! {fact_value} = عامل خطر رئيسي! ",
                'medium': f"كوليسترول مرتفع قليلاً: {fact_value}",
                'normal': f"كوليسترول طبيعي: {fact_value} "
            },
            'ExerciseInducedAngina': {
                'yes': "ألم مع المجهود! هذا شديد الأهمية! ",
                'no': "لا ألم مع المجهود... جيد! "
            },
            'FastingBloodSugar': {
                'yes': "سكر الدم مرتفع! هذا عامل خطر إضافي! ",
                'no': "سكر الدم طبيعي... ممتاز! "
            }
        }
        
        # اختر الفكرة المناسبة
        if fact_type in thoughts:
            category = self._categorize_value(fact_type, fact_value)
            return thoughts[fact_type].get(category, f"تم تسجيل {fact_type}: {fact_value}")
        
        return f"تم تسجيل {fact_type}: {fact_value}"
    
    def _generate_thought_en(self, 
                            fact_type: str, 
                            fact_value: str,
                            existing_facts: Dict) -> str:
        """توليد أفكار داخلية بالإنجليزية"""
        thoughts = {
            'Age': {
                'high': f"Age {fact_value}... Over 50, important risk factor! ",
                'medium': f"Age {fact_value}... Relatively normal",
                'info': f"Age registered: {fact_value} years"
            },
            'ChestPain': {
                'yes': "Chest pain! Critical warning sign! ",
                'no': "No chest pain... Excellent! ",
                'info': "Pain information registered"
            },
            'BloodPressure': {
                'high': f"High blood pressure! {fact_value} = Critical! ",
                'moderate': f"Elevated blood pressure: {fact_value}",
                'normal': f"Normal blood pressure: {fact_value} "
            },
            'Cholesterol': {
                'high': f"High cholesterol! {fact_value} = Major risk factor! ",
                'medium': f"Elevated cholesterol: {fact_value}",
                'normal': f"Normal cholesterol: {fact_value} "
            },
            'ExerciseInducedAngina': {
                'yes': "Pain with exercise! Very significant! ",
                'no': "No pain with exercise... Good! "
            },
            'FastingBloodSugar': {
                'yes': "High blood sugar! Additional risk factor! ",
                'no': "Normal blood sugar... Excellent! "
            }
        }
        
        if fact_type in thoughts:
            category = self._categorize_value(fact_type, fact_value)
            return thoughts[fact_type].get(category, f"{fact_type} registered: {fact_value}")
        
        return f"{fact_type} registered: {fact_value}"
    
    def _categorize_value(self, fact_type: str, fact_value: str) -> str:
        """تصنيف قيمة الحقيقة (high, medium, normal, yes, no)"""
        fact_value_str = str(fact_value).lower()
        
        # تصنيف نعم/لا
        if fact_type in ['ChestPain', 'ExerciseInducedAngina', 'FastingBloodSugar']:
            if 'yes' in fact_value_str or 'نعم' in fact_value_str:
                return 'yes'
            return 'no'
        
        # تصنيف الأرقام
        if fact_type == 'Age':
            age = self._extract_number(fact_value)
            if age and age > 50:
                return 'high'
            return 'medium'
        
        elif fact_type == 'BloodPressure':
            systolic = self._extract_bp_systolic(fact_value)
            if systolic and systolic >= 140:
                return 'high'
            elif systolic and systolic >= 130:
                return 'moderate'
            return 'normal'
        
        elif fact_type == 'Cholesterol':
            chol = self._extract_number(fact_value)
            if chol and chol > 240:
                return 'high'
            elif chol and chol > 200:
                return 'medium'
            return 'normal'
        
        return 'info'
    
    def _extract_number(self, value: str) -> Optional[float]:
        """استخراج رقم من النص"""
        try:
            import re
            numbers = re.findall(r'\d+\.?\d*', str(value))
            if numbers:
                return float(numbers[0])
        except:
            pass
        return None
    
    def _extract_bp_systolic(self, value: str) -> Optional[int]:
        """استخراج ضغط الدم الانقباضي"""
        try:
            import re
            numbers = re.findall(r'\d+', str(value))
            if numbers:
                return int(numbers[0])
        except:
            pass
        return None
    
    def _calculate_thought_confidence(self, fact_type: str, fact_value: str) -> float:
        """حساب درجة ثقة الفكرة الداخلية"""
        # أرقام واضحة = ثقة عالية
        if self._extract_number(fact_value):
            return 0.95
        # إجابات نعم/لا = ثقة عالية
        elif 'yes' in str(fact_value).lower() or 'no' in str(fact_value).lower():
            return 0.90
        return 0.75
    
    def infer_from_facts(self, facts: Dict) -> InternalThought:
        """
        الاستنتاج من الحقائق المجمعة
        الـ Chatbot يفكر: "ماذا تعني هذه الحقائق مجموعة؟"
        """
        inference_ar = self._generate_inference_ar(facts)
        inference_en = self._generate_inference_en(facts)
        
        confidence = self._calculate_inference_confidence(facts)
        
        internal_thought = InternalThought(
            thought=inference_ar,
            thought_en=inference_en,
            category='inference',
            confidence=confidence,
            timestamp=datetime.now(),
            language=self.language
        )
        
        self.internal_thoughts.append(internal_thought)
        logger.info(f"[استنتاج] {inference_ar}")
        
        return internal_thought
    
    def _safe_int(self, value, default=0) -> int:
        """تحويل آمن للقيمة إلى عدد صحيح"""
        try:
            if isinstance(value, (int, float)):
                return int(value)
            if isinstance(value, str):
                # استخراج الأرقام من النص
                import re
                numbers = re.findall(r'\d+', value)
                if numbers:
                    return int(numbers[0])
            return default
        except:
            return default
    
    def _generate_inference_ar(self, facts: Dict) -> str:
        """توليد استنتاج بالعربية"""
        risk_factors = 0
        inference_parts = []
        
        # عد عوامل الخطر
        if self._safe_int(facts.get('Age', 0)) > 50:
            risk_factors += 1
            inference_parts.append("العمر أكبر من 50")
        
        if facts.get('ChestPain') == 'Yes':
            risk_factors += 1
            inference_parts.append("وجود ألم صدر")
        
        if self._extract_number(str(facts.get('BloodPressure', '0'))) and \
           self._extract_bp_systolic(str(facts.get('BloodPressure', '0'))) >= 140:
            risk_factors += 1
            inference_parts.append("ضغط دم مرتفع جداً")
        
        if self._extract_number(str(facts.get('Cholesterol', '0'))) and \
           self._extract_number(str(facts.get('Cholesterol', '0'))) > 240:
            risk_factors += 1
            inference_parts.append("كوليسترول مرتفع جداً")
        
        if facts.get('ExerciseInducedAngina') == 'Yes':
            risk_factors += 1
            inference_parts.append("ألم مع المجهود")
        
        if facts.get('FastingBloodSugar') == 'Yes':
            risk_factors += 1
            inference_parts.append("سكر دم مرتفع")
        
        # بناء الاستنتاج
        if risk_factors >= 4:
            return f" CRITICAL! لدينا {risk_factors} عوامل خطر: {', '.join(inference_parts)}. احتمالية عالية جداً لأمراض القلب!"
        elif risk_factors >= 3:
            return f" SERIOUS! {risk_factors} عوامل خطر: {', '.join(inference_parts)}. خطر عالي من أمراض القلب."
        elif risk_factors >= 2:
            return f" لدينا {risk_factors} عوامل خطر. يجب الاستمرار في الفحص."
        else:
            return "الحمد لله، لا توجد عوامل خطر واضحة حتى الآن."
    
    def _generate_inference_en(self, facts: Dict) -> str:
        """توليد استنتاج بالإنجليزية"""
        risk_factors = 0
        inference_parts = []
        
        if self._safe_int(facts.get('Age', 0)) > 50:
            risk_factors += 1
            inference_parts.append("Age > 50")
        
        if facts.get('ChestPain') == 'Yes':
            risk_factors += 1
            inference_parts.append("Chest pain present")
        
        if self._extract_bp_systolic(str(facts.get('BloodPressure', '0'))) and \
           self._extract_bp_systolic(str(facts.get('BloodPressure', '0'))) >= 140:
            risk_factors += 1
            inference_parts.append("High blood pressure")
        
        if self._extract_number(str(facts.get('Cholesterol', '0'))) and \
           self._extract_number(str(facts.get('Cholesterol', '0'))) > 240:
            risk_factors += 1
            inference_parts.append("High cholesterol")
        
        if facts.get('ExerciseInducedAngina') == 'Yes':
            risk_factors += 1
            inference_parts.append("Exercise-induced pain")
        
        if facts.get('FastingBloodSugar') == 'Yes':
            risk_factors += 1
            inference_parts.append("High blood sugar")
        
        if risk_factors >= 4:
            return f" CRITICAL! {risk_factors} risk factors: {', '.join(inference_parts)}. Very high likelihood of heart disease!"
        elif risk_factors >= 3:
            return f" SERIOUS! {risk_factors} risk factors: {', '.join(inference_parts)}. High risk of heart disease."
        elif risk_factors >= 2:
            return f" {risk_factors} risk factors present. Continue assessment."
        else:
            return "Good news, no obvious risk factors detected so far."
    
    def _calculate_inference_confidence(self, facts: Dict) -> float:
        """حساب ثقة الاستنتاج"""
        # كل حقيقة تضيف ثقة
        facts_count = len([v for v in facts.values() if v])
        base_confidence = min(0.5 + (facts_count * 0.1), 0.95)
        return base_confidence
    
    def make_decision(self, facts: Dict, inferences: Dict) -> InternalThought:
        """
        اتخاذ قرار بناءً على الحقائق والاستنتاجات
        "ماذا يجب أن أسأل التالي؟"
        """
        decision_ar = self._generate_decision_ar(facts, inferences)
        decision_en = self._generate_decision_en(facts, inferences)
        
        internal_thought = InternalThought(
            thought=decision_ar,
            thought_en=decision_en,
            category='decision',
            confidence=0.85,
            timestamp=datetime.now(),
            language=self.language
        )
        
        self.internal_thoughts.append(internal_thought)
        logger.info(f"[قرار] {decision_ar}")
        
        return internal_thought
    
    def _generate_decision_ar(self, facts: Dict, inferences: Dict) -> str:
        """توليد قرار بالعربية"""
        answered = len([v for v in facts.values() if v])
        
        # تحديد السؤال التالي
        if 'ChestPain' not in facts or not facts.get('ChestPain'):
            return "يجب أسأل عن ألم الصدر أولاً - هذا الأهم! "
        elif 'BloodPressure' not in facts or not facts.get('BloodPressure'):
            return "ضغط الدم مهم جداً! سأسأل عنه التالي."
        elif 'Cholesterol' not in facts or not facts.get('Cholesterol'):
            return "الكوليسترول عامل خطر مهم جداً. يجب السؤال عنه."
        elif 'FastingBloodSugar' not in facts or not facts.get('FastingBloodSugar'):
            return "سكر الدم أيضاً مهم. سأسأل عنه."
        else:
            return f"تم جمع {answered} معلومات. سأكمل الأسئلة الباقية."
    
    def _generate_decision_en(self, facts: Dict, inferences: Dict) -> str:
        """توليد قرار بالإنجليزية"""
        answered = len([v for v in facts.values() if v])
        
        if 'ChestPain' not in facts or not facts.get('ChestPain'):
            return "Must ask about chest pain first - most important! "
        elif 'BloodPressure' not in facts or not facts.get('BloodPressure'):
            return "Blood pressure is critical! Will ask next."
        elif 'Cholesterol' not in facts or not facts.get('Cholesterol'):
            return "Cholesterol is major risk factor. Must ask."
        elif 'FastingBloodSugar' not in facts or not facts.get('FastingBloodSugar'):
            return "Blood sugar also important. Will ask."
        else:
            return f"Collected {answered} data points. Continue with remaining questions."
    
    def trigger_warning(self, 
                       warning_type: str, 
                       severity: str,
                       details: Dict) -> InternalThought:
        """
        تنبيه من الخطر
        الـ Chatbot يتحدث مع نفسه: "هذا خطير جداً!"
        """
        warning_ar = self._generate_warning_ar(warning_type, severity, details)
        warning_en = self._generate_warning_en(warning_type, severity, details)
        
        internal_thought = InternalThought(
            thought=warning_ar,
            thought_en=warning_en,
            category='warning',
            confidence=1.0,
            timestamp=datetime.now(),
            language=self.language
        )
        
        self.internal_thoughts.append(internal_thought)
        logger.warning(f"[تحذير] {warning_ar}")
        
        return internal_thought
    
    def _generate_warning_ar(self, warning_type: str, severity: str, details: Dict) -> str:
        """توليد تحذير بالعربية"""
        warnings = {
            'critical_symptoms': {
                'critical': " تحذير حرج! أعراض قد تشير لنوبة قلبية!",
                'high': " تحذير مهم! أعراض خطيرة!",
                'medium': " انتبه! هذه أعراض تحتاج متابعة."
            },
            'multiple_risk_factors': {
                'critical': " احتمالية عالية جداً لأمراض القلب! (4+ عوامل خطر)",
                'high': " احتمالية عالية لأمراض القلب! (3+ عوامل خطر)",
                'medium': "احتمالية متوسطة. يجب متابعة دقيقة."
            }
        }
        
        if warning_type in warnings:
            return warnings[warning_type].get(severity, "تحذير: هناك مؤشرات قد تحتاج اهتمام.")
        
        return f"تحذير: {warning_type}"
    
    def _generate_warning_en(self, warning_type: str, severity: str, details: Dict) -> str:
        """توليد تحذير بالإنجليزية"""
        warnings = {
            'critical_symptoms': {
                'critical': " CRITICAL WARNING! Symptoms may indicate heart attack!",
                'high': " IMPORTANT WARNING! Serious symptoms!",
                'medium': " Caution! These symptoms need monitoring."
            },
            'multiple_risk_factors': {
                'critical': " Very high likelihood of heart disease! (4+ risk factors)",
                'high': " High likelihood of heart disease! (3+ risk factors)",
                'medium': "Moderate likelihood. Close monitoring required."
            }
        }
        
        if warning_type in warnings:
            return warnings[warning_type].get(severity, "Warning: Indicators may need attention.")
        
        return f"Warning: {warning_type}"
    
    def self_update(self, 
                   update_type: str, 
                   details: Dict) -> SelfUpdate:
        """
        تحديث الحالة الذاتية
        الـ Chatbot يحدث نفسه
        """
        update = SelfUpdate(
            update_type=update_type,
            details=details,
            timestamp=datetime.now(),
            impact_level=self._calculate_impact(update_type, details)
        )
        
        self.self_updates.append(update)
        logger.info(f"[تحديث ذاتي] {update_type}: {impact_level}")
        
        return update
    
    def _calculate_impact(self, update_type: str, details: Dict) -> str:
        """حساب مستوى التأثير"""
        if update_type in ['warning_triggered', 'critical_symptom']:
            return 'critical'
        elif update_type in ['risk_level_changed', 'inference_made']:
            return 'high'
        elif update_type in ['priority_changed', 'fact_added']:
            return 'medium'
        return 'low'
    
    def get_internal_monologue(self) -> str:
        """الحصول على سلسلة التفكير الداخلية الكاملة"""
        monologue = " [سلسلة التفكير الداخلية]\n" + "="*50 + "\n"
        
        for thought in self.internal_thoughts[-5:]:  # آخر 5 أفكار
            monologue += f" {thought.thought}\n"
        
        return monologue
    
    def get_summary(self) -> Dict:
        """ملخص حالة الـ Chatbot"""
        return {
            'thoughts_count': len(self.internal_thoughts),
            'updates_count': len(self.self_updates),
            'last_thought': self.internal_thoughts[-1] if self.internal_thoughts else None,
            'current_risk_level': self.current_risk_level,
            'confidence_score': self.confidence_score,
            'internal_monologue': self.get_internal_monologue()
        }


# مثال على الاستخدام
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # إنشاء مدير الحوار الذاتي
    dialog_manager = SelfDialogManager(language='ar')
    
    # محاكاة حوار
    facts = {
        'Age': 55,
        'ChestPain': 'Yes',
        'BloodPressure': '145/90',
        'Cholesterol': 280
    }
    
    # تحليل إجابة
    print("\n1. تحليل الإجابة:")
    print("" * 50)
    thought = dialog_manager.analyze_answer('Age', '55', facts)
    print(f"الفكرة: {thought.thought}")
    print(f"الثقة: {thought.confidence}")
    
    # الاستنتاج
    print("\n2. الاستنتاج:")
    print("" * 50)
    inference = dialog_manager.infer_from_facts(facts)
    print(f"الاستنتاج: {inference.thought}")
    
    # القرار
    print("\n3. القرار:")
    print("" * 50)
    decision = dialog_manager.make_decision(facts, {})
    print(f"القرار: {decision.thought}")
    
    # التحذير
    print("\n4. التحذير:")
    print("" * 50)
    warning = dialog_manager.trigger_warning(
        'critical_symptoms', 
        'critical',
        {'symptom': 'chest_pain', 'severity': 'severe'}
    )
    print(f"التحذير: {warning.thought}")
    
    # الملخص
    print("\n5. الملخص:")
    print("" * 50)
    summary = dialog_manager.get_summary()
    print(f"عدد الأفكار: {summary['thoughts_count']}")
    print(f"عدد التحديثات: {summary['updates_count']}")
    print(f"مستوى الخطر الحالي: {summary['current_risk_level']}")
