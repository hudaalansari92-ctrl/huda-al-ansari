"""
Centralized translation dictionary for Arabic/English UI
"""

UI_TEXT = {
    'ar': {
        # Page config
        'page_title': 'نظام شات بوت للرعاية الصحية مبني على التقنيات الذكية',
        'page_subtitle': 'Healthcare Chatbot System Based on Intelligent Techniques',
        'header_title': 'نظام شات بوت للرعاية الصحية مبني على التقنيات الذكية',

        # Sidebar - Control Panel
        'control_panel': 'لوحة التحكم',
        'new_session': 'بدء جلسة جديدة',
        'current_session': 'الجلسة الحالية',
        'facts_collected': 'الحقائق المجموعة',
        'risk_level': 'مستوى الخطر',
        'confidence': 'الثقة',

        # Sidebar - Dashboard
        'dashboard': 'لوحة المعلومات',
        'no_facts': 'لم يتم جمع حقائق بعد',
        'not_assessed': 'لم يتم التقييم بعد',

        # Sidebar - Examples
        'writing_examples': 'أمثلة على طرق الكتابة',

        # Sidebar - Previous Sessions
        'previous_sessions': 'الجلسات السابقة',
        'load': 'تحميل',
        'delete': 'حذف',
        'loaded': 'تم التحميل!',
        'no_sessions': 'لا توجد جلسات محفوظة',
        'date': 'التاريخ',
        'facts': 'الحقائق',

        # Sidebar - Language
        'language': 'اللغة',
        'choose_language': 'اختر اللغة',

        # Main area - No session
        'start_session_prompt': 'الرجاء بدء جلسة جديدة من الشريط الجانبي',
        'smart_system_title': 'نظام ذكي',
        'smart_system_items': ['حوار ذاتي داخلي', 'استنتاج تلقائي', 'أولويات ديناميكية'],
        'safe_storage_title': 'تخزين آمن',
        'safe_storage_items': ['حفظ جميع الخطوات', 'تتبع كامل للحقائق', 'استرجاع الجلسات'],
        'accurate_analysis_title': 'تحليل دقيق',
        'accurate_analysis_items': ['تقييم مستوى الخطر', 'تحذيرات فورية', 'تقارير شاملة'],

        # Main area - Dialog
        'dialog_area': 'منطقة الحوار',
        'tell_health': 'أخبرني عن حالتك الصحية',
        'next_question_label': 'السؤال التالي',
        'write_info': 'اكتب معلوماتك هنا:',
        'write_placeholder': 'مثال: عمري 55 سنة، أعاني من ألم في الصدر أحياناً، ضغط الدم عندي 140/90، والكوليسترول 250...',
        'write_help': 'اكتب بأي طريقة تريد - بالعربية أو الإنجليزية',
        'analyze_send': 'تحليل وإرسال',
        'clear': 'مسح',

        # Progress
        'progress': 'التقدم',
        'progress_text': 'تم جمع {done} من {total} حقيقة ({pct}%)',
        'remaining_fields': 'الحقول المتبقية',
        'completed_fields': 'الحقول المُكتملة',
        'field': 'حقل',
        'remaining': 'المتبقية',
        'can_write': 'يمكنك كتابة أي منها أو كلها في حقل الإدخال بالأسفل',

        # Processing results
        'great_processed': 'رائع! تم فهم ومعالجة **{count}** معلومة بنجاح!',
        'info_understood': 'المعلومات التي فهمتها منك:',
        'could_not_understand': 'لم أتمكن من فهم بعض الأجزاء: {parts}',
        'info_saved': 'تم حفظ المعلومات بنجاح!',
        'write_first': 'الرجاء كتابة معلوماتك أولاً',
        'all_collected': 'تم جمع جميع الحقائق!',
        'continue_next': 'متابعة للسؤال التالي',
        'transitioning': 'جاري الانتقال للسؤال التالي...',
        'could_not_extract': 'لم أتمكن من استخراج معلومات واضحة من النص.',
        'tips_title': 'نصائح للحصول على نتائج أفضل:',
        'tip1': 'استخدم أرقام واضحة (مثل: 55، 140/90)',
        'tip2': 'اذكر الكلمات المفتاحية (عمر، ضغط، كوليسترول، ألم)',
        'tip3': 'يمكنك الكتابة بالعربية أو الإنجليزية',
        'tip4': 'جرب صياغة مختلفة للجمل',
        'attempt_counter': '⚠️ محاولة {n}/{max} — {purpose}',
        'attempt_purpose_example': 'مع مثال',
        'attempt_purpose_last': 'آخر محاولة + تحذير',
        'auto_skipped': '⏭️ تم تخطّي السؤال تلقائياً بعد {max} محاولات. تم تسجيل القيمة الطبيعية الافتراضية ({value}) — يستطيع الطبيب مراجعتها لاحقاً.',
        'skipped_badge': 'مُتخطى',

        # Assessment
        'comprehensive_assessment': 'التقييم الشامل - Comprehensive Assessment',
        'section1_domain': 'القسم الأول: تحليل القواعد الطبية',
        'section1_subtitle': 'Domain Rules Analysis',
        'risk_level_label': 'مستوى الخطر',
        'rules_applied': 'القواعد المُطبقة',
        'risk_factors': 'عوامل الخطر',
        'recommendations': 'التوصيات',

        'section2_features': 'القسم الثاني: الخصائص المتقدمة',
        'section2_subtitle': 'Advanced Features Summary',
        'classification': 'التصنيف:',
        'age': 'العمر',
        'cholesterol': 'الكوليسترول',
        'blood_pressure': 'ضغط الدم',
        'physical_capacity': 'القدرة البدنية:',
        'capacity': 'القدرة',
        'total_features': 'إجمالي الخصائص المولدة:',

        'section3_ml': 'القسم الثالث: تنبؤ نموذج التعلم الآلي',
        'section3_subtitle': 'ML Model Prediction',
        'prediction': 'التنبؤ',
        'positive': 'إيجابي',
        'negative': 'سلبي',
        'probability': 'الاحتمالية',
        'source': 'المصدر',

        'section4_decision': 'القسم الرابع: القرار النهائي الشامل',
        'section4_subtitle': 'Final Comprehensive Decision',
        'final_decision': 'القرار النهائي',
        'reasoning': 'التفسير',
        'decision_sources': 'مصادر القرار',
        'medical_rules': 'القواعد الطبية:',
        'ml_model': 'نموذج ML:',
        'applied_rules': 'القواعد المطبقة',
        'final_recommendations': 'التوصيات النهائية',

        'decision_tree_title': 'Rule-Based Decision Tree Visualization',
        'decision_tree_subtitle': 'رسم شجرة القرار - Graphviz Style',
        'tab_tree': 'Decision Tree Diagram',
        'tab_rules': 'Decision Rules Table',
        'tab_flow': 'Process Flow',

        'show_full_json': 'عرض التقييم الكامل (JSON)',
        'show_legacy': 'عرض التقرير النهائي (Legacy)',

        # Conversation display
        'first_question': 'السؤال الأول',
        'basic_question': 'سؤال أساسي',
        'first_q_note': 'هذا السؤال الأساسي الذي يبدأ به التشخيص دائماً',
        'answer_examples': 'أمثلة على الإجابة',
        'note': 'ملاحظة:',
        'you': 'أنت',
        'analysis': 'التحليل',
        'inference': 'الاستنتاج',
        'decision_label': 'القرار',
        'important_warning': 'تحذير مهم',
        'why_important': 'لماذا هذا السؤال مهم؟',
        'next_important_q': 'السؤال التالي الأهم',
        'smart_system': 'النظام الذكي',
        'priority_critical': 'عالية جداً',
        'priority_high': 'عالية',
        'priority_medium': 'متوسطة',
        'priority_normal': 'عادية',

        # Conversation & Facts table
        'conversation': 'المحادثة',
        'col_field': 'الحقل',
        'col_value': 'القيمة',
        'col_time': 'الوقت',

        # Groq AI (v7.0.0)
        'groq_settings': 'إعدادات الذكاء الاصطناعي',
        'groq_api_key': 'مفتاح Groq API',
        'groq_help': 'أدخل مفتاح Groq API للحصول على تفسير ذكي وتوصيات مخصصة',
        'groq_connected': 'تم الاتصال بـ Groq AI بنجاح!',
        'groq_error': 'فشل الاتصال بـ Groq API. تحقق من المفتاح.',
        'groq_optional': 'اختياري — النظام يعمل بدونه',
        'groq_not_connected': 'أدخل مفتاح Groq API في الشريط الجانبي للحصول على تفسير ذكي وتوصيات مخصصة بالذكاء الاصطناعي.',
        'section5_groq': 'القسم 5: تحليل الذكاء الاصطناعي',
        'section5_subtitle': 'تفسير النتائج وتوصيات مخصصة باستخدام Groq AI',
        'ai_interpretation': 'تفسير الذكاء الاصطناعي',
        'personalized_recommendations': 'توصيات مخصصة لحالتك',
        'powered_by_groq': 'مدعوم بـ Groq AI (llama-3.3-70b-versatile)',

        # Smart Conversation (v8.0.0)
        'smart_mode_active': 'الوضع الذكي مفعّل',
        'smart_mode_badge': 'محادثة ذكية',
        'classic_mode_badge': 'الوضع الكلاسيكي',
        'doctor_label': 'الطبيب',
        'patient_label': 'المريض',
        'smart_extracting': 'جاري تحليل إجابتك...',
        'fields_extracted': 'تم استخراج {count} معلومة',
        'smart_fallback_notice': 'تم التبديل للوضع الكلاسيكي مؤقتاً',
        'type_your_message': 'اكتب رسالتك هنا...',
        'send_message': 'إرسال',
        'smart_greeting_default': 'مرحباً بك! أخبرني عن نفسك وعن أي شكوى تعاني منها.',
        'ack_understand': 'أفهم، شكراً لك على المعلومة.',
        'ack_with_field': 'أفهم، تم تسجيل {label}: {value}.',
        'ack_next_question_prefix': 'الآن سؤالي التالي:',
        'all_fields_collected': 'تم جمع جميع المعلومات المطلوبة! جاري تحضير التقييم...',
        'extracted_info_label': 'المعلومات المستخرجة',

        # Voice Input / Output
        'voice_btn': 'سجل رسالتك الصوتية',
        'voice_recording': 'جاري تحويل الصوت إلى نص...',
        'voice_stopped': 'تم إيقاف التسجيل',
        'voice_not_supported': 'تعذر تحويل الصوت إلى نص',
        'listen_btn': 'استماع',
        'listening_now': 'جاري القراءة...',

        # Footer
        'footer_text': 'نظام الحوار الطبي الذكي | Medical Intelligent Dialog System',
        'footer_powered': 'Powered by Self-Reasoning AI + Groq AI • Made with ',

        # Risk gauge
        'risk_gauge_title': 'مستوى الخطر',

        # Session messages
        'session_started': 'تم بدء جلسة جديدة: {sid}',
        'start_session_first': 'الرجاء بدء جلسة جديدة أولاً!',

        # Field names
        'field_names': {
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
            'ST_Slope': 'ميل ST',
        },
    },

    'en': {
        # Page config
        'page_title': 'Healthcare Chatbot System Based on Intelligent Techniques',
        'page_subtitle': 'Healthcare Chatbot System Based on Intelligent Techniques',
        'header_title': 'Healthcare Chatbot System Based on Intelligent Techniques',

        # Sidebar - Control Panel
        'control_panel': 'Control Panel',
        'new_session': 'Start New Session',
        'current_session': 'Current Session',
        'facts_collected': 'Facts Collected',
        'risk_level': 'Risk Level',
        'confidence': 'Confidence',

        # Sidebar - Dashboard
        'dashboard': 'Dashboard',
        'no_facts': 'No facts collected yet',
        'not_assessed': 'Not assessed yet',

        # Sidebar - Examples
        'writing_examples': 'Writing Examples',

        # Sidebar - Previous Sessions
        'previous_sessions': 'Previous Sessions',
        'load': 'Load',
        'delete': 'Delete',
        'loaded': 'Loaded!',
        'no_sessions': 'No saved sessions',
        'date': 'Date',
        'facts': 'Facts',

        # Sidebar - Language
        'language': 'Language',
        'choose_language': 'Choose Language',

        # Main area - No session
        'start_session_prompt': 'Please start a new session from the sidebar',
        'smart_system_title': 'Smart System',
        'smart_system_items': ['Internal self-dialog', 'Auto inference', 'Dynamic priorities'],
        'safe_storage_title': 'Secure Storage',
        'safe_storage_items': ['Save all steps', 'Full fact tracking', 'Session recovery'],
        'accurate_analysis_title': 'Accurate Analysis',
        'accurate_analysis_items': ['Risk level assessment', 'Instant warnings', 'Comprehensive reports'],

        # Main area - Dialog
        'dialog_area': 'Dialog Area',
        'tell_health': 'Tell me about your health',
        'next_question_label': 'Next Question',
        'write_info': 'Write your information here:',
        'write_placeholder': 'Example: I am 55 years old, I have chest pain sometimes, blood pressure 140/90, cholesterol 250...',
        'write_help': 'Write in any way you want - in Arabic or English',
        'analyze_send': 'Analyze & Send',
        'clear': 'Clear',

        # Progress
        'progress': 'Progress',
        'progress_text': 'Collected {done} of {total} facts ({pct}%)',
        'remaining_fields': 'Remaining Fields',
        'completed_fields': 'Completed Fields',
        'field': 'field',
        'remaining': 'Remaining',
        'can_write': 'You can write any or all of them in the input field below',

        # Processing results
        'great_processed': 'Great! Successfully processed **{count}** piece(s) of information!',
        'info_understood': 'Information understood from you:',
        'could_not_understand': 'Could not understand some parts: {parts}',
        'info_saved': 'Information saved successfully!',
        'write_first': 'Please write your information first',
        'all_collected': 'All facts have been collected!',
        'continue_next': 'Continue to Next Question',
        'transitioning': 'Transitioning to next question...',
        'could_not_extract': 'Could not extract clear information from the text.',
        'tips_title': 'Tips for better results:',
        'attempt_counter': '⚠️ Attempt {n}/{max} — {purpose}',
        'attempt_purpose_example': 'with example',
        'attempt_purpose_last': 'last try + warning',
        'auto_skipped': '⏭️ Skipped automatically after {max} attempts. Recorded the clinical default ({value}) so the doctor can review it later.',
        'skipped_badge': 'Skipped',
        'tip1': 'Use clear numbers (e.g.: 55, 140/90)',
        'tip2': 'Mention keywords (age, pressure, cholesterol, pain)',
        'tip3': 'You can write in Arabic or English',
        'tip4': 'Try different phrasing',

        # Assessment
        'comprehensive_assessment': 'Comprehensive Assessment',
        'section1_domain': 'Section 1: Medical Rules Analysis',
        'section1_subtitle': 'Domain Rules Analysis',
        'risk_level_label': 'Risk Level',
        'rules_applied': 'Rules Applied',
        'risk_factors': 'Risk Factors',
        'recommendations': 'Recommendations',

        'section2_features': 'Section 2: Advanced Features',
        'section2_subtitle': 'Advanced Features Summary',
        'classification': 'Classification:',
        'age': 'Age',
        'cholesterol': 'Cholesterol',
        'blood_pressure': 'Blood Pressure',
        'physical_capacity': 'Physical Capacity:',
        'capacity': 'Capacity',
        'total_features': 'Total generated features:',

        'section3_ml': 'Section 3: ML Model Prediction',
        'section3_subtitle': 'ML Model Prediction',
        'prediction': 'Prediction',
        'positive': 'Positive',
        'negative': 'Negative',
        'probability': 'Probability',
        'source': 'Source',

        'section4_decision': 'Section 4: Final Comprehensive Decision',
        'section4_subtitle': 'Final Comprehensive Decision',
        'final_decision': 'Final Decision',
        'reasoning': 'Reasoning',
        'decision_sources': 'Decision Sources',
        'medical_rules': 'Medical Rules:',
        'ml_model': 'ML Model:',
        'applied_rules': 'Applied Rules',
        'final_recommendations': 'Final Recommendations',

        'decision_tree_title': 'Rule-Based Decision Tree Visualization',
        'decision_tree_subtitle': 'Decision Tree Diagram - Graphviz Style',
        'tab_tree': 'Decision Tree Diagram',
        'tab_rules': 'Decision Rules Table',
        'tab_flow': 'Process Flow',

        'show_full_json': 'Show Full Assessment (JSON)',
        'show_legacy': 'Show Final Report (Legacy)',

        # Conversation display
        'first_question': 'First Question',
        'basic_question': 'Basic Question',
        'first_q_note': 'This is the basic question that always starts the diagnosis',
        'answer_examples': 'Answer Examples',
        'note': 'Note:',
        'you': 'You',
        'analysis': 'Analysis',
        'inference': 'Inference',
        'decision_label': 'Decision',
        'important_warning': 'Important Warning',
        'why_important': 'Why is this question important?',
        'next_important_q': 'Most Important Next Question',
        'smart_system': 'Smart System',
        'priority_critical': 'Very High',
        'priority_high': 'High',
        'priority_medium': 'Medium',
        'priority_normal': 'Normal',

        # Conversation & Facts table
        'conversation': 'Conversation',
        'col_field': 'Field',
        'col_value': 'Value',
        'col_time': 'Time',

        # Groq AI (v7.0.0)
        'groq_settings': 'AI Settings',
        'groq_api_key': 'Groq API Key',
        'groq_help': 'Enter your Groq API key for AI-powered interpretation and personalized recommendations',
        'groq_connected': 'Connected to Groq AI successfully!',
        'groq_error': 'Failed to connect to Groq API. Check your key.',
        'groq_optional': 'Optional — system works without it',
        'groq_not_connected': 'Enter your Groq API key in the sidebar for AI-powered interpretation and personalized recommendations.',
        'section5_groq': 'Section 5: AI Analysis',
        'section5_subtitle': 'Result interpretation and personalized recommendations powered by Groq AI',
        'ai_interpretation': 'AI Interpretation',
        'personalized_recommendations': 'Personalized Recommendations',
        'powered_by_groq': 'Powered by Groq AI (llama-3.3-70b-versatile)',

        # Smart Conversation (v8.0.0)
        'smart_mode_active': 'Smart Mode Active',
        'smart_mode_badge': 'Smart Conversation',
        'classic_mode_badge': 'Classic Mode',
        'doctor_label': 'Doctor',
        'patient_label': 'Patient',
        'smart_extracting': 'Analyzing your response...',
        'fields_extracted': '{count} field(s) extracted',
        'smart_fallback_notice': 'Temporarily switched to classic mode',
        'type_your_message': 'Type your message here...',
        'send_message': 'Send',
        'smart_greeting_default': 'Welcome! Please tell me about yourself and any concerns you may have.',
        'ack_understand': 'I understand, thank you for sharing.',
        'ack_with_field': 'I understand — recorded {label}: {value}.',
        'ack_next_question_prefix': 'Now my next question is:',
        'all_fields_collected': 'All required information collected! Preparing assessment...',
        'extracted_info_label': 'Extracted Information',

        # Voice Input / Output
        'voice_btn': 'Record your voice message',
        'voice_recording': 'Converting speech to text...',
        'voice_stopped': 'Recording stopped',
        'voice_not_supported': 'Could not convert speech to text',
        'listen_btn': 'Listen',
        'listening_now': 'Reading...',

        # Footer
        'footer_text': 'Medical Intelligent Dialog System',
        'footer_powered': 'Powered by Self-Reasoning AI + Groq AI • Made with ',

        # Risk gauge
        'risk_gauge_title': 'Risk Level',

        # Session messages
        'session_started': 'New session started: {sid}',
        'start_session_first': 'Please start a new session first!',

        # Field names
        'field_names': {
            'Age': 'Age',
            'Sex': 'Sex',
            'ChestPain': 'Chest Pain',
            'BloodPressure': 'Blood Pressure',
            'Cholesterol': 'Cholesterol',
            'FastingBS': 'Fasting Blood Sugar',
            'RestingECG': 'Resting ECG',
            'MaxHR': 'Max Heart Rate',
            'ExerciseAngina': 'Exercise Angina',
            'Oldpeak': 'ST Depression',
            'ST_Slope': 'ST Slope',
        },
    },
}


