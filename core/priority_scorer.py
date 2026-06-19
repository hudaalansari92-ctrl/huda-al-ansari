

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger('priority_scorer')


@dataclass
class QuestionPriority:
    """أولوية سؤال معين"""
    field_name: str  # اسم الحقل (Age, ChestPain, etc)
    priority_score: float  # درجة الأولوية (0.0-1.0)
    reasoning_ar: str  # السبب بالعربية
    reasoning_en: str  # السبب بالإنجليزية
    risk_contribution: float  # مدى إسهام الحقل في الخطر
    is_critical: bool  # هل هو سؤال حرج؟


class PriorityScorer:
    """
    نظام حساب الأولويات
    يحدد أي سؤال يجب طرحه بناءً على الحقائق الموجودة
    """
    
    def __init__(self):
        """تهيئة نظام الأولويات"""
        # الأوزان الأساسية لكل حقل (استخدام أسماء BioBERT الموحدة)
        self.base_weights = {
            'ChestPain': 0.25,              # أهم حقل!
            'BloodPressure': 0.20,
            'Cholesterol': 0.15,
            'Sex': 0.14,                    # حقل أساسي ديموغرافي — يُسأل مبكراً
            'FastingBS': 0.12,
            'MaxHR': 0.10,
            'ExerciseAngina': 0.10,
            'RestingECG': 0.08,
            'Oldpeak': 0.07,
            'ST_Slope': 0.06,
            'Age': 0.04,
        }
        
        # الأسئلة الحرجة (يجب طرحها أولاً)
        self.critical_fields = ['ChestPain', 'BloodPressure', 'Cholesterol']
        
        # الأسئلة الداعمة
        self.supporting_fields = ['FastingBS', 'ExerciseAngina']
    
    def calculate_priorities(self, 
                            facts: Dict,
                            current_risk_level: str = 'LOW',
                            answered_fields: List[str] = None) -> List[QuestionPriority]:
        """
        حساب أولويات جميع الأسئلة
        
        Args:
            facts: الحقائق المجمعة حتى الآن
            current_risk_level: مستوى الخطر الحالي
            answered_fields: الحقول التي تمت الإجابة عليها
            
        Returns:
            قائمة بالأولويات مرتبة تنازلياً
        """
        if answered_fields is None:
            answered_fields = []
        
        priorities = []
        
        for field_name, base_weight in self.base_weights.items():
            # إذا تم الإجابة على السؤال، تخطاه
            if field_name in answered_fields:
                continue
            
            # حساب الأولوية
            priority_score = self._calculate_priority_score(
                field_name,
                base_weight,
                facts,
                current_risk_level,
                answered_fields
            )
            
            # توليد التفسير
            reasoning_ar, reasoning_en = self._generate_reasoning(
                field_name,
                priority_score,
                current_risk_level,
                facts
            )
            
            # تحديد إذا كان حرج
            is_critical = field_name in self.critical_fields and priority_score > 0.7
            
            # حساب مساهمة الحقل في الخطر
            risk_contribution = self._calculate_risk_contribution(field_name, facts)
            
            priority = QuestionPriority(
                field_name=field_name,
                priority_score=priority_score,
                reasoning_ar=reasoning_ar,
                reasoning_en=reasoning_en,
                risk_contribution=risk_contribution,
                is_critical=is_critical
            )
            
            priorities.append(priority)
        
        # ترتيب تنازلي حسب الأولوية
        priorities.sort(key=lambda x: x.priority_score, reverse=True)
        
        # تسجيل النتائج
        logger.info(f"تم حساب {len(priorities)} أولويات")
        for p in priorities[:3]:
            logger.info(f"  {p.field_name}: {p.priority_score:.2f} ({p.reasoning_ar})")
        
        return priorities
    
    def _calculate_priority_score(self,
                                  field_name: str,
                                  base_weight: float,
                                  facts: Dict,
                                  current_risk_level: str,
                                  answered_fields: List[str]) -> float:
        """حساب درجة أولوية حقل معين"""
        
        # 1. الوزن الأساسي
        score = base_weight

        # 2. Sex يُسأل مباشرة بعد Age (حقل ديموغرافي أساسي)
        if field_name == 'Sex' and 'Age' in answered_fields and 'Sex' not in answered_fields:
            score += 0.50

        # 3. إذا كان الحقل حرجاً، زيادة الأولوية
        if field_name in self.critical_fields:
            score += 0.15
        
        # 3. بناءً على مستوى الخطر الحالي
        risk_multiplier = {
            'LOW': 1.0,
            'MEDIUM': 1.3,
            'HIGH': 1.5,
            'CRITICAL': 2.0
        }
        score *= risk_multiplier.get(current_risk_level, 1.0)
        
        # 4. إذا كان لدينا حقائق تشير لخطر، زيادة أولوية الحقول الداعمة
        if self._indicates_risk(facts):
            if field_name in self.supporting_fields:
                score += 0.10
        
        # 5. الحد الأقصى للدرجة هو 1.0
        return min(score, 1.0)
    
    def _indicates_risk(self, facts: Dict) -> bool:
        """هل الحقائق تشير لوجود خطر؟"""
        # إذا كان هناك ألم صدر
        if facts.get('ChestPain') == 'Yes':
            return True
        
        # إذا كان ضغط الدم مرتفع جداً
        bp = facts.get('BloodPressure', '')
        if self._is_high_bp(bp):
            return True
        
        # إذا كان الكوليسترول مرتفع جداً
        chol = facts.get('Cholesterol', 0)
        if isinstance(chol, (int, float)) and chol > 240:
            return True
        
        return False
    
    def _is_high_bp(self, bp_value) -> bool:
        """هل ضغط الدم مرتفع جداً؟"""
        try:
            if isinstance(bp_value, str):
                systolic = int(bp_value.split('/')[0])
                return systolic >= 140
        except:
            pass
        return False
    
    def _calculate_risk_contribution(self, field_name: str, facts: Dict) -> float:
        """حساب مدى إسهام الحقل في الخطر"""
        
        if field_name == 'ChestPain':
            if facts.get('ChestPain') == 'Yes':
                return 0.40  # أكبر مساهمة
            return 0.0
        
        elif field_name == 'BloodPressure':
            if self._is_high_bp(facts.get('BloodPressure')):
                return 0.25
            return 0.0
        
        elif field_name == 'Cholesterol':
            chol = facts.get('Cholesterol', 0)
            if isinstance(chol, (int, float)) and chol > 240:
                return 0.20
            return 0.0
        
        elif field_name == 'Age':
            age = facts.get('Age', 0)
            if isinstance(age, (int, float)) and age > 50:
                return 0.15
            return 0.0
        
        elif field_name in ['ExerciseAngina', 'FastingBS']:
            if facts.get(field_name) == 'Yes' or facts.get(field_name) == 1:
                return 0.10
            return 0.0
        
        return 0.0
    
    def _generate_reasoning(self,
                           field_name: str,
                           priority_score: float,
                           current_risk_level: str,
                           facts: Dict) -> Tuple[str, str]:
        """توليد تفسير الأولوية بالعربية والإنجليزية"""
        
        reasoning_template_ar = {
            'ChestPain': f"أهم سؤال! {(' هناك أعراض تحتاج تركيز' if current_risk_level in ['HIGH', 'CRITICAL'] else 'يجب التأكد من عدم وجود أعراض')}",
            'BloodPressure': f"ضروري جداً عند وجود أعراض. الخطر الحالي: {current_risk_level}",
            'Cholesterol': "عامل خطر مهم جداً في أمراض القلب",
            'FastingBS': "السكري يزيد من خطر أمراض القلب",
            'ExerciseAngina': "معلومة حاسمة عن تطور الأعراض",
            'MaxHR': "يساعد في فهم حالة الجهاز القلبي",
            'RestingECG': "فحص مهم لتقييم القلب",
            'Oldpeak': "معايير تشخيصية مهمة",
            'ST_Slope': "مؤشرات متقدمة للخطر",
            'Age': "العمر عامل خطر معروف",
            'Sex': "الجنس يؤثر على مخاطر الإصابة"
        }
        
        reasoning_template_en = {
            'ChestPain': f"Most critical! {(' Symptoms need focus' if current_risk_level in ['HIGH', 'CRITICAL'] else 'Ensure no symptoms')}",
            'BloodPressure': f"Essential especially with symptoms. Current risk: {current_risk_level}",
            'Cholesterol': "Major risk factor in heart disease",
            'FastingBS': "Diabetes increases heart disease risk",
            'ExerciseAngina': "Crucial info about symptom progression",
            'MaxHR': "Helps assess cardiac function",
            'RestingECG': "Important cardiac assessment tool",
            'Oldpeak': "Important diagnostic criteria",
            'ST_Slope': "Advanced risk indicators",
            'Age': "Known age risk factor",
            'Sex': "Affects heart disease susceptibility"
        }
        
        reasoning_ar = reasoning_template_ar.get(
            field_name,
            f"أولوية: {priority_score:.1%}"
        )
        reasoning_en = reasoning_template_en.get(
            field_name,
            f"Priority: {priority_score:.1%}"
        )
        
        return reasoning_ar, reasoning_en
    
    def get_next_question(self,
                         facts: Dict,
                         current_risk_level: str = 'LOW',
                         answered_fields: List[str] = None) -> Optional[QuestionPriority]:
        """
        الحصول على السؤال ذو الأولوية الأعلى
        
        Args:
            facts: الحقائق المجمعة
            current_risk_level: مستوى الخطر
            answered_fields: الحقول المجاب عنها
            
        Returns:
            أولى سؤال ذو أولوية عالية، أو None إذا تمت الإجابة على جميع الأسئلة
        """
        if answered_fields is None:
            answered_fields = []
        
        priorities = self.calculate_priorities(facts, current_risk_level, answered_fields)
        
        if priorities:
            next_q = priorities[0]
            logger.info(f"السؤال التالي: {next_q.field_name} (أولوية: {next_q.priority_score:.2f})")
            return next_q
        
        logger.info("لا توجد أسئلة متبقية")
        return None
    
    def get_critical_questions_first(self,
                                    facts: Dict,
                                    answered_fields: List[str] = None) -> List[QuestionPriority]:
        """
        الحصول على الأسئلة الحرجة أولاً
        """
        if answered_fields is None:
            answered_fields = []
        
        priorities = self.calculate_priorities(facts, 'CRITICAL', answered_fields)
        
        # رشح الأسئلة الحرجة فقط
        critical = [p for p in priorities if p.is_critical]
        
        return critical[:5]  # أعلى 5 أسئلة حرجة
    
    def adjust_priority_based_on_risk(self,
                                     priorities: List[QuestionPriority],
                                     current_risk_level: str) -> List[QuestionPriority]:
        """
        تعديل الأولويات بناءً على مستوى الخطر
        """
        risk_boost = {
            'CRITICAL': 0.30,
            'HIGH': 0.15,
            'MEDIUM': 0.05,
            'LOW': 0.0
        }
        
        boost = risk_boost.get(current_risk_level, 0.0)
        
        for priority in priorities:
            # زيادة أولويات الأسئلة الحرجة عند وجود خطر عالي
            if priority.is_critical and boost > 0:
                priority.priority_score = min(priority.priority_score + boost, 1.0)
        
        # إعادة الترتيب
        priorities.sort(key=lambda x: x.priority_score, reverse=True)
        
        return priorities
    
    def get_priority_distribution(self,
                                 priorities: List[QuestionPriority]) -> Dict:
        """الحصول على توزيع الأولويات"""
        high_priority = [p for p in priorities if p.priority_score >= 0.7]
        medium_priority = [p for p in priorities if 0.3 <= p.priority_score < 0.7]
        low_priority = [p for p in priorities if p.priority_score < 0.3]
        
        return {
            'high': len(high_priority),
            'medium': len(medium_priority),
            'low': len(low_priority),
            'high_list': high_priority,
            'medium_list': medium_priority,
            'low_list': low_priority,
            'total_unanswered': len(priorities)
        }
    
    def should_ask_urgent(self, facts: Dict) -> bool:
        """هل يجب طرح أسئلة عاجلة؟"""
        # إذا كان هناك ألم صدر شديد
        chest_pain = facts.get('ChestPain')
        if chest_pain == 'Yes' or chest_pain == 'Severe':
            return True
        
        # إذا كان ضغط الدم حرج جداً
        bp = facts.get('BloodPressure', '')
        if self._is_critical_bp(bp):
            return True
        
        return False
    
    def _is_critical_bp(self, bp_value) -> bool:
        """هل ضغط الدم حرج جداً؟"""
        try:
            if isinstance(bp_value, str):
                systolic = int(bp_value.split('/')[0])
                diastolic = int(bp_value.split('/')[1])
                return systolic >= 180 or diastolic >= 120
        except:
            pass
        return False


