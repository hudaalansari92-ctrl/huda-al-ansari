
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger('dynamic_question_selector')


@dataclass
class Question:
    """تعريف سؤال"""
    field_name: str
    question_ar: str  # السؤال بالعربية
    question_en: str  # السؤال بالإنجليزية
    question_type: str  # text, number, choice, yesno
    choices_ar: Optional[List[str]] = None
    choices_en: Optional[List[str]] = None
    validation_rules: Optional[Dict] = None
    examples_ar: Optional[List[str]] = None
    examples_en: Optional[List[str]] = None
    follow_up_questions: Optional[List[str]] = None


class DynamicQuestionSelector:
    """
    نظام اختيار الأسئلة الديناميكي
    يختار السؤال التالي بناءً على الحقائق والأولويات الحالية
    """
    
    def __init__(self):
        """تهيئة نظام اختيار الأسئلة"""
        self.questions = self._initialize_questions()
        self.question_order = []  # ترتيب الأسئلة الديناميكي
        self.asked_questions = []  # الأسئلة التي تم طرحها
    
    def _initialize_questions(self) -> Dict[str, Question]:
        """تهيئة قائمة الأسئلة المتاحة"""
        return {
            'Age': Question(
                field_name='Age',
                question_ar="كم عمرك؟",
                question_en="What is your age?",
                question_type='number',
                validation_rules={'min': 0, 'max': 150},
                examples_ar=["55", "عمري 55 سنة", "55 سنة"],
                examples_en=["55", "I am 55 years old", "55 years"]
            ),
            'Sex': Question(
                field_name='Sex',
                question_ar="ما جنسك؟",
                question_en="What is your gender?",
                question_type='choice',
                choices_ar=["ذكر", "أنثى"],
                choices_en=["Male", "Female"],
                examples_ar=["ذكر", "أنثى"],
                examples_en=["Male", "Female"]
            ),
            'ChestPain': Question(
                field_name='ChestPain',
                question_ar="هل تشعر بألم في الصدر؟",
                question_en="Do you experience chest pain?",
                question_type='yesno',
                choices_ar=["نعم", "لا"],
                choices_en=["Yes", "No"],
                follow_up_questions=['ExerciseAngina', 'Oldpeak'],
                examples_ar=["نعم", "لا", "ألم خفيف", "ألم نموذجي TA"]
            ),
            'BloodPressure': Question(
                field_name='BloodPressure',
                question_ar="ما قراءة ضغط دمك؟",
                question_en="What is your blood pressure reading?",
                question_type='text',
                validation_rules={'pattern': r'\d{2,3}/\d{2,3}'},
                examples_ar=["145/90", "120/80", "130/85"],
                examples_en=["145/90", "120/80", "130/85"]
            ),
            'Cholesterol': Question(
                field_name='Cholesterol',
                question_ar="ما مستوى الكوليسترول لديك؟",
                question_en="What is your cholesterol level?",
                question_type='number',
                validation_rules={'min': 0, 'max': 1000},
                examples_ar=["280", "280 mg/dL", "280 ملغ/ديسيلتر"],
                examples_en=["280", "280 mg/dL", "280 milligrams"]
            ),
            'FastingBS': Question(
                field_name='FastingBS',
                question_ar="هل لديك سكر الدم مرتفع (السكري)؟",
                question_en="Do you have high fasting blood sugar (diabetes)?",
                question_type='yesno',
                choices_ar=["نعم", "لا"],
                choices_en=["Yes", "No"],
                examples_ar=["نعم", "لا", "سكر صائم مرتفع", "Fasting BS: 1"]
            ),
            'RestingECG': Question(
                field_name='RestingECG',
                question_ar="ما نتيجة رسم القلب (ECG)؟",
                question_en="What is your resting ECG result?",
                question_type='choice',
                choices_ar=["طبيعي", "غير طبيعي"],
                choices_en=["Normal", "Abnormal"],
                examples_ar=["طبيعي", "غير طبيعي"]
            ),
            'MaxHR': Question(
                field_name='MaxHR',
                question_ar="ما أقصى معدل نبض قلبك؟",
                question_en="What is your maximum heart rate?",
                question_type='number',
                validation_rules={'min': 30, 'max': 220},
                examples_ar=["150", "160 bpm", "معدل القلب الأقصى 140"],
                examples_en=["150", "160 bpm", "Max HR 140"]
            ),
            'ExerciseAngina': Question(
                field_name='ExerciseAngina',
                question_ar="هل تشعر بألم في الصدر عند ممارسة الرياضة أو المجهود؟",
                question_en="Do you experience chest pain with exercise?",
                question_type='yesno',
                choices_ar=["نعم", "لا"],
                choices_en=["Yes", "No"],
                examples_ar=["نعم", "لا", "ألم عند المجهود", "Exercise angina: Yes"]
            ),
            'Oldpeak': Question(
                field_name='Oldpeak',
                question_ar="ما درجة انخفاض ST في رسم القلب (mm)؟",
                question_en="What is your ST depression (mm)?",
                question_type='number',
                validation_rules={'min': 0, 'max': 10},
                examples_ar=["2.5", "2.5 ملم", "1.0", "انخفاض ST: 2.5"],
                examples_en=["2.5", "2.5 mm", "1.0", "ST depression 2.5"]
            ),
            'ST_Slope': Question(
                field_name='ST_Slope',
                question_ar="ما شكل انحدار ST في اختبار الجهد؟",
                question_en="What is the ST segment slope?",
                question_type='choice',
                choices_ar=["صاعد", "مسطح", "هابط"],
                choices_en=["Up", "Flat", "Down"],
                examples_ar=["صاعد", "مسطح", "هابط", "ميل ST مسطح"],
                examples_en=["Up", "Flat", "Down", "ST Slope: Flat"]
            )
        }
    
    def get_question(self,
                    field_name: str,
                    language: str = 'ar') -> Optional[Question]:
        """
        الحصول على سؤال معين
        
        Args:
            field_name: اسم الحقل
            language: اللغة ('ar' أو 'en')
            
        Returns:
            كائن السؤال أو None
        """
        return self.questions.get(field_name)
    
    def select_next_question(self,
                            priorities: List,
                            facts: Dict,
                            language: str = 'ar') -> Optional[Dict]:
        """
        اختيار السؤال التالي بناءً على الأولويات
        
        Args:
            priorities: قائمة الأولويات من PriorityScorer
            facts: الحقائق المجمعة
            language: اللغة
            
        Returns:
            كائن السؤال مع البيانات الكاملة أو None
        """
        # الحصول على أول سؤال ذو أولوية عالية
        if not priorities:
            logger.warning("لا توجد أولويات متاحة")
            return None
        
        for priority in priorities:
            field_name = priority.field_name
            
            # تخطي الحقول التي تمت الإجابة عليها
            if field_name in facts and facts[field_name]:
                continue
            
            # الحصول على السؤال
            question = self.get_question(field_name, language)
            if not question:
                continue
            
            # تسجيل السؤال
            self.asked_questions.append(field_name)
            logger.info(f"تم اختيار السؤال: {field_name} (أولوية: {priority.priority_score:.2f})")
            
            # بناء استجابة شاملة
            return {
                'field_name': question.field_name,
                'question': question.question_ar if language == 'ar' else question.question_en,
                'question_type': question.question_type,
                'choices': question.choices_ar if language == 'ar' else question.choices_en,
                'examples': question.examples_ar if language == 'ar' else question.examples_en,
                'priority': priority.priority_score,
                'is_critical': priority.is_critical,
                'reasoning': priority.reasoning_ar if language == 'ar' else priority.reasoning_en,
                'validation_rules': question.validation_rules,
                'follow_up': question.follow_up_questions
            }
        
        logger.info("لا توجد أسئلة متبقية")
        return None
    
    def get_adaptive_question(self,
                             priorities: List,
                             facts: Dict,
                             current_risk_level: str,
                             language: str = 'ar') -> Optional[Dict]:
        """
        اختيار سؤال متكيف بناءً على مستوى الخطر
        
        إذا كان الخطر عالياً، اسأل الأسئلة الحرجة أولاً
        إذا كان الخطر منخفضاً، يمكن السؤال بشكل متدرج
        """
        if current_risk_level in ['CRITICAL', 'HIGH']:
            # أسئلة حرجة فقط
            critical_priorities = [p for p in priorities if p.is_critical]
            if critical_priorities:
                return self.select_next_question(critical_priorities, facts, language)
        
        # الأسئلة العادية
        return self.select_next_question(priorities, facts, language)
    
    def get_sequential_questions(self,
                                priorities: List,
                                facts: Dict,
                                count: int = 3,
                                language: str = 'ar') -> List[Dict]:
        """
        الحصول على عدة أسئلة متتالية
        
        Args:
            priorities: الأولويات
            facts: الحقائق
            count: عدد الأسئلة
            language: اللغة
            
        Returns:
            قائمة الأسئلة التالية
        """
        questions = []
        
        for _ in range(count):
            q = self.select_next_question(priorities, facts, language)
            if q:
                questions.append(q)
                # إضافة حقيقة مؤقتة لتخطي هذا السؤال في التكرار التالي
                facts[q['field_name']] = '__placeholder__'
            else:
                break
        
        return questions
    
    def get_follow_up_questions(self,
                               field_name: str,
                               language: str = 'ar') -> List[str]:
        """
        الحصول على الأسئلة المتابعة لسؤال معين
        
        مثال: بعد سؤال "هل تشعر بألم صدر؟"
        الأسئلة المتابعة: "هل الألم يأتي مع المجهود؟"
        """
        question = self.get_question(field_name)
        if question and question.follow_up_questions:
            return question.follow_up_questions
        return []
    
    def customize_question(self,
                          field_name: str,
                          custom_text_ar: str,
                          custom_text_en: str,
                          language: str = 'ar') -> Optional[Dict]:
        """
        تخصيص نص السؤال بناءً على السياق
        
        مثال: إذا كان هناك علامات خطر، اجعل السؤال أكثر حدة
        """
        question = self.get_question(field_name)
        if not question:
            return None
        
        return {
            'field_name': question.field_name,
            'question': custom_text_ar if language == 'ar' else custom_text_en,
            'question_type': question.question_type,
            'choices': question.choices_ar if language == 'ar' else question.choices_en,
            'examples': question.examples_ar if language == 'ar' else question.examples_en
        }
    
    def adjust_questions_for_risk(self,
                                 priorities: List,
                                 current_risk_level: str) -> List:
        """
        تعديل الأسئلة بناءً على مستوى الخطر
        
        الخطر العالي = أسئلة مركزة على الأعراض
        الخطر المنخفض = أسئلة أكثر استرخاءً
        """
        adjusted = []
        
        for priority in priorities:
            if current_risk_level == 'CRITICAL':
                # ركز على الأسئلة الحرجة
                if priority.is_critical:
                    adjusted.append(priority)
            
            elif current_risk_level == 'HIGH':
                # أولويات عالية ومتوسطة
                if priority.priority_score >= 0.5:
                    adjusted.append(priority)
            
            else:
                # جميع الأسئلة
                adjusted.append(priority)
        
        return adjusted
    
    def get_question_statistics(self) -> Dict:
        """إحصائيات الأسئلة"""
        return {
            'total_questions': len(self.questions),
            'questions_asked': len(set(self.asked_questions)),
            'questions_remaining': len(self.questions) - len(set(self.asked_questions)),
            'asked_list': list(set(self.asked_questions)),
            'available_questions': list(self.questions.keys())
        }
    
    def reset(self):
        """إعادة تعيين الحالة"""
        self.question_order = []
        self.asked_questions = []
        logger.info("تم إعادة تعيين نظام اختيار الأسئلة")