# Sidebar writing examples HTML - per language
EXAMPLES_HTML = {
    'ar': """
    <style>
        .ex-card { background: #f8fafc; border-radius: 8px; padding: 10px 12px; margin-bottom: 8px; border-right: 4px solid #6366f1; }
        .ex-card h4 { color: #4f46e5; margin: 0 0 6px 0; font-size: 13px; }
        .ex-row { display: flex; flex-wrap: wrap; gap: 5px; }
        .ex-chip { background: #e0e7ff; color: #3730a3; padding: 3px 8px; border-radius: 12px; font-size: 12px; white-space: nowrap; }
        .ex-chip.en { background: #dbeafe; color: #1e40af; }
        .ex-section { margin-bottom: 12px; }
        .ex-section-title { color: #6366f1; font-weight: bold; font-size: 14px; margin-bottom: 8px; padding-bottom: 4px; border-bottom: 2px solid #e0e7ff; }
        .ex-full { background: linear-gradient(135deg, #ede9fe, #e0e7ff); border-radius: 8px; padding: 10px 12px; margin-top: 10px; border-right: 4px solid #7c3aed; }
        .ex-full h4 { color: #7c3aed; margin: 0 0 6px 0; font-size: 13px; }
        .ex-full code { display: block; background: #fff; padding: 8px; border-radius: 6px; font-size: 11px; line-height: 1.6; white-space: pre-wrap; color: #334155; }
    </style>
    <div class="ex-section">
        <div class="ex-section-title">معلومات أساسية</div>
        <div class="ex-card"><h4>العمر</h4><div class="ex-row"><span class="ex-chip">عمري 55 سنة</span><span class="ex-chip">أبلغ 62 عاماً</span><span class="ex-chip en">Age 70</span><span class="ex-chip en">I am 45 years old</span><span class="ex-chip">العمر: 58</span></div></div>
        <div class="ex-card"><h4>الجنس</h4><div class="ex-row"><span class="ex-chip">ذكر</span><span class="ex-chip">أنثى</span><span class="ex-chip">رجل</span><span class="ex-chip">امرأة</span><span class="ex-chip en">Male</span><span class="ex-chip en">Female</span><span class="ex-chip en">M / F</span></div></div>
        <div class="ex-card"><h4>ألم الصدر</h4><div class="ex-row"><span class="ex-chip">ألم صدر نموذجي</span><span class="ex-chip">لدي ألم بالصدر</span><span class="ex-chip">ألم غير نموذجي</span><span class="ex-chip">لا يوجد ألم</span><span class="ex-chip en">TA / ATA / NAP / ASY</span><span class="ex-chip en">Typical Angina</span></div></div>
    </div>
    <div class="ex-section">
        <div class="ex-section-title">معلومات القلب</div>
        <div class="ex-card"><h4>ضغط الدم</h4><div class="ex-row"><span class="ex-chip">ضغط الدم 140/90</span><span class="ex-chip">الضغط 130/85</span><span class="ex-chip">ضغطي 150/100</span><span class="ex-chip en">BP: 145/95</span><span class="ex-chip en">Blood pressure 120/80</span></div></div>
        <div class="ex-card"><h4>الكوليسترول</h4><div class="ex-row"><span class="ex-chip">الكوليسترول 250</span><span class="ex-chip">كوليسترول: 220</span><span class="ex-chip en">Cholesterol 280</span><span class="ex-chip en">Chol: 310</span></div></div>
        <div class="ex-card"><h4>نبض القلب الأقصى</h4><div class="ex-row"><span class="ex-chip">نبضات القلب 160</span><span class="ex-chip">النبض الأقصى 145</span><span class="ex-chip en">Heart rate: 140 bpm</span><span class="ex-chip en">Max HR 170</span></div></div>
    </div>
    <div class="ex-section">
        <div class="ex-section-title">فحوصات متقدمة</div>
        <div class="ex-card"><h4>سكر الدم الصائم</h4><div class="ex-row"><span class="ex-chip">سكر صائم مرتفع</span><span class="ex-chip">سكر صائم طبيعي</span><span class="ex-chip en">FBS > 120</span><span class="ex-chip en">Fasting BS: 1</span></div></div>
        <div class="ex-card"><h4>ألم مع المجهود</h4><div class="ex-row"><span class="ex-chip">ألم عند المجهود</span><span class="ex-chip">ألم عند الرياضة</span><span class="ex-chip">لا يوجد ألم مع المجهود</span><span class="ex-chip en">Exercise angina: Yes/No</span></div></div>
        <div class="ex-card"><h4>تخطيط القلب</h4><div class="ex-row"><span class="ex-chip">طبيعي</span><span class="ex-chip">تضخم البطين</span><span class="ex-chip en">Normal</span><span class="ex-chip en">ST-T abnormality</span><span class="ex-chip en">LVH</span></div></div>
        <div class="ex-card"><h4>انخفاض ST</h4><div class="ex-row"><span class="ex-chip">انخفاض ST: 1.5</span><span class="ex-chip">أولدبيك 2.0</span><span class="ex-chip en">Oldpeak: 2.5</span><span class="ex-chip en">ST depression: 3.0</span></div></div>
        <div class="ex-card"><h4>ميل ST</h4><div class="ex-row"><span class="ex-chip">صاعد</span><span class="ex-chip">مسطح</span><span class="ex-chip">منحدر</span><span class="ex-chip en">Up</span><span class="ex-chip en">Flat</span><span class="ex-chip en">Down</span></div></div>
    </div>
    <div class="ex-full"><h4>أمثلة جمل كاملة</h4><code>عمري 55 سنة، ذكر، ألم في الصدر،\nضغط الدم 140/90، الكوليسترول 250،\nسكر صائم مرتفع، معدل القلب 160</code></div>
    <div class="ex-full" style="margin-top:6px; border-right-color:#2563eb;"><h4 style="color:#2563eb;">English Example</h4><code>Age 62, male, chest pain typical,\nBP 145/92, cholesterol 280,\nfasting BS high, max HR 150</code></div>
    """,

    'en': """
    <style>
        .ex-card { background: #f8fafc; border-radius: 8px; padding: 10px 12px; margin-bottom: 8px; border-left: 4px solid #6366f1; }
        .ex-card h4 { color: #4f46e5; margin: 0 0 6px 0; font-size: 13px; }
        .ex-row { display: flex; flex-wrap: wrap; gap: 5px; }
        .ex-chip { background: #dbeafe; color: #1e40af; padding: 3px 8px; border-radius: 12px; font-size: 12px; white-space: nowrap; }
        .ex-chip.ar { background: #e0e7ff; color: #3730a3; }
        .ex-section { margin-bottom: 12px; }
        .ex-section-title { color: #6366f1; font-weight: bold; font-size: 14px; margin-bottom: 8px; padding-bottom: 4px; border-bottom: 2px solid #e0e7ff; }
        .ex-full { background: linear-gradient(135deg, #dbeafe, #e0e7ff); border-radius: 8px; padding: 10px 12px; margin-top: 10px; border-left: 4px solid #2563eb; }
        .ex-full h4 { color: #2563eb; margin: 0 0 6px 0; font-size: 13px; }
        .ex-full code { display: block; background: #fff; padding: 8px; border-radius: 6px; font-size: 11px; line-height: 1.6; white-space: pre-wrap; color: #334155; }
    </style>
    <div class="ex-section">
        <div class="ex-section-title">Basic Information</div>
        <div class="ex-card"><h4>Age</h4><div class="ex-row"><span class="ex-chip">I am 55 years old</span><span class="ex-chip">Age 62</span><span class="ex-chip">70 years old</span><span class="ex-chip ar">عمري 55 سنة</span></div></div>
        <div class="ex-card"><h4>Sex</h4><div class="ex-row"><span class="ex-chip">Male</span><span class="ex-chip">Female</span><span class="ex-chip">M / F</span><span class="ex-chip ar">ذكر</span><span class="ex-chip ar">أنثى</span></div></div>
        <div class="ex-card"><h4>Chest Pain</h4><div class="ex-row"><span class="ex-chip">Typical Angina (TA)</span><span class="ex-chip">Atypical (ATA)</span><span class="ex-chip">Non-Anginal (NAP)</span><span class="ex-chip">Asymptomatic (ASY)</span></div></div>
    </div>
    <div class="ex-section">
        <div class="ex-section-title">Heart Information</div>
        <div class="ex-card"><h4>Blood Pressure</h4><div class="ex-row"><span class="ex-chip">BP 140/90</span><span class="ex-chip">Blood pressure 130/85</span><span class="ex-chip">150/100</span></div></div>
        <div class="ex-card"><h4>Cholesterol</h4><div class="ex-row"><span class="ex-chip">Cholesterol 250</span><span class="ex-chip">Chol: 280 mg/dL</span><span class="ex-chip">310</span></div></div>
        <div class="ex-card"><h4>Max Heart Rate</h4><div class="ex-row"><span class="ex-chip">Heart rate: 160 bpm</span><span class="ex-chip">Max HR 150</span><span class="ex-chip">145 bpm</span></div></div>
    </div>
    <div class="ex-section">
        <div class="ex-section-title">Advanced Tests</div>
        <div class="ex-card"><h4>Fasting Blood Sugar</h4><div class="ex-row"><span class="ex-chip">Fasting BS high</span><span class="ex-chip">FBS > 120</span><span class="ex-chip">Normal</span></div></div>
        <div class="ex-card"><h4>Exercise Angina</h4><div class="ex-row"><span class="ex-chip">Exercise angina: Yes</span><span class="ex-chip">No exercise pain</span></div></div>
        <div class="ex-card"><h4>Resting ECG</h4><div class="ex-row"><span class="ex-chip">Normal</span><span class="ex-chip">ST-T abnormality</span><span class="ex-chip">LVH</span></div></div>
        <div class="ex-card"><h4>ST Depression (Oldpeak)</h4><div class="ex-row"><span class="ex-chip">Oldpeak: 2.5</span><span class="ex-chip">ST depression: 1.5</span></div></div>
        <div class="ex-card"><h4>ST Slope</h4><div class="ex-row"><span class="ex-chip">Up</span><span class="ex-chip">Flat</span><span class="ex-chip">Down</span></div></div>
    </div>
    <div class="ex-full"><h4>Full Sentence Example</h4><code>Age 62, male, chest pain typical,\nBP 145/92, cholesterol 280,\nfasting BS high, max HR 150</code></div>
    <div class="ex-full" style="margin-top:6px; border-left-color:#7c3aed;"><h4 style="color:#7c3aed;">مثال عربي</h4><code>عمري 55 سنة، ذكر، ألم في الصدر،\nضغط الدم 140/90، الكوليسترول 250،\nسكر صائم مرتفع، معدل القلب 160</code></div>
    """,
}


def t(key, lang='ar'):
    """Get translated text by key"""
    return UI_TEXT.get(lang, UI_TEXT['ar']).get(key, key)


def get_field_name(field, lang='ar'):
    """Get translated field name"""
    names = UI_TEXT.get(lang, UI_TEXT['ar']).get('field_names', {})
    return names.get(field, field)


def get_field_names_dict(lang='ar'):
    """Get all field names as dict"""
    return UI_TEXT.get(lang, UI_TEXT['ar']).get('field_names', {})