# مثال على الاستخدام
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # إنشاء نظام حساب الأولويات
    scorer = PriorityScorer()
    
    # حقائق المريض
    facts = {
        'Age': 55,
        'ChestPain': 'Yes',
        'BloodPressure': '145/90',
        'Cholesterol': 280
    }
    
    answered = ['Age', 'ChestPain', 'BloodPressure', 'Cholesterol']
    
    print("\n1. حساب الأولويات:")
    print("=" * 60)
    priorities = scorer.calculate_priorities(facts, 'HIGH', answered)
    
    for p in priorities[:5]:
        print(f"\n{p.field_name}:")
        print(f"  أولوية: {p.priority_score:.2f}")
        print(f"  السبب: {p.reasoning_ar}")
        print(f"  مساهمة الخطر: {p.risk_contribution:.2f}")
        print(f"  حرج: {p.is_critical}")
    
    print("\n2. السؤال التالي:")
    print("=" * 60)
    next_q = scorer.get_next_question(facts, 'HIGH', answered)
    if next_q:
        print(f"السؤال: {next_q.field_name}")
        print(f"السبب: {next_q.reasoning_ar}")
    
    print("\n3. الأسئلة الحرجة:")
    print("=" * 60)
    critical = scorer.get_critical_questions_first(facts, answered)
    for c in critical:
        print(f"  - {c.field_name} ({c.priority_score:.2f})")
    
    print("\n4. توزيع الأولويات:")
    print("=" * 60)
    dist = scorer.get_priority_distribution(priorities)
    print(f"أولويات عالية: {dist['high']}")
    print(f"أولويات متوسطة: {dist['medium']}")
    print(f"أولويات منخفضة: {dist['low']}")
