
import re
from config.translations import t, get_field_name

def remove_icons(text):
    """إزالة جميع الأيقونات من النص"""
    if not text:
        return text

    icons_to_remove = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '']

    for icon in icons_to_remove:
        text = text.replace(icon, '')

    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)

    text = emoji_pattern.sub('', text)
    text = ' '.join(text.split())

    return text.strip()


def render_first_question(question_info, language='ar'):
    """عرض السؤال الأول بتصميم مميز"""
    examples_html = "".join([
        f"<div style='background: rgba(255,255,255,0.2); padding: 12px 16px; margin: 8px 0; "
        f"border-radius: 10px; font-size: 1.05rem; transition: all 0.3s; "
        f"border-left: 3px solid rgba(255,255,255,0.4);'>{ex}</div>"
        for ex in question_info['examples'][:4]
    ])

    html = f"""
    <div class="question-box bounce-in">
        <div class="question-header">
            <div class="question-title">{t('first_question', language)}</div>
            <div class="question-badge priority-normal">{t('basic_question', language)}</div>
        </div>
        <div class="question-text">{question_info['question']}</div>
        <div class="question-examples">
            <div class="examples-title">{t('answer_examples', language)}</div>
            <div class="examples-list">{examples_html}</div>
        </div>
        <div class="question-note">
            <strong>{t('note', language)}</strong> {t('first_q_note', language)}
        </div>
    </div>
    """
    return html


def render_user_message(field_name, value, language='ar'):
    """عرض رسالة المستخدم"""
    display_name = get_field_name(field_name, language)
    html = f"""
    <div class="message-bubble user-message fade-in">
        <span class="message-sender">{t('you', language)}</span>
        <div class="message-content">
            <strong>{display_name}:</strong> {value}
        </div>
    </div>
    """
    return html


