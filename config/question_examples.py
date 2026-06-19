

# قاموس الأمثلة لكل سؤال
QUESTION_EXAMPLES = {
    'Age': {
        'question_ar': 'كم عمرك؟',
        'question_en': 'What is your age?',
        'examples_ar': [
            '55',
            'عمري 55 سنة',
            'أنا أبلغ من العمر 62 عاماً',
            '45 سنة'
        ],
        'examples_en': [
            '55',
            'I am 55 years old',
            '45 years',
            'Age: 62'
        ],
        'tips_ar': 'اكتب عمرك بالأرقام (مثل: 55)',
        'is_first': True  # هذا هو السؤال الأول دائماً
    },
    
    'Sex': {
        'question_ar': 'ما جنسك؟',
        'question_en': 'What is your gender?',
        'examples_ar': [
            'ذكر',
            'أنثى',
            'Male',
            'Female'
        ],
        'examples_en': [
            'Male',
            'Female',
            'M',
            'F'
        ],
        'tips_ar': 'اكتب: ذكر أو أنثى'
    },
    
    'ChestPain': {
        'question_ar': 'هل تشعر بألم في الصدر؟',
        'question_en': 'Do you experience chest pain?',
        'examples_ar': [
            'نعم',
            'لا',
            'أعاني من ألم في الصدر',
            'لدي ألم خفيف',
            'ألم شديد'
        ],
        'examples_en': [
            'Yes',
            'No',
            'I have chest pain',
            'Mild pain',
            'Severe pain'
        ],
        'tips_ar': 'اكتب: نعم أو لا، أو صف الألم'
    },
    
    'BloodPressure': {
        'question_ar': 'ما قراءة ضغط دمك؟',
        'question_en': 'What is your blood pressure?',
        'examples_ar': [
            '140/90',
            '120/80',
            '150/95',
            'ضغطي 130/85',
            'الضغط عندي 145 على 90'
        ],
        'examples_en': [
            '140/90',
            '120/80',
            '150/95',
            'BP: 130/85',
            'Blood pressure 145/90'
        ],
        'tips_ar': 'اكتب بصيغة: رقم/رقم (مثل: 140/90)'
    },
    
    'Cholesterol': {
        'question_ar': 'ما مستوى الكوليسترول لديك؟',
        'question_en': 'What is your cholesterol level?',
        'examples_ar': [
            '280',
            '250',
            '200 mg/dL',
            'الكوليسترول 280',
            'الكوليسترول عندي 250'
        ],
        'examples_en': [
            '280',
            '250 mg/dL',
            'Cholesterol: 280',
            '280 milligrams'
        ],
        'tips_ar': 'اكتب الرقم (مثل: 280)'
    },
    
    'FastingBloodSugar': {
        'question_ar': 'هل لديك سكر الدم مرتفع (السكري)؟',
        'question_en': 'Do you have high fasting blood sugar?',
        'examples_ar': [
            'نعم',
            'لا',
            'عندي سكري',
            'سكر مرتفع',
            'سكر الدم صائم مرتفع'
        ],
        'examples_en': [
            'Yes',
            'No',
            'I have diabetes',
            'High blood sugar',
            'Elevated fasting sugar'
        ],
        'tips_ar': 'اكتب: نعم أو لا'
    },
    
    'RestingECG': {
        'question_ar': 'ما نتيجة رسم القلب (ECG)؟',
        'question_en': 'What is your resting ECG result?',
        'examples_ar': [
            'طبيعي',
            'غير طبيعي',
            'Normal',
            'رسم القلب طبيعي',
            'ECG غير طبيعي'
        ],
        'examples_en': [
            'Normal',
            'Abnormal',
            'ECG normal',
            'Resting ECG abnormal'
        ],
        'tips_ar': 'اكتب: طبيعي أو غير طبيعي'
    },
    
    'MaxHeartRate': {
        'question_ar': 'ما أقصى معدل نبض قلبك؟',
        'question_en': 'What is your maximum heart rate?',
        'examples_ar': [
            '150',
            '120',
            '95 نبضة',
            'نبضات القلب 160',
            'النبض 150 bpm'
        ],
        'examples_en': [
            '150',
            '120 bpm',
            'Heart rate: 160',
            'Max HR 95',
            '150 beats per minute'
        ],
        'tips_ar': 'اكتب الرقم (مثل: 150)'
    },
    
    'ExerciseInducedAngina': {
        'question_ar': 'هل تشعر بألم في الصدر عند ممارسة الرياضة أو المجهود؟',
        'question_en': 'Do you experience chest pain with exercise?',
        'examples_ar': [
            'نعم',
            'لا',
            'ألم عند المجهود',
            'ألم لما أتعب',
            'ألم مع التمرين'
        ],
        'examples_en': [
            'Yes',
            'No',
            'Pain with exercise',
            'Chest pain on exertion',
            'Angina during activity'
        ],
        'tips_ar': 'اكتب: نعم أو لا'
    },
    
    'OldPeak': {
        'question_ar': 'ما درجة انخفاض ST في رسم القلب؟',
        'question_en': 'What is your ST depression?',
        'examples_ar': [
            '2.5',
            '1.0',
            '2.5 ملم',
            'ST انخفاض 2.5'
        ],
        'examples_en': [
            '2.5',
            '1.0 mm',
            'ST depression: 2.5',
            '2.5 millimeters'
        ],
        'tips_ar': 'اكتب الرقم (مثل: 2.5)'
    },
    
    'Slope': {
        'question_ar': 'ما شكل انحدار ST في اختبار الجهد؟',
        'question_en': 'What is the ST slope?',
        'examples_ar': [
            'صاعد',
            'مسطح',
            'هابط',
            'Upsloping',
            'Flat'
        ],
        'examples_en': [
            'Upsloping',
            'Flat',
            'Downsloping'
        ],
        'tips_ar': 'اكتب: صاعد، مسطح، أو هابط'
    }
}


def get_question_info(field_name, language='ar'):
    """
    الحصول على معلومات السؤال
    
    Args:
        field_name: اسم الحقل
        language: اللغة ('ar' أو 'en')
    
    Returns:
        dict: معلومات السؤال
    """
    if field_name not in QUESTION_EXAMPLES:
        return None
    
    info = QUESTION_EXAMPLES[field_name]
    question_key = f'question_{language}'
    examples_key = f'examples_{language}'
    
    return {
        'field': field_name,
        'question': info.get(question_key, ''),
        'examples': info.get(examples_key, []),
        'tips': info.get(f'tips_{language}', ''),
        'is_first': info.get('is_first', False)
    }


def get_first_question(language='ar'):
    """
    الحصول على السؤال الأول (العمر)
    
    Args:
        language: اللغة
    
    Returns:
        dict: معلومات السؤال الأول
    """
    return get_question_info('Age', language)


def format_examples_html(examples, max_count=4):
    """
    تنسيق الأمثلة كـ HTML
    
    Args:
        examples: قائمة الأمثلة
        max_count: أقصى عدد من الأمثلة للعرض
    
    Returns:
        str: HTML للأمثلة
    """
    if not examples:
        return ""
    
    examples_to_show = examples[:max_count]
    examples_list = "<br>".join([f"• {ex}" for ex in examples_to_show])
    
    return f"""
    <div style='margin-top: 10px; padding: 12px; background: rgba(156,39,176,0.08); 
                border-radius: 8px; border-left: 3px solid #9c27b0;'>
        <strong style='color: #7b1fa2;'> أمثلة على الإجابة:</strong><br>
        <span style='color: #555; font-size: 0.95rem;'>{examples_list}</span>
    </div>
    """