# مثال على الاستخدام
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    from priority_scorer import PriorityScorer
    
    # إنشاء الأنظمة
    scorer = PriorityScorer()
    selector = DynamicQuestionSelector()
    
    # حقائق المريض
    facts = {
        'Age': 55,
    }
    
    answered = ['Age']
    
    print("\n1. اختيار السؤال التالي:")
    print("=" * 60)
    
    # حساب الأولويات
    priorities = scorer.calculate_priorities(facts, 'HIGH', answered)
    
    # اختيار السؤال
    next_q = selector.select_next_question(priorities, facts, language='ar')
    
    if next_q:
        print(f"السؤال: {next_q['question']}")
        print(f"النوع: {next_q['question_type']}")
        print(f"الأولوية: {next_q['priority']:.2f}")
        print(f"السبب: {next_q['reasoning']}")
        if next_q['choices']:
            print(f"الخيارات: {', '.join(next_q['choices'])}")
        if next_q['examples']:
            print(f"أمثلة: {', '.join(next_q['examples'])}")
    
    print("\n2. الأسئلة المتابعة:")
    print("=" * 60)
    follow_ups = selector.get_follow_up_questions('ChestPain')
    for fu in follow_ups:
        print(f"  - {fu}")
    
    print("\n3. إحصائيات الأسئلة:")
    print("=" * 60)
    stats = selector.get_question_statistics()
    print(f"إجمالي الأسئلة: {stats['total_questions']}")
    print(f"الأسئلة المطروحة: {stats['questions_asked']}")
    print(f"الأسئلة المتبقية: {stats['questions_remaining']}")