def render_bot_response(step, is_last=False, show_technical_details=True, language='ar'):
    """عرض رد النظام"""
    sections = []

    if show_technical_details:
        # التحليل
        internal_thought = step.get('internal_thought', {})
        if internal_thought and isinstance(internal_thought, dict):
            thought_text = internal_thought.get('thought', '')
            if thought_text:
                thought_text = remove_icons(thought_text)
                sections.append(f"""
                <div class="analysis-section analysis-thought">
                    <span class="section-title">{t('analysis', language)}</span>
                    <div class="section-content">{thought_text}</div>
                </div>
                """)

        # الاستنتاج
        inference = step.get('inference', {})
        if inference and isinstance(inference, dict):
            inference_text = inference.get('thought', '')
            if inference_text:
                inference_text = remove_icons(inference_text)
                sections.append(f"""
                <div class="analysis-section analysis-inference">
                    <span class="section-title">{t('inference', language)}</span>
                    <div class="section-content">{inference_text}</div>
                </div>
                """)

        # القرار
        decision = step.get('decision', {})
        if decision and isinstance(decision, dict):
            decision_text = decision.get('message', '')
            if decision_text:
                decision_text = remove_icons(decision_text)
                sections.append(f"""
                <div class="analysis-section analysis-decision">
                    <span class="section-title">{t('decision_label', language)}</span>
                    <div class="section-content">{decision_text}</div>
                </div>
                """)

        # التحذير
        warning = step.get('warning')
        if warning and isinstance(warning, dict) and warning.get('triggered'):
            warning_msg = warning.get('message', '')
            if warning_msg:
                warning_msg = remove_icons(warning_msg)
                sections.append(f"""
                <div class="analysis-section analysis-warning">
                    <span class="section-title">{t('important_warning', language)}</span>
                    <div class="section-content">{warning_msg}</div>
                </div>
                """)

    # السؤال التالي (فقط للرسالة الأخيرة)
    if is_last:
        next_q = step.get('next_question', {})
        if next_q and isinstance(next_q, dict):
            next_question = next_q.get('question', '')
            priority = next_q.get('priority', 0)
            reasoning_ar = next_q.get('reasoning_ar', '')
            reasoning_en = next_q.get('reasoning_en', '')
            examples_ar = next_q.get('examples_ar', [])

            reasoning_text = reasoning_en if language == 'en' and reasoning_en else reasoning_ar

            if next_question:
                if priority >= 0.35:
                    priority_class = "priority-critical"
                    priority_label = t('priority_critical', language)
                    priority_icon = ""
                elif priority >= 0.25:
                    priority_class = "priority-high"
                    priority_label = t('priority_high', language)
                    priority_icon = ""
                elif priority >= 0.15:
                    priority_class = "priority-medium"
                    priority_label = t('priority_medium', language)
                    priority_icon = ""
                else:
                    priority_class = "priority-normal"
                    priority_label = t('priority_normal', language)
                    priority_icon = ""

                reasoning_html = ""
                if reasoning_text:
                    reasoning_html = f"""
                    <div style='margin-top: 15px; padding: 15px;
                                background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
                                border-radius: 10px; border-left: 4px solid #ff9800;'>
                        <div style='display: flex; align-items: center; gap: 10px;'>
                            <span style='font-size: 1.3rem;'></span>
                            <div>
                                <div style='font-weight: 700; color: #e65100; margin-bottom: 5px;'>
                                    {t('why_important', language)}
                                </div>
                                <div style='color: #4a4a4a; font-size: 1rem; line-height: 1.5;'>
                                    {reasoning_text}
                                </div>
                            </div>
                        </div>
                    </div>
                    """

                examples_html = ""
                if examples_ar:
                    examples_items = "".join([
                        f"<div style='background: rgba(156,39,176,0.06); padding: 10px 14px; "
                        f"margin: 6px 0; border-radius: 8px; font-size: 1rem; "
                        f"border-left: 2px solid #9c27b0;'>{ex}</div>"
                        for ex in examples_ar[:3]
                    ])
                    examples_html = f"""
                    <div style='margin-top: 20px; padding: 16px; background: rgba(156,39,176,0.04);
                                border-radius: 12px; border: 1px solid rgba(156,39,176,0.1);'>
                        <div style='font-weight: 700; color: #7b1fa2; margin-bottom: 12px;
                                    font-size: 1.05rem;'>{t('answer_examples', language)}</div>
                        <div>{examples_items}</div>
                    </div>
                    """

                sections.append(f"""
                <div style='margin-top: 25px; padding: 25px;
                            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                            border-radius: 14px; border: 2px solid #9c27b0;
                            box-shadow: 0 4px 6px rgba(156,39,176,0.1);'>
                    <div style='display: flex; justify-content: space-between; align-items: center;
                                margin-bottom: 18px;'>
                        <span style='font-size: 1.2rem; font-weight: 700; color: #2d3748;'>
                            {priority_icon} {t('next_important_q', language)}
                        </span>
                        <span class="priority-badge {priority_class}">{priority_label}</span>
                    </div>
                    <div style='font-size: 1.5rem; font-weight: 700; color: #7b1fa2;
                                line-height: 1.6; margin-bottom: 15px;'>
                        {next_question}
                    </div>
                    {reasoning_html}
                    {examples_html}
                </div>
                """)

    if sections:
        sections_html = "".join(sections)
        html = f"""
        <div class="message-bubble bot-message bot-analysis fade-in">
            <span class="message-sender">{t('smart_system', language)}</span>
            <div class="message-content">
                {sections_html}
            </div>
        </div>
        """
        return html

    return ""


def get_conversation_html(conversation_steps, chatbot, language='ar'):
    """إنشاء HTML كامل للمحادثة"""
    html_parts = []

    for i, step in enumerate(conversation_steps):
        try:
            if not isinstance(step, dict):
                continue

            field_name = step.get('field_processed', 'Unknown')

            if field_name == 'Welcome':
                continue

            user_value = chatbot.facts.get(field_name) if chatbot else 'N/A'
            html_parts.append(render_user_message(field_name, user_value, language))

            is_last = (i == len(conversation_steps) - 1)
            bot_html = render_bot_response(step, is_last, show_technical_details=True, language=language)
            if bot_html:
                html_parts.append(bot_html)

        except Exception as e:
            print(f"Error rendering step {i}: {str(e)}")
            continue

    return "".join(html_parts)


# ═══════════════════════════════════════════════════════════════
# Smart Conversation Display (v8.0.0)
# ═══════════════════════════════════════════════════════════════

def render_doctor_message(text, language='ar'):
    """عرض رسالة الطبيب كفقاعة محادثة"""
    doctor_label = t('doctor_label', language)
    direction = 'rtl' if language == 'ar' else 'ltr'
    align = 'right' if language == 'ar' else 'left'
    border_side = 'border-right' if language == 'ar' else 'border-left'

    return f"""
    <div style="direction: {direction}; text-align: {align}; margin: 12px 0;">
        <div style="display: inline-block; max-width: 85%; padding: 16px 20px;
                    background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
                    border-radius: 16px; {border_side}: 4px solid #43a047;
                    box-shadow: 0 2px 8px rgba(67,160,71,0.15);">
            <div style="font-weight: 700; color: #2e7d32; font-size: 0.85rem;
                        margin-bottom: 8px;">
                {doctor_label}
            </div>
            <div style="color: #1b5e20; font-size: 1.05rem; line-height: 1.7;">
                {text}
            </div>
        </div>
    </div>
    """


def render_patient_message(text, language='ar'):
    """عرض رسالة المريض كفقاعة محادثة"""
    patient_label = t('patient_label', language)
    direction = 'rtl' if language == 'ar' else 'ltr'
    align = 'left' if language == 'ar' else 'right'
    border_side = 'border-left' if language == 'ar' else 'border-right'

    return f"""
    <div style="direction: {direction}; text-align: {align}; margin: 12px 0;">
        <div style="display: inline-block; max-width: 85%; padding: 16px 20px;
                    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                    border-radius: 16px; {border_side}: 4px solid #1976d2;
                    box-shadow: 0 2px 8px rgba(25,118,210,0.15);">
            <div style="font-weight: 700; color: #1565c0; font-size: 0.85rem;
                        margin-bottom: 8px;">
                {patient_label}
            </div>
            <div style="color: #0d47a1; font-size: 1.05rem; line-height: 1.7;">
                {text}
            </div>
        </div>
    </div>
    """


def render_extracted_fields_badge(fields, language='ar'):
    """عرض شارة المعلومات المستخرجة"""
    if not fields:
        return ""

    field_label = t('extracted_info_label', language)
    chips = ""
    for f in fields:
        name = f.get('field_ar', f.get('field', ''))
        val = f.get('value', '')
        source = f.get('source', '')
        source_color = '#43a047' if source == 'groq' else '#1976d2'
        chips += f"""<span style="display: inline-block; background: #f3e5f5; color: #6a1b9a;
                     padding: 4px 10px; border-radius: 12px; font-size: 0.85rem;
                     margin: 3px; border: 1px solid #ce93d8;">
                     {name}: <strong>{val}</strong>
                     </span>"""

    return f"""
    <div style="margin: 8px 0; padding: 10px 14px; background: #faf5ff;
                border-radius: 10px; border: 1px solid #e1bee7;">
        <div style="font-weight: 600; color: #7b1fa2; font-size: 0.85rem; margin-bottom: 6px;">
            {field_label}
        </div>
        <div>{chips}</div>
    </div>
    """


def get_smart_conversation_html(chat_history, language='ar'):
    """إنشاء HTML للمحادثة الذكية"""
    html_parts = []

    for msg in chat_history:
        role = msg.get('role', '')
        content = msg.get('content', '')
        extracted = msg.get('extracted_fields', [])

        if role == 'doctor':
            html_parts.append(render_doctor_message(content, language))
        elif role == 'patient':
            html_parts.append(render_patient_message(content, language))
            if extracted:
                html_parts.append(render_extracted_fields_badge(extracted, language))

    return "".join(html_parts)
