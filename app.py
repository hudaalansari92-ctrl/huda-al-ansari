

import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path
import pandas as pd
from typing import Dict, List, Optional
import plotly.graph_objects as go
import plotly.express as px

# استيراد النظام الأساسي
from core.integrated_chatbot import IntegratedSelfReasoningChatbot
from config.question_examples import get_question_info, get_first_question, format_examples_html, QUESTION_EXAMPLES
from ui.enhanced_styles import ENHANCED_CSS
from ui.conversation_display import (
    render_first_question, get_conversation_html,
    render_doctor_message, render_patient_message,
    render_extracted_fields_badge, get_smart_conversation_html
)
from config.translations import t, get_field_name, get_field_names_dict, EXAMPLES_HTML
from ui.decision_tree_viz import (
    create_decision_tree_diagram,
    create_simple_decision_tree_flow,
    create_decision_rules_table
)
from ui.comparison_page import render_comparison_page
from ui.architecture_page import render_architecture_page
from ui.live_demo_page import render_live_demo_page
from auth import require_login, render_logout_button, is_admin, is_patient
from ui.patient_report import render_patient_report, render_instant_alert
from core.history_tracker import FIELD_THRESHOLDS as TRACKED_FIELDS

def get_lang():
    """الحصول على اللغة المختارة"""
    return st.session_state.get('language_select', 'ar')

#
#  نظام إدارة البيانات | Data Management System
#

class SessionStorage:
    """نظام تخزين متقدم للجلسات"""
    
    def __init__(self, storage_dir: str = "sessions"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
    def save_session(self, session_id: str, data: Dict):
        """حفظ الجلسة"""
        session_file = self.storage_dir / f"{session_id}.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    def load_session(self, session_id: str) -> Optional[Dict]:
        """تحميل الجلسة"""
        session_file = self.storage_dir / f"{session_id}.json"
        if session_file.exists():
            with open(session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def list_sessions(self, username: Optional[str] = None) -> List[Dict]:
        """قائمة الجلسات — مرشَّحة حسب المريض إن وُجد username"""
        sessions = []
        wanted = (username or '').strip().lower() or None
        for file in self.storage_dir.glob("*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                owner = (data.get('username') or '').strip().lower()
                # تطبيق الفلترة إذا username مُحدَّد
                if wanted is not None and owner != wanted:
                    continue
                sessions.append({
                    'session_id': file.stem,
                    'created_at': data.get('created_at'),
                    'facts_count': len(data.get('facts', {})),
                    'status': data.get('status', 'ongoing'),
                    'username': data.get('username', ''),
                    'role': data.get('role', ''),
                })
            except Exception:
                pass
        return sorted(sessions, key=lambda x: x['created_at'] or '', reverse=True)
    
    def delete_session(self, session_id: str):
        """حذف جلسة"""
        session_file = self.storage_dir / f"{session_id}.json"
        if session_file.exists():
            session_file.unlink()

# 
#  تهيئة واجهة Streamlit | Streamlit UI Configuration
# 

def init_streamlit_config():
    """تهيئة إعدادات Streamlit"""
    st.set_page_config(
        page_title="Healthcare Chatbot System Based on Intelligent Techniques",
        page_icon="",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply Enhanced CSS
    st.markdown(ENHANCED_CSS, unsafe_allow_html=True)

def display_header():
    """عرض الترويسة"""
    lang = get_lang()
    st.html(f"""
        <div style='text-align: center; padding: 30px 0; margin-bottom: 30px;
                    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
                    border-radius: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);'>
            <h1 style='margin: 0; padding: 0; font-size: 2.5rem; font-weight: 800;
                       background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                       -webkit-background-clip: text;
                       -webkit-text-fill-color: transparent;
                       animation: fadeInDown 1s ease-out;'>
                {t('header_title', lang)}
            </h1>
            <p style='margin: 15px 0 0 0; font-size: 1.1rem; color: #64748b; font-weight: 500;
                      animation: fadeIn 1.2s ease-out;'>
                {t('page_subtitle', lang)}
            </p>
            <div style='margin-top: 20px; height: 3px; width: 100px;
                        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                        margin-left: auto; margin-right: auto; border-radius: 10px;'></div>
        </div>
    """)

def display_risk_gauge(risk_level: str):
    """عرض مقياس الخطر"""
    risk_colors = {
        'LOW': '#10b981',
        'MODERATE': '#f59e0b',
        'HIGH': '#ef4444',
        'CRITICAL': '#dc2626',
        'UNKNOWN': '#94a3b8',
    }

    risk_values = {
        'LOW': 25,
        'MODERATE': 50,
        'HIGH': 75,
        'CRITICAL': 100,
        'UNKNOWN': 0,
    }

    lang = get_lang()
    risk_labels = {
        'LOW': 'LOW',
        'MODERATE': 'MODERATE',
        'HIGH': 'HIGH',
        'CRITICAL': 'CRITICAL',
        'UNKNOWN': t('not_assessed', lang),
    }

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_values.get(risk_level, 0),
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"{t('risk_gauge_title', lang)}<br>{risk_labels.get(risk_level, risk_level)}", 'font': {'size': 24}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': risk_colors.get(risk_level, 'gray')},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 25], 'color': '#d1fae5'},
                {'range': [25, 50], 'color': '#fef3c7'},
                {'range': [50, 75], 'color': '#fed7aa'},
                {'range': [75, 100], 'color': '#fecaca'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': risk_values.get(risk_level, 0)
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig

def display_conversation_history(conversation_steps: List[Dict]):
    """عرض تاريخ المحادثة بشكل سؤال وجواب"""
    lang = getattr(st.session_state.get('chatbot'), 'language', 'ar') or 'ar'

    if not conversation_steps:
        # عرض السؤال الأول
        first_q = get_first_question(lang)
        if first_q:
            html = render_first_question(first_q, lang)
            if html:
                st.html(html)
        return

    # هل يوجد فقط welcome step بدون إجابات؟
    only_welcome = (
        len(conversation_steps) == 1
        and conversation_steps[0].get('field_processed') == 'Welcome'
    )

    if only_welcome:
        first_q = get_first_question(lang)
        if first_q:
            html = render_first_question(first_q, lang)
            if html:
                st.html(html)
        return

    # عنوان المحادثة
    conv_title = t('conversation', lang)
    st.html(f'<div class="card-header">{conv_title}</div>')

    # عرض المحادثة (مع جميع التفاصيل)
    conversation_html = get_conversation_html(conversation_steps, st.session_state.chatbot, lang)
    if conversation_html:  # فحص لتجنب خطأ st.html مع نص فارغ
        st.html(conversation_html)  # استخدام st.html - أفضل وأسرع!
            
def display_facts_table(facts: Dict):
    """عرض جدول الحقائق"""
    lang = get_lang()
    if not facts or not isinstance(facts, dict):
        st.info(t('no_facts', lang))
        return

    try:
        df_data = []
        field_names = get_field_names_dict(lang)
        col_field = t('col_field', lang)
        col_value = t('col_value', lang)
        col_time = t('col_time', lang)

        for key, value in facts.items():
            df_data.append({
                col_field: field_names.get(key, key),
                col_value: str(value) if value is not None else 'N/A',
                col_time: datetime.now().strftime('%H:%M:%S')
            })

        if df_data:
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info(t('no_facts', lang))
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.info(t('no_facts', lang))

def display_step_timeline(steps: List[Dict]):
    """عرض الخط الزمني للخطوات"""
    if not steps:
        return
    
    lang = get_lang()
    timeline_title = 'Dialog Timeline' if lang == 'en' else 'الخط الزمني للحوار'
    st.markdown(f"###  {timeline_title}")

    for i, step in enumerate(steps, 1):
        try:
            field_name = step.get('field_processed', 'Unknown') if isinstance(step, dict) else 'Unknown'
            step_label = f"Step {i}: {field_name}" if lang == 'en' else f"الخطوة {i}: {field_name}"
            with st.expander(step_label, expanded=(i == len(steps))):
                col1, col2 = st.columns([1, 1])

                with col1:
                    thought_label = 'Internal Thought:' if lang == 'en' else 'الفكرة الداخلية:'
                    st.markdown(f"** {thought_label}**")
                    internal_thought = step.get('internal_thought', {}) if isinstance(step, dict) else {}
                    thought_text = internal_thought.get('thought', 'N/A') if isinstance(internal_thought, dict) else 'N/A'
                    if thought_text:
                        st.html(f"<div class='thought-box'>{thought_text}</div>")

                    inference = step.get('inference') if isinstance(step, dict) else None
                    if inference and isinstance(inference, dict):
                        inf_label = 'Inference:' if lang == 'en' else 'الاستنتاج:'
                        st.markdown(f"** {inf_label}**")
                        st.info(inference.get('thought', 'N/A'))

                with col2:
                    status_label = 'Status:' if lang == 'en' else 'الحالة:'
                    st.markdown(f"** {status_label}**")
                    status = step.get('current_status', {}) if isinstance(step, dict) else {}
                    status = status if isinstance(status, dict) else {}

                    st.metric(t('risk_level', lang), status.get('risk_level', 'N/A'))
                    confidence = status.get('confidence_score', 0)
                    st.metric(t('confidence', lang), f"{confidence:.0%}" if isinstance(confidence, (int, float)) else "N/A")
                    facts_collected = status.get('facts_collected', 0)
                    st.metric(t('facts_collected', lang), f"{facts_collected}/11")

                    warning = step.get('warning') if isinstance(step, dict) else None
                    if warning and isinstance(warning, dict) and warning.get('triggered'):
                        st.warning(f" {warning.get('message', '')}")
        except Exception as e:
            err_label = f"Error displaying step {i}" if lang == 'en' else f"خطأ في عرض الخطوة {i}"
            st.error(f"{err_label}: {str(e)}")
            continue

def display_progress_bar(facts_count: int, total_facts: int = 11):
    """عرض شريط التقدم"""
    lang = get_lang()
    progress = facts_count / total_facts
    st.progress(progress)
    pct = f"{progress*100:.1f}"
    st.caption(t('progress_text', lang).format(done=facts_count, total=total_facts, pct=pct))

# 
#  الوظائف الرئيسية | Main Functions
# 

def initialize_session_state():
    """تهيئة حالة الجلسة"""
    if 'storage' not in st.session_state:
        st.session_state.storage = SessionStorage()
    
    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = None
    
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = None
    
    if 'conversation_steps' not in st.session_state:
        st.session_state.conversation_steps = []
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    if 'session_data' not in st.session_state:
        st.session_state.session_data = {
            'created_at': None,
            'facts': {},
            'steps': [],
            'conversation_history': [],
            'status': 'ongoing'
        }

    # Smart Conversation (v8.0.0)
    if 'smart_mode' not in st.session_state:
        st.session_state.smart_mode = False
    if 'smart_chat_history' not in st.session_state:
        st.session_state.smart_chat_history = []
    if 'show_comparison' not in st.session_state:
        st.session_state.show_comparison = False
    if 'show_architecture' not in st.session_state:
        st.session_state.show_architecture = False
    if 'show_live_demo' not in st.session_state:
        st.session_state.show_live_demo = False
    if 'input_key_counter' not in st.session_state:
        st.session_state.input_key_counter = 0
    # Longitudinal tracking
    if 'alerted_fields' not in st.session_state:
        st.session_state.alerted_fields = set()
    if 'pending_instant_alerts' not in st.session_state:
        st.session_state.pending_instant_alerts = []
    if 'show_final_report' not in st.session_state:
        st.session_state.show_final_report = False
    if 'tts_played_count' not in st.session_state:
        st.session_state.tts_played_count = 0

def detect_and_queue_instant_alerts():
    """
    After facts are saved, detect any tracked field whose value is new since
    the last check and queue an instant alert comparison against this
    patient's history. Alerts render on the next rerun above the conversation.
    """
    if 'user' not in st.session_state:
        return
    username = st.session_state.user.get('username', '')
    if not username:
        return
    chatbot = st.session_state.get('chatbot')
    if not chatbot:
        return
    current_session_id = st.session_state.get('current_session_id', '')
    if 'alerted_fields' not in st.session_state:
        st.session_state.alerted_fields = set()
    if 'pending_instant_alerts' not in st.session_state:
        st.session_state.pending_instant_alerts = []

    from core.history_tracker import HistoryTracker
    tracker = HistoryTracker()
    lang = get_lang()

    for field, value in chatbot.facts.items():
        if field not in TRACKED_FIELDS:
            continue
        if field in st.session_state.alerted_fields:
            continue
        try:
            comp = tracker.compare_with_previous(
                username, field, value,
                exclude_session_id=current_session_id
            )
        except Exception:
            continue
        st.session_state.alerted_fields.add(field)
        if not comp:
            continue
        alert = tracker.generate_alert_text(comp, lang)
        if not alert or alert.get('level') == 'stable':
            continue
        alert['comparison'] = comp
        st.session_state.pending_instant_alerts.append(alert)


def start_new_session(language: str = 'ar'):
    """بدء جلسة جديدة"""
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    st.session_state.current_session_id = session_id
    groq_key = st.session_state.get('groq_key_saved', None)
    st.session_state.chatbot = IntegratedSelfReasoningChatbot(language=language, groq_api_key=groq_key)
    st.session_state.conversation_steps = []
    st.session_state.conversation_history = []
    # Link session to the logged-in user (patient or admin)
    _current_user = st.session_state.get('user', {}) or {}
    _owner = _current_user.get('username', '')
    st.session_state.session_data = {
        'created_at': datetime.now().isoformat(),
        'language': language,
        'username': _owner,
        'role': _current_user.get('role', ''),
        'facts': {},
        'steps': [],
        'conversation_history': [],
        'status': 'ongoing'
    }
    # Reset tracked-field alert memory for the new session
    st.session_state.alerted_fields = set()
    
    # إضافة سؤال ترحيبي أولي
    welcome_step = {
        'step': 0,
        'field_processed': 'Welcome',
        'internal_thought': {
            'thought': 'مرحباً! سأبدأ بجمع المعلومات الطبية الأساسية لتقييم حالتك الصحية.' if language == 'ar' else 'Welcome! I will start collecting basic medical information to assess your health condition.',
            'category': 'greeting',
            'confidence': 1.0
        },
        'inference': {
            'thought': 'لا توجد حقائق حتى الآن. سأبدأ بالسؤال الأهم حسب الأولوية.' if language == 'ar' else 'No facts yet. I will start with the highest priority question.',
            'confidence': 1.0
        },
        'current_status': {
            'risk_level': 'UNKNOWN',
            'confidence_score': 0.0,
            'facts_collected': 0,
            'total_facts': 11
        },
        'decision': {
            'message': 'سأبدأ بالسؤال عن الأعراض الحادة أولاً' if language == 'ar' else 'I will start by asking about acute symptoms first'
        },
        'next_question': {
            'field': 'ChestPain',
            'question': 'هل تعاني من ألم في الصدر؟' if language == 'ar' else 'Do you have chest pain?',
            'question_en': 'Do you have chest pain?',
            'priority': 0.40
        }
    }
    
    st.session_state.conversation_steps.append(welcome_step)
    st.session_state.session_data['steps'].append(welcome_step)

    # Smart mode setup (v8.0.0)
    is_smart = st.session_state.chatbot.conversation_mode == "smart"
    st.session_state.smart_mode = is_smart
    st.session_state.smart_chat_history = []

    if is_smart:
        # Generate doctor greeting
        greeting = st.session_state.chatbot.get_smart_greeting()
        if greeting:
            st.session_state.smart_chat_history.append({
                'role': 'doctor',
                'content': greeting
            })
        else:
            # Fallback greeting
            st.session_state.smart_chat_history.append({
                'role': 'doctor',
                'content': t('smart_greeting_default', language)
            })

    st.success(t('session_started', get_lang()).format(sid=session_id))
    return session_id

def process_user_answer(field: str, answer: str):
    """معالجة إجابة المستخدم"""
    if not st.session_state.chatbot:
        st.error(t('start_session_first', get_lang()))
        return None
    
    # معالجة الإجابة
    response = st.session_state.chatbot.process_answer(field, answer)
    
    # تخزين الخطوة
    st.session_state.conversation_steps.append(response)
    st.session_state.session_data['steps'].append(response)
    st.session_state.session_data['facts'] = st.session_state.chatbot.facts.copy()

    # حفظ الجلسة
    st.session_state.storage.save_session(
        st.session_state.current_session_id,
        st.session_state.session_data
    )
    detect_and_queue_instant_alerts()

    return response

def process_free_input(user_input: str, available_fields: dict) -> dict:
    """
    معالجة الإدخال الحر وتحليله لاستخراج المعلومات باستخدام BioBERT NER
    
    Args:
        user_input: النص الحر من المستخدم
        available_fields: الحقول المتاحة للمعالجة
    
    Returns:
        dict: النتائج المستخرجة والمعالجة
    """
    import re
    
    results = {
        'processed_count': 0,
        'extracted': [],
        'unprocessed': ''
    }
    
    # استخدام BioBERT NER لاستخراج المعلومات 
    if hasattr(st.session_state, 'chatbot') and st.session_state.chatbot:
        try:
            # استخدام BioBERT NER من chatbot
            extraction_result = st.session_state.chatbot.extract_fields_from_text(user_input)
            
            # معالجة النتائج المستخرجة
            for item in extraction_result.get('extracted', []):
                field_name = item['field']
                field_value = item['value']
                
                # التحقق من أن الحقل متاح في available_fields
                if field_name in available_fields:
                    # معالجة الإجابة (chatbot سيقوم بتطبيع القيمة)
                    response = process_user_answer(field_name, field_value)
                    
                    if response:
                        results['processed_count'] += 1
                        results['extracted'].append({
                            'field': field_name,
                            'field_ar': available_fields.get(field_name, field_name),
                            'value': field_value,
                            'confidence': item.get('confidence', 0.85)
                        })
            
            # إضافة رسالة توضيحية إذا تم الاستخراج بنجاح
            if results['processed_count'] > 0:
                import logging
                logging.info(f"BioBERT extracted and processed {results['processed_count']} fields successfully")
            
            return results
            
        except Exception as e:
            # في حالة فشل BioBERT، استخدم الطريقة القديمة كـ fallback
            import logging
            logging.warning(f"BioBERT NER failed, using fallback: {e}")
            import traceback
            traceback.print_exc()
    
    # Fallback: الطريقة القديمة (regex patterns)
    text_lower = user_input.lower()
    
    # قواميس الكلمات المفتاحية لكل حقل
    field_patterns = {
        'Age': {
            'keywords': ['عمر', 'age', 'سنة', 'سنوات', 'year', 'years old'],
            'pattern': r'(?:عمر[يه]?|age|أنا|أبلغ|i am|i\'m)?\s*(\d{1,3})\s*(?:سنة|سنوات|year|years|old)?',
            'extract_func': lambda m: m.group(1)
        },
        'Sex': {
            'keywords': ['جنس', 'ذكر', 'أنثى', 'رجل', 'امرأة', 'sex', 'gender', 'male', 'female', 'man', 'woman'],
            'pattern': r'(?:جنس|gender|sex)?\s*(ذكر|أنثى|رجل|امرأة|male|female|m|f)',
            'extract_func': lambda m: 'Male' if any(x in m.group(1).lower() for x in ['ذكر', 'رجل', 'male', 'm']) else 'Female'
        },
        'ChestPain': {
            'keywords': ['ألم', 'صدر', 'chest', 'pain', 'وجع'],
            'pattern': r'(?:ألم|وجع|pain).*?(?:صدر|chest)|(?:صدر|chest).*?(?:ألم|وجع|pain)',
            'extract_func': lambda m: 'Yes'
        },
        'BloodPressure': {
            'keywords': ['ضغط', 'دم', 'blood', 'pressure', 'bp'],
            'pattern': r'(?:ضغط\s*(?:الدم)?|blood\s*pressure|bp)?\s*(\d{2,3})\s*[/\\]\s*(\d{2,3})',
            'extract_func': lambda m: f"{m.group(1)}/{m.group(2)}"
        },
        'Cholesterol': {
            'keywords': ['كوليسترول', 'cholesterol', 'chol'],
            'pattern': r'(?:كوليسترول|cholesterol|chol)?\s*(\d{2,3})',
            'extract_func': lambda m: m.group(1)
        },
        'FastingBS': {
            'keywords': ['سكر', 'صائم', 'fasting', 'sugar', 'glucose'],
            'pattern': r'(?:سكر|sugar|glucose).*?(?:صائم|fasting)|(?:fasting|صائم).*?(?:سكر|sugar)',
            'extract_func': lambda m: 'Yes'
        },
        'MaxHR': {
            'keywords': ['نبض', 'قلب', 'heart', 'rate', 'pulse', 'bpm'],
            'pattern': r'(?:نبض|معدل|heart\s*rate|pulse)?\s*(\d{2,3})\s*(?:bpm|نبضة)?',
            'extract_func': lambda m: m.group(1)
        },
        'ExerciseAngina': {
            'keywords': ['مجهود', 'تمرين', 'exercise', 'angina', 'رياضة'],
            'pattern': r'(?:ألم|وجع).*?(?:مجهود|تمرين|exercise|رياضة)|(?:مجهود|exercise).*?(?:ألم|angina)',
            'extract_func': lambda m: 'Yes'
        }
    }
    
    # محاولة استخراج المعلومات لكل حقل متاح
    for field_name in available_fields.keys():
        if field_name not in field_patterns:
            continue
        
        pattern_info = field_patterns[field_name]
        
        # البحث عن الكلمات المفتاحية أولاً
        found_keyword = False
        for keyword in pattern_info['keywords']:
            if keyword in text_lower:
                found_keyword = True
                break
        
        if not found_keyword:
            continue
        
        # محاولة استخراج القيمة باستخدام النمط
        try:
            match = re.search(pattern_info['pattern'], text_lower, re.IGNORECASE | re.UNICODE)
            if match:
                value = pattern_info['extract_func'](match)
                
                # معالجة الإجابة
                response = process_user_answer(field_name, value)
                
                if response:
                    results['processed_count'] += 1
                    results['extracted'].append({
                        'field': field_name,
                        'field_ar': available_fields[field_name],
                        'value': value
                    })
        except Exception as e:
            # تجاهل الأخطاء والمتابعة
            continue
    
    # إذا لم نجد أي شيء، حاول استخراج معلومات عامة
    if results['processed_count'] == 0:
        # البحث عن أرقام عامة
        numbers = re.findall(r'\d+', user_input)
        if numbers:
            # إذا كان هناك رقم واحد فقط ويبدو مثل العمر
            if len(numbers) == 1 and 1 <= int(numbers[0]) <= 120 and 'Age' in available_fields:
                response = process_user_answer('Age', numbers[0])
                if response:
                    results['processed_count'] += 1
                    results['extracted'].append({
                        'field': 'Age',
                        'field_ar': 'العمر',
                        'value': numbers[0]
                    })
    
    return results

def process_user_answer(field: str, answer: str):
    """معالجة إجابة المستخدم"""
    if not st.session_state.chatbot:
        st.error(t('start_session_first', get_lang()))
        return None
    
    # معالجة الإجابة
    response = st.session_state.chatbot.process_answer(field, answer)
    
    # تخزين الخطوة
    st.session_state.conversation_steps.append(response)
    st.session_state.session_data['steps'].append(response)
    st.session_state.session_data['facts'] = st.session_state.chatbot.facts.copy()

    # حفظ الجلسة
    st.session_state.storage.save_session(
        st.session_state.current_session_id,
        st.session_state.session_data
    )
    detect_and_queue_instant_alerts()

    return response

def render_sidebar():
    """عرض الشريط الجانبي"""
    with st.sidebar:
        # اللغة أولاً (تؤثر على كل شيء)
        _current_lang = st.session_state.get('language_select', 'ar')
        _lang_label = 'اللغة' if _current_lang == 'ar' else 'Language'
        language = st.selectbox(
            _lang_label,
            options=['ar', 'en'],
            format_func=lambda x: 'العربية' if x == 'ar' else 'English',
            key='language_select'
        )
        lang = get_lang()

        # User info + logout
        render_logout_button()
        st.markdown("---")

        st.markdown(f"## {t('control_panel', lang)}")

        # ===== Admin-only: Groq API Key =====
        if is_admin():
            st.markdown(f"### {t('groq_settings', lang)}")
            try:
                _default_groq_key = st.secrets["GROQ_API_KEY"]
            except Exception:
                _default_groq_key = ""
            groq_key = st.text_input(
                t('groq_api_key', lang),
                value=_default_groq_key,
                type="password",
                key="groq_api_key",
                help=t('groq_help', lang)
            )
            if groq_key:
                if st.session_state.chatbot:
                    st.session_state.chatbot.set_groq_api_key(groq_key)
                    if st.session_state.chatbot.groq_client.is_available:
                        st.success(t('groq_connected', lang))
                        st.session_state.smart_mode = True
                    else:
                        st.error(t('groq_error', lang))
                        st.session_state.smart_mode = False
                st.session_state['groq_key_saved'] = groq_key
            else:
                st.caption(t('groq_optional', lang))
            st.markdown("---")
        else:
            # Patient: silently auto-load Groq key from secrets if available
            try:
                _auto_key = st.secrets["GROQ_API_KEY"]
            except Exception:
                _auto_key = ""
            if _auto_key and st.session_state.chatbot:
                st.session_state.chatbot.set_groq_api_key(_auto_key)
                if st.session_state.chatbot.groq_client.is_available:
                    st.session_state.smart_mode = True

        # زر جلسة جديدة (available to both roles)
        if st.button(t('new_session', lang), use_container_width=True):
            st.session_state.show_comparison = False
            st.session_state.show_architecture = False
            st.session_state.show_live_demo = False
            start_new_session(language=lang)
            st.rerun()

        # ===== Admin-only: navigation buttons =====
        if is_admin():
            # زر صفحة المقارنة
            comparison_label = 'مقارنة الأنظمة' if lang == 'ar' else 'System Comparison'
            if st.button(f"{comparison_label}", use_container_width=True):
                st.session_state.show_comparison = not st.session_state.get('show_comparison', False)
                st.session_state.show_architecture = False
                st.session_state.show_live_demo = False
                st.rerun()

            # زر بنية النظام
            arch_label = 'بنية النظام' if lang == 'ar' else 'System Architecture'
            if st.button(f"{arch_label}", use_container_width=True):
                st.session_state.show_architecture = not st.session_state.get('show_architecture', False)
                st.session_state.show_comparison = False
                st.session_state.show_live_demo = False
                st.rerun()

            # زر التجربة الحية
            demo_label = 'تجربة حية' if lang == 'ar' else 'Live Demo'
            if st.button(f"{demo_label}", use_container_width=True):
                st.session_state.show_live_demo = not st.session_state.get('show_live_demo', False)
                st.session_state.show_comparison = False
                st.session_state.show_architecture = False
                st.rerun()

            # ═══ User management (admin only, prominent location) ═══
            st.markdown("---")
            _users_hdr = ('إدارة المستخدمين' if lang == 'ar' else 'User Management')
            with st.expander(f"👥 {_users_hdr}", expanded=True):
                from auth import AuthManager
                _auth = st.session_state.get('auth_manager') or AuthManager()
                st.session_state.auth_manager = _auth

                # ── Add new user form ──
                _new_hdr = ('إضافة مستخدم جديد' if lang == 'ar' else 'Add new user')
                st.markdown(f"**{_new_hdr}**")
                with st.form('add_user_form', clear_on_submit=True):
                    _nu = st.text_input(
                        ('اسم المستخدم' if lang == 'ar' else 'Username'),
                        key='nu_username')
                    _np = st.text_input(
                        ('كلمة المرور' if lang == 'ar' else 'Password'),
                        type='password', key='nu_password')
                    _nfn = st.text_input(
                        ('الاسم الكامل (اختياري)' if lang == 'ar' else 'Full name (optional)'),
                        key='nu_fullname')
                    _nr = st.selectbox(
                        ('الدور' if lang == 'ar' else 'Role'),
                        options=['patient', 'admin'],
                        format_func=lambda r: (
                            'مريض' if (r == 'patient' and lang == 'ar')
                            else 'مسؤول' if (r == 'admin' and lang == 'ar')
                            else r.capitalize()
                        ),
                        key='nu_role')
                    _submit = st.form_submit_button(
                        ('➕ إنشاء المستخدم' if lang == 'ar' else '➕ Create user'),
                        use_container_width=True,
                        type='primary',
                    )
                if _submit:
                    if not _nu.strip() or not _np.strip():
                        st.warning(('يلزم اسم المستخدم وكلمة المرور'
                                    if lang == 'ar'
                                    else 'Username and password are required'))
                    else:
                        _added = _auth.add_user(
                            username=_nu.strip(),
                            password=_np,
                            role=_nr,
                            full_name=_nfn.strip(),
                        )
                        if _added:
                            st.success(
                                (f"تم إنشاء المستخدم: {_nu}" if lang == 'ar'
                                 else f"User created: {_nu}"))
                            st.rerun()
                        else:
                            st.error(('اسم المستخدم موجود بالفعل'
                                      if lang == 'ar'
                                      else 'Username already exists'))

                st.markdown('---')

                # ── List existing users ──
                _list_hdr = ('المستخدمون الحاليون' if lang == 'ar' else 'Existing users')
                _users = _auth.list_users()
                st.markdown(f"**{_list_hdr}** — {len(_users)}")
                _self = (st.session_state.get('user', {}) or {}).get('username', '')

                for _u in _users:
                    _is_admin_default = (_u['username'] == 'admin')
                    _is_me = (_u['username'] == _self)
                    _role_icon = '🔑' if _u['role'] == 'admin' else '👤'
                    _label_extra = ''
                    if _is_me:
                        _label_extra = (' (أنت)' if lang == 'ar' else ' (you)')
                    elif _is_admin_default:
                        _label_extra = (' (محمي)' if lang == 'ar' else ' (protected)')

                    with st.expander(f"{_role_icon} {_u['username']}{_label_extra}"):
                        # ── Info card ──
                        _role_text = (('مسؤول' if _u['role'] == 'admin' else 'مريض')
                                      if lang == 'ar' else _u['role'].capitalize())
                        _role_color = ('#059669' if _u['role'] == 'admin'
                                       else '#2563EB')
                        _name_label = ('الاسم الكامل' if lang == 'ar' else 'Full name')
                        _role_label = ('الدور' if lang == 'ar' else 'Role')
                        st.html(f"""
                        <div style='background:#F8FAFC;border-radius:8px;
                                    padding:10px 12px;margin:4px 0 12px;
                                    border-left:3px solid {_role_color};
                                    font-size:13px;color:#1E293B;'>
                            <div><b>{_name_label}:</b> {_u.get('full_name') or '—'}</div>
                            <div style='margin-top:4px;'><b>{_role_label}:</b>
                                <span style='color:{_role_color};font-weight:600'>
                                    {_role_text}
                                </span>
                            </div>
                        </div>
                        """)

                        # ── Section: Change password ──
                        _pw_section = ('🔑 تغيير كلمة المرور'
                                       if lang == 'ar'
                                       else '🔑 Change password')
                        st.markdown(
                            f"<div style='font-size:13px;font-weight:600;"
                            f"color:#475569;margin:4px 0 6px;'>{_pw_section}</div>",
                            unsafe_allow_html=True,
                        )
                        _new_pw_key = f"cp_{_u['username']}"
                        _new_pw = st.text_input(
                            ('كلمة مرور جديدة' if lang == 'ar' else 'New password'),
                            type='password', key=_new_pw_key,
                            label_visibility='collapsed',
                            placeholder=('كلمة مرور جديدة' if lang == 'ar'
                                         else 'New password'))
                        if st.button(
                                ('💾 حفظ كلمة المرور الجديدة'
                                 if lang == 'ar'
                                 else '💾 Save new password'),
                                key=f"btn_cp_{_u['username']}",
                                use_container_width=True):
                            if _new_pw.strip():
                                if _auth.change_password(_u['username'], _new_pw):
                                    st.success(
                                        ('تم تغيير كلمة المرور بنجاح'
                                         if lang == 'ar'
                                         else 'Password changed successfully'))
                                    st.rerun()
                                else:
                                    st.error(
                                        ('فشل تغيير كلمة المرور' if lang == 'ar'
                                         else 'Failed to change password'))
                            else:
                                st.warning(
                                    ('اكتب كلمة مرور أولاً' if lang == 'ar'
                                     else 'Enter a password first'))

                        # ── Section: Delete user ──
                        st.markdown(
                            "<div style='height:8px;border-top:1px dashed "
                            "#E2E8F0;margin:14px 0 10px;'></div>",
                            unsafe_allow_html=True,
                        )
                        _del_section = ('⚠️ المنطقة الخطرة'
                                        if lang == 'ar'
                                        else '⚠️ Danger zone')
                        st.markdown(
                            f"<div style='font-size:12px;font-weight:600;"
                            f"color:#B91C1C;margin:0 0 6px;'>{_del_section}</div>",
                            unsafe_allow_html=True,
                        )

                        if _is_admin_default or _is_me:
                            _why = ('هذا الحساب محمي من الحذف.'
                                    if lang == 'ar'
                                    else 'This account is protected from deletion.')
                            st.html(f"""
                            <div style='background:#F1F5F9;border-radius:8px;
                                        padding:8px 10px;font-size:12px;
                                        color:#64748B;text-align:center;'>
                                🛡️ {_why}
                            </div>
                            """)
                        else:
                            _confirm_key = f"confirm_del_user_{_u['username']}"
                            if not st.session_state.get(_confirm_key):
                                if st.button(
                                        ('🗑️ حذف هذا المستخدم'
                                         if lang == 'ar'
                                         else '🗑️ Delete this user'),
                                        key=f"btn_del_user_{_u['username']}",
                                        use_container_width=True):
                                    st.session_state[_confirm_key] = True
                                    st.rerun()
                            else:
                                _warn_msg = ('هذا الإجراء لا يمكن التراجع عنه!'
                                             if lang == 'ar'
                                             else 'This action cannot be undone!')
                                st.html(f"""
                                <div style='background:#FEE2E2;border:1px solid #FECACA;
                                            border-radius:8px;padding:8px 10px;
                                            font-size:12px;color:#7F1D1D;
                                            text-align:center;margin-bottom:8px;'>
                                    {_warn_msg}
                                </div>
                                """)
                                _c1, _c2 = st.columns(2)
                                with _c1:
                                    if st.button(
                                            ('✅ تأكيد' if lang == 'ar'
                                             else '✅ Confirm'),
                                            key=f"btn_confirm_del_user_{_u['username']}",
                                            use_container_width=True,
                                            type='primary'):
                                        _auth.delete_user(_u['username'])
                                        st.session_state[_confirm_key] = False
                                        st.success(
                                            (f"تم حذف {_u['username']}"
                                             if lang == 'ar'
                                             else f"Deleted {_u['username']}"))
                                        st.rerun()
                                with _c2:
                                    if st.button(
                                            ('❌ إلغاء' if lang == 'ar'
                                             else '❌ Cancel'),
                                            key=f"btn_cancel_del_user_{_u['username']}",
                                            use_container_width=True):
                                        st.session_state[_confirm_key] = False
                                        st.rerun()

        st.markdown("---")

        # معلومات الجلسة الحالية
        if st.session_state.current_session_id:
            st.markdown(f"### {t('current_session', lang)}")
            st.info(f"**ID:** {st.session_state.current_session_id}")

            if st.session_state.chatbot:
                facts_count = len(st.session_state.chatbot.facts)
                st.metric(t('facts_collected', lang), f"{facts_count}/11")
                st.metric(t('risk_level', lang), st.session_state.chatbot.current_risk_level)
                st.metric(t('confidence', lang), f"{st.session_state.chatbot.confidence_score:.0%}")

        # ===== Admin-only: dashboard + risk gauge + facts table =====
        if is_admin():
            st.markdown("---")
            st.markdown(f"### {t('dashboard', lang)}")
            if st.session_state.chatbot:
                has_facts = len(st.session_state.chatbot.answered_fields) > 0
                risk = st.session_state.chatbot.current_risk_level if has_facts else 'UNKNOWN'
                st.plotly_chart(
                    display_risk_gauge(risk),
                    use_container_width=True
                )
                if st.session_state.chatbot.facts:
                    display_facts_table(st.session_state.chatbot.facts)
                else:
                    st.info(t('no_facts', lang))
            else:
                st.plotly_chart(
                    display_risk_gauge('UNKNOWN'),
                    use_container_width=True
                )
                st.info(t('no_facts', lang))

            with st.expander(t('writing_examples', lang), expanded=False):
                st.html(EXAMPLES_HTML.get(lang, EXAMPLES_HTML['ar']))

            st.markdown("---")

            # الجلسات السابقة (admin — يرى جميع الجلسات لكل المرضى)
            st.markdown(f"### {t('previous_sessions', lang)}")
            sessions = st.session_state.storage.list_sessions()

            # ─── Bulk delete buttons (admin-only, with two-click confirm) ───
            _patient_sessions = [
                s for s in sessions
                if str(s.get('role', '')).lower() != 'admin'
            ]
            _admin_sessions = [
                s for s in sessions
                if str(s.get('role', '')).lower() == 'admin'
            ]

            def _bulk_delete(session_list):
                for s in session_list:
                    try:
                        st.session_state.storage.delete_session(s['session_id'])
                    except Exception:
                        pass

            _bulk_label_p = (f"🗑️ حذف كل جلسات المرضى ({len(_patient_sessions)})"
                             if lang == 'ar'
                             else f"🗑️ Delete all patient sessions ({len(_patient_sessions)})")
            _bulk_label_a = (f"🗑️ حذف كل جلسات الأدمن ({len(_admin_sessions)})"
                             if lang == 'ar'
                             else f"🗑️ Delete all admin sessions ({len(_admin_sessions)})")
            _confirm_p_label = ('⚠️ تأكيد حذف كل جلسات المرضى'
                                if lang == 'ar'
                                else '⚠️ Confirm: delete ALL patient sessions')
            _confirm_a_label = ('⚠️ تأكيد حذف كل جلسات الأدمن'
                                if lang == 'ar'
                                else '⚠️ Confirm: delete ALL admin sessions')

            if _patient_sessions:
                if not st.session_state.get('confirm_del_patients'):
                    if st.button(_bulk_label_p, use_container_width=True,
                                 key='btn_del_patients'):
                        st.session_state.confirm_del_patients = True
                        st.rerun()
                else:
                    if st.button(_confirm_p_label, use_container_width=True,
                                 type='primary', key='confirm_del_patients_btn'):
                        _bulk_delete(_patient_sessions)
                        st.session_state.confirm_del_patients = False
                        st.success(('تم حذف كل جلسات المرضى' if lang == 'ar'
                                    else 'All patient sessions deleted'))
                        st.rerun()
                    if st.button(('إلغاء' if lang == 'ar' else 'Cancel'),
                                 use_container_width=True,
                                 key='cancel_del_patients_btn'):
                        st.session_state.confirm_del_patients = False
                        st.rerun()

            if _admin_sessions:
                if not st.session_state.get('confirm_del_admins'):
                    if st.button(_bulk_label_a, use_container_width=True,
                                 key='btn_del_admins'):
                        st.session_state.confirm_del_admins = True
                        st.rerun()
                else:
                    if st.button(_confirm_a_label, use_container_width=True,
                                 type='primary', key='confirm_del_admins_btn'):
                        _bulk_delete(_admin_sessions)
                        st.session_state.confirm_del_admins = False
                        st.success(('تم حذف كل جلسات الأدمن' if lang == 'ar'
                                    else 'All admin sessions deleted'))
                        st.rerun()
                    if st.button(('إلغاء' if lang == 'ar' else 'Cancel'),
                                 use_container_width=True,
                                 key='cancel_del_admins_btn'):
                        st.session_state.confirm_del_admins = False
                        st.rerun()

            if sessions:
                for session in sessions[:10]:
                    _owner = session.get('username') or '?'
                    _date = (session.get('created_at') or '')[:10]
                    with st.expander(f"👤 {_owner} — {_date}"):
                        st.text(f"{t('date', lang)}: {session['created_at'][:19]}")
                        st.text(f"{t('facts', lang)}: {session['facts_count']}/11")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(t('load', lang), key=f"load_{session['session_id']}"):
                                data = st.session_state.storage.load_session(session['session_id'])
                                if data:
                                    st.session_state.session_data = data
                                    st.session_state.current_session_id = session['session_id']
                                    st.success(t('loaded', lang))
                                    st.rerun()
                        with col2:
                            if st.button(t('delete', lang), key=f"del_{session['session_id']}"):
                                st.session_state.storage.delete_session(session['session_id'])
                                st.rerun()
            else:
                st.info(t('no_sessions', lang))
        else:
            # ═══ Patient: عرض جلسات هذا المريض فقط ═══
            _user = st.session_state.get('user', {}) or {}
            _username = _user.get('username', '')

            st.markdown(f"### {t('previous_sessions', lang)}")
            patient_sessions = st.session_state.storage.list_sessions(
                username=_username
            )
            if patient_sessions:
                for session in patient_sessions[:5]:
                    _date = (session.get('created_at') or '')[:10]
                    with st.expander(f"📋 {_date}"):
                        st.text(f"{t('date', lang)}: {session['created_at'][:19]}")
                        st.text(f"{t('facts', lang)}: {session['facts_count']}/11")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(t('load', lang), key=f"pload_{session['session_id']}"):
                                data = st.session_state.storage.load_session(session['session_id'])
                                if data:
                                    st.session_state.session_data = data
                                    st.session_state.current_session_id = session['session_id']
                                    st.success(t('loaded', lang))
                                    st.rerun()
                        with col2:
                            if st.button(t('delete', lang), key=f"pdel_{session['session_id']}"):
                                st.session_state.storage.delete_session(session['session_id'])
                                st.rerun()
            else:
                st.info(t('no_sessions', lang))

            with st.expander(t('writing_examples', lang), expanded=False):
                st.html(EXAMPLES_HTML.get(lang, EXAMPLES_HTML['ar']))

def render_main_area():
    """عرض المنطقة الرئيسية"""
    lang = get_lang()
    # العنوان
    display_header()

    # ═══ Welcome voice message (plays once per login, patients only) ═══
    if is_patient() and not st.session_state.get('welcome_played', False):
        try:
            import io as _iow
            from gtts import gTTS as _gTTSw
            _user_obj = st.session_state.get('user', {}) or {}
            _name = _user_obj.get('full_name') or _user_obj.get('username', '')
            if lang == 'ar':
                _welcome_text = (f"مرحباً {_name}، أنا نظام هدى الأنصاري الذكي "
                                 f"للكشف عن مخاطر القلب. اضغطي على زر جلسة جديدة "
                                 f"لنبدأ المحادثة.")
            else:
                _welcome_text = (f"Welcome {_name}, I am Huda Al-Ansari smart system "
                                 f"for cardiovascular risk assessment. "
                                 f"Click the new session button to begin our chat.")
            _tts = _gTTSw(text=_welcome_text, lang='ar' if lang == 'ar' else 'en')
            _buf = _iow.BytesIO(); _tts.write_to_fp(_buf); _buf.seek(0)
            st.audio(_buf, format='audio/mp3', autoplay=True)
        except Exception:
            pass
        st.session_state.welcome_played = True

    # عرض الصفحات الخاصة (admin only)
    if is_admin():
        if st.session_state.get('show_comparison', False):
            render_comparison_page(lang)
            return
        if st.session_state.get('show_architecture', False):
            render_architecture_page(lang)
            return
        if st.session_state.get('show_live_demo', False):
            render_live_demo_page(lang)
            return
    else:
        # Patients can never reach admin-only pages
        st.session_state.show_comparison = False
        st.session_state.show_architecture = False
        st.session_state.show_live_demo = False

    # التحقق من وجود جلسة
    if not st.session_state.current_session_id:
        st.info(t('start_session_prompt', lang))

        # عرض معلومات تعريفية
        col1, col2, col3 = st.columns(3)
        cards = [
            ('smart_system_title', 'smart_system_items'),
            ('safe_storage_title', 'safe_storage_items'),
            ('accurate_analysis_title', 'accurate_analysis_items'),
        ]
        for col, (title_key, items_key) in zip([col1, col2, col3], cards):
            with col:
                items = t(items_key, lang)
                items_md = "\n".join(f"- {item}" for item in items)
                st.markdown(f"### {t(title_key, lang)}\n{items_md}")
        return
    
    # عرض التقدم
    facts_count = len(st.session_state.chatbot.facts) if st.session_state.chatbot else 0
    display_progress_bar(facts_count)

    # ═══ Instant trend alerts (queued after last answer) ═══
    # Reset the per-run audio guard at the top of every render pass
    st.session_state.alert_audio_played_this_run = False
    if st.session_state.get('pending_instant_alerts'):
        from ui.patient_report import _render_alert_card
        alerts_to_show = st.session_state.pop('pending_instant_alerts')
        alert_header = ('🔔 مقارنة مع جلستك السابقة' if lang == 'ar'
                        else '🔔 Comparison with your previous session')
        st.markdown(f"#### {alert_header}")
        for alert in alerts_to_show:
            _render_alert_card(alert, lang)
        # Single combined voice cue (avoid stacked audios)
        try:
            import io as _ioa
            from gtts import gTTS as _gTTSa
            _texts = [a.get('tts_text') for a in alerts_to_show if a.get('tts_text')]
            if _texts:
                _full = '. '.join(_texts)
                _tts = _gTTSa(text=_full, lang='ar' if lang == 'ar' else 'en')
                _buf = _ioa.BytesIO(); _tts.write_to_fp(_buf); _buf.seek(0)
                st.audio(_buf, format='audio/mp3', autoplay=True)
                # Mark that an audio has already played in this run so the
                # doctor-message TTS below will skip its own autoplay and
                # avoid overlapping two voices.
                st.session_state.alert_audio_played_this_run = True
        except Exception:
            pass

    # منطقة الحوار
    if True:
        # === Smart Mode vs Classic Mode ===
        is_smart = st.session_state.smart_mode and st.session_state.chatbot and st.session_state.chatbot.conversation_mode == "smart"

        if is_smart:
            # ════════════════════════════════════════════════
            # SMART MODE — محادثة ذكية مع طبيب AI
            # ════════════════════════════════════════════════
            st.markdown(f"## {t('dialog_area', lang)}")

            # Smart mode badge
            badge_color = '#43a047'
            badge_text = t('smart_mode_badge', lang)
            st.html(f"""
            <div style='display: inline-block; background: {badge_color}; color: white;
                        padding: 4px 14px; border-radius: 20px; font-size: 0.85rem;
                        font-weight: 600; margin-bottom: 12px;'>
                {badge_text}
            </div>
            """)

            # عرض المحادثة الذكية
            chat_container = st.container()
            with chat_container:
                for _msg_i, msg in enumerate(st.session_state.smart_chat_history):
                    role = msg.get('role', '')
                    content = msg.get('content', '')
                    extracted = msg.get('extracted_fields', [])

                    if role == 'doctor':
                        st.html(render_doctor_message(content, lang))
                        # TTS: auto-play only the latest new doctor message
                        _is_last_doctor = not any(
                            m.get('role') == 'doctor'
                            for m in st.session_state.smart_chat_history[_msg_i+1:]
                        )
                        _doctor_count = sum(1 for m in st.session_state.smart_chat_history[:_msg_i+1] if m.get('role') == 'doctor')
                        if _is_last_doctor and _doctor_count > st.session_state.tts_played_count:
                            # Skip the doctor-message TTS in this rerun if an
                            # alert audio is already playing — prevents two
                            # voices from overlapping.
                            if st.session_state.get('alert_audio_played_this_run', False):
                                st.session_state.tts_played_count = _doctor_count
                            else:
                                try:
                                    import io as _io, re as _re
                                    from gtts import gTTS
                                    _clean = _re.sub(r'<[^>]+>', '', content)
                                    _tts_lang = 'ar' if lang == 'ar' else 'en'
                                    _tts = gTTS(text=_clean, lang=_tts_lang)
                                    _buf = _io.BytesIO()
                                    _tts.write_to_fp(_buf)
                                    _buf.seek(0)
                                    st.audio(_buf, format='audio/mp3', autoplay=True)
                                    st.session_state.tts_played_count = _doctor_count
                                except Exception:
                                    st.session_state.tts_played_count = _doctor_count
                    elif role == 'patient':
                        st.html(render_patient_message(content, lang))
                        if extracted:
                            st.html(render_extracted_fields_badge(extracted, lang))

            # Progress bar
            available_fields = get_field_names_dict(lang)
            remaining_fields = {}
            if st.session_state.chatbot:
                remaining_fields = {k: v for k, v in available_fields.items()
                                  if k not in st.session_state.chatbot.answered_fields}

            answered_count = len(st.session_state.chatbot.answered_fields) if st.session_state.chatbot else 0
            total = len(available_fields)
            pct = int((answered_count / total) * 100) if total > 0 else 0
            st.progress(pct / 100, text=t('progress_text', lang).format(done=answered_count, total=total, pct=pct))

            if remaining_fields:
                # حقل إدخال المحادثة الذكية
                st.markdown("---")

                # Check for voice transcription to pre-fill
                _voice_default = st.session_state.pop('voice_transcription', '')

                user_input = st.text_area(
                    t('type_your_message', lang),
                    value=_voice_default,
                    height=100,
                    placeholder=t('write_placeholder', lang),
                    key=f"smart_input_{st.session_state.input_key_counter}"
                )

                # Voice input via st.audio_input + Groq Whisper
                audio_input = st.audio_input(
                    t('voice_btn', lang),
                    key=f"voice_input_{st.session_state.input_key_counter}"
                )
                if audio_input:
                    with st.spinner(t('voice_recording', lang)):
                        _transcribed = None
                        if st.session_state.chatbot and hasattr(st.session_state.chatbot, 'groq_client'):
                            _transcribed = st.session_state.chatbot.groq_client.transcribe(audio_input, lang)
                        if _transcribed:
                            st.session_state.voice_transcription = _transcribed
                            st.session_state.input_key_counter += 1
                            st.rerun()
                        else:
                            st.warning(t('voice_not_supported', lang))

                col_send, col_clear = st.columns([3, 1])
                with col_send:
                    send_btn = st.button(t('send_message', lang), use_container_width=True, type="primary", key="smart_send")
                with col_clear:
                    clear_btn = st.button(t('clear', lang), use_container_width=True, key="smart_clear")

                if clear_btn:
                    st.rerun()

                if send_btn and user_input and user_input.strip():
                    # Add patient message to chat history
                    st.session_state.smart_chat_history.append({
                        'role': 'patient',
                        'content': user_input.strip()
                    })

                    # Process with smart input
                    with st.spinner(t('smart_extracting', lang)):
                        result = st.session_state.chatbot.process_smart_input(user_input.strip())

                    # Update extracted fields in last patient message
                    if result.get('extracted_fields'):
                        st.session_state.smart_chat_history[-1]['extracted_fields'] = result['extracted_fields']

                    # Add doctor response
                    if result.get('mode') == 'smart' and result.get('doctor_response'):
                        st.session_state.smart_chat_history.append({
                            'role': 'doctor',
                            'content': result['doctor_response']
                        })
                    elif result.get('next_question'):
                        # Classic fallback — show structured question
                        nq = result['next_question']
                        fallback_msg = nq.get('question', nq.get('message', ''))
                        if fallback_msg:
                            st.session_state.smart_chat_history.append({
                                'role': 'doctor',
                                'content': fallback_msg
                            })
                        st.info(t('smart_fallback_notice', lang))

                    # Save session
                    st.session_state.conversation_steps.append(result)
                    st.session_state.session_data['facts'] = st.session_state.chatbot.facts.copy()
                    st.session_state.storage.save_session(
                        st.session_state.current_session_id,
                        st.session_state.session_data
                    )
                    detect_and_queue_instant_alerts()

                    # Check if all fields collected
                    if result.get('all_complete'):
                        st.success(t('all_fields_collected', lang))
                        st.session_state.show_final_report = True

                    # Clear the input field by changing its key
                    st.session_state.input_key_counter += 1
                    st.rerun()

                elif send_btn:
                    st.warning(t('write_first', lang))

        else:
            # ════════════════════════════════════════════════
            # CLASSIC MODE — الوضع الكلاسيكي (بدون Groq)
            # ════════════════════════════════════════════════
            st.markdown(f"## {t('dialog_area', lang)}")

            # Classic mode badge
            if st.session_state.chatbot:
                badge_text = t('classic_mode_badge', lang)
                st.html(f"""
                <div style='display: inline-block; background: #757575; color: white;
                            padding: 4px 14px; border-radius: 20px; font-size: 0.85rem;
                            font-weight: 600; margin-bottom: 12px;'>
                    {badge_text}
                </div>
                """)

            # عرض المحادثة
            display_conversation_history(st.session_state.conversation_steps)

            # نموذج الإدخال
            st.markdown("---")
            st.markdown(f"### {t('tell_health', lang)}")

            # الحقول المتاحة
            available_fields = get_field_names_dict(lang)

            # استبعاد الحقول المجابة
            if st.session_state.chatbot:
                remaining_fields = {k: v for k, v in available_fields.items()
                                  if k not in st.session_state.chatbot.answered_fields}
            else:
                remaining_fields = available_fields

            if remaining_fields:
                # الحقول المتبقية
                answered_count = len(st.session_state.chatbot.answered_fields) if st.session_state.chatbot else 0
                st.info(f" {t('progress', lang)}: {answered_count}/{len(available_fields)} {t('field', lang)} | {t('remaining', lang)}: {len(remaining_fields)}")

                # عرض الحقول المُجابة
                if st.session_state.chatbot and st.session_state.chatbot.answered_fields:
                    with st.expander(t('completed_fields', lang), expanded=False):
                        answered_display = []
                        for field in st.session_state.chatbot.answered_fields:
                            field_label = available_fields.get(field, field)
                            value = st.session_state.chatbot.facts.get(field, 'N/A')
                            answered_display.append(f"• **{field_label}**: {value}")
                        st.markdown("\n".join(answered_display))

                # عرض الحقول المتبقية بوضوح
                if remaining_fields:
                    with st.expander(f"{t('remaining_fields', lang)} ({len(remaining_fields)} {t('field', lang)})", expanded=True):
                        remaining_display = []
                        for field, field_label in remaining_fields.items():
                            remaining_display.append(f"• **{field_label}** ({field})")
                        st.markdown("\n".join(remaining_display))
                        st.markdown("---")
                        st.markdown(f" **{t('can_write', lang)}**")

                # عرض السؤال التالي (فقط بعد الإجابة على سؤال واحد على الأقل)
                next_q_text = None
                has_answers = st.session_state.chatbot and len(st.session_state.chatbot.answered_fields) > 0
                if has_answers:
                    steps = st.session_state.conversation_steps
                    if steps:
                        last_step = steps[-1]
                        nq = last_step.get('next_question', {})
                        next_q_text = nq.get('question') or nq.get('message')
                if next_q_text:
                    border_side = 'right' if lang == 'ar' else 'left'
                    st.html(f"""
                    <div style='background: linear-gradient(135deg, #fffbeb, #fef3c7);
                                padding: 12px 16px; border-radius: 10px; margin-bottom: 12px;
                                border-{border_side}: 4px solid #f59e0b; display: flex; align-items: center; gap: 10px;'>
                        <span style='font-size: 22px; color: #f59e0b; font-weight: bold;'>?</span>
                        <div>
                            <span style='color: #92400e; font-size: 12px; font-weight: bold;'>{t('next_question_label', lang)}</span><br>
                            <span style='color: #78350f; font-size: 15px; font-weight: 600;'>{next_q_text}</span>
                        </div>
                    </div>
                    """)

                # حقل الإدخال الحر
                user_input = st.text_area(
                    t('write_info', lang),
                    height=120,
                    placeholder=t('write_placeholder', lang),
                    key="free_input",
                    help=t('write_help', lang)
                )

                col_btn1, col_btn2 = st.columns([3, 1])

                with col_btn1:
                    submit_button = st.button(t('analyze_send', lang), use_container_width=True, type="primary")

                with col_btn2:
                    clear_button = st.button(t('clear', lang), use_container_width=True)

                if clear_button:
                    st.rerun()

                if submit_button:
                    if user_input and user_input.strip():
                        # استدعاء دالة معالجة الإدخال الحر
                        results = process_free_input(user_input, remaining_fields)

                        if results['processed_count'] > 0:
                            st.success(t('great_processed', lang).format(count=results['processed_count']))

                            with st.expander(t('info_understood', lang), expanded=True):
                                for item in results['extracted']:
                                    field_label = get_field_name(item.get('field', ''), lang) if lang == 'en' else item.get('field_ar', item.get('field', ''))
                                    st.html(f"""
                                    <div style='background: #e8f5e9; padding: 10px; border-radius: 5px;
                                                margin: 5px 0; border-left: 4px solid #4caf50;'>
                                        <strong>{field_label}:</strong> {item['value']}
                                    </div>
                                    """)

                            if results.get('unprocessed'):
                                st.warning(t('could_not_understand', lang).format(parts=results['unprocessed']))

                            st.html(f"""
                            <div style='background: #e3f2fd; padding: 15px; border-radius: 10px; margin: 10px 0;
                                        border-left: 4px solid #2196f3; text-align: center;'>
                                <strong style='color: #1976d2;'>{t('info_saved', lang)}</strong>
                            </div>
                            """)

                            col_next1, col_next2, col_next3 = st.columns([1, 2, 1])
                            with col_next2:
                                if st.button(t('continue_next', lang), use_container_width=True, type="primary", key="continue_btn"):
                                    with st.spinner(t('transitioning', lang)):
                                        import time
                                        time.sleep(0.3)
                                    st.rerun()
                        else:
                            st.warning(t('could_not_extract', lang))

                            st.html(f"""
                            <div style='background: #fff3cd; padding: 15px; border-radius: 10px;
                                        margin-top: 10px; border-left: 4px solid #ffc107;'>
                                <strong>{t('tips_title', lang)}</strong><br>
                                • {t('tip1', lang)}<br>
                                • {t('tip2', lang)}<br>
                                • {t('tip3', lang)}<br>
                                • {t('tip4', lang)}
                            </div>
                            """)
                    else:
                        st.warning(t('write_first', lang))
            else:
                st.success(t('all_collected', lang))

        # ============================================================
        # v6.0.0: Comprehensive Assessment Display (shared for both modes)
        # ============================================================
        # Check if all facts collected — show assessment for BOTH smart and classic modes
        all_answered = (st.session_state.chatbot and
                       len(st.session_state.chatbot.answered_fields) >= 11)

        if all_answered and st.session_state.chatbot:
                # Get comprehensive final assessment
                final_assessment = st.session_state.chatbot.get_final_assessment()
                
                if final_assessment.get('status') == 'complete':
                    st.markdown("---")
                    st.markdown(f"## {t('comprehensive_assessment', lang)}")
                    st.markdown("---")

                    # ========================================
                    # Section 1: Domain Rules Analysis
                    # ========================================
                    st.markdown(f"### {t('section1_domain', lang)}")
                    st.markdown(f"**{t('section1_subtitle', lang)}**")
                    
                    domain_assessment = final_assessment.get('domain_rules', {})
                    
                    if domain_assessment.get('status') == 'complete':
                        insights = domain_assessment.get('insights', {})
                        
                        risk_level_display = insights.get('risk_level_ar', 'غير معروف') if lang == 'ar' else insights.get('risk_level', 'UNKNOWN')
                        risk_level = insights.get('risk_level', 'UNKNOWN')

                        col1, col2 = st.columns(2)
                        with col1:
                            if risk_level == 'HIGH':
                                st.error(f"**{t('risk_level_label', lang)}:** {risk_level_display}")
                            elif risk_level == 'MEDIUM':
                                st.warning(f"**{t('risk_level_label', lang)}:** {risk_level_display}")
                            else:
                                st.success(f"**{t('risk_level_label', lang)}:** {risk_level_display}")

                        with col2:
                            st.info(f"**{t('rules_applied', lang)}:** {insights.get('triggered_rules_count', 0)}/48")

                        risk_factors_key = 'risk_factors_ar' if lang == 'ar' else 'risk_factors'
                        if insights.get(risk_factors_key, insights.get('risk_factors_ar')):
                            factors = insights.get(risk_factors_key, insights.get('risk_factors_ar', []))
                            with st.expander(t('risk_factors', lang), expanded=True):
                                for factor in factors[:5]:
                                    st.markdown(f"• {factor}")

                        rec_key = 'recommendations_ar' if lang == 'ar' else 'recommendations'
                        if insights.get(rec_key, insights.get('recommendations_ar')):
                            recs = insights.get(rec_key, insights.get('recommendations_ar', []))
                            with st.expander(t('recommendations', lang), expanded=False):
                                for rec in recs[:3]:
                                    st.markdown(f"• {rec}")
                    
                    st.markdown("---")
                    
                    # ========================================
                    # Section 2: Advanced Features Summary
                    # ========================================
                    st.markdown(f"### {t('section2_features', lang)}")
                    st.markdown(f"**{t('section2_subtitle', lang)}**")
                    
                    adv_features = final_assessment.get('advanced_features', {})
                    features_summary = adv_features.get('summary', {})
                    
                    if features_summary:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**{t('classification', lang)}**")
                            st.markdown(f"• **{t('age', lang)}:** {features_summary.get('age_category', 'N/A')}")
                            st.markdown(f"• **{t('cholesterol', lang)}:** {features_summary.get('cholesterol_level', 'N/A')}")
                            st.markdown(f"• **{t('blood_pressure', lang)}:** {features_summary.get('bp_stage', 'N/A')}")

                        with col2:
                            st.markdown(f"**{t('physical_capacity', lang)}**")
                            st.markdown(f"• **{t('capacity', lang)}:** {features_summary.get('exercise_capacity', 'N/A')}")
                            st.markdown(f"• **Framingham:** {features_summary.get('framingham_score', 'N/A')}")
                            st.markdown(f"• **ST Depression:** {features_summary.get('st_depression', 'N/A')}")

                        st.info(f"**{t('total_features', lang)}** {adv_features.get('total_features', 0)} feature")
                    
                    st.markdown("---")
                    
                    # ========================================
                    # Section 3: ML Model Prediction
                    # ========================================
                    st.markdown(f"### {t('section3_ml', lang)}")
                    st.markdown(f"**{t('section3_subtitle', lang)}**")
                    
                    ml_prediction = final_assessment.get('ml_prediction', {})
                    
                    if ml_prediction:
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            prediction = ml_prediction.get('prediction', 'Unknown')
                            if prediction == 'Positive':
                                st.error(f"**{t('prediction', lang)}:** {t('positive', lang)}")
                            else:
                                st.success(f"**{t('prediction', lang)}:** {t('negative', lang)}")

                        with col2:
                            probability = ml_prediction.get('probability', 0)
                            st.metric(f"**{t('probability', lang)}**", f"{probability*100:.1f}%")

                        with col3:
                            risk_level = ml_prediction.get('risk_level', 'UNKNOWN')
                            risk_colors = {
                                'CRITICAL': '',
                                'HIGH': '',
                                'MODERATE': '',
                                'LOW': ''
                            }
                            st.metric(f"**{t('risk_level_label', lang)}**", f"{risk_colors.get(risk_level, '')} {risk_level}")

                        st.caption(f"{t('source', lang)}: {ml_prediction.get('source', 'Unknown')}")
                    
                    st.markdown("---")
                    
                    # ========================================
                    # Section 4: Final Decision
                    # ========================================
                    st.markdown(f"### {t('section4_decision', lang)}")
                    st.markdown(f"**{t('section4_subtitle', lang)}**")
                    
                    final_decision = final_assessment.get('final_decision', {})
                    
                    if final_decision:
                        # Final Risk Level - Big Display
                        final_risk = final_decision.get('final_risk_level', 'UNKNOWN')
                        final_risk_display = final_decision.get('final_risk_level_ar', 'غير معروف') if lang == 'ar' else final_risk
                        confidence = final_decision.get('confidence', 0)

                        decision_text = f"### **{t('final_decision', lang)}:** {final_risk_display} ({final_risk})"
                        confidence_text = f"**{t('confidence', lang)}:** {confidence*100:.0f}%"

                        if final_risk == 'CRITICAL':
                            st.error(decision_text)
                            st.error(confidence_text)
                        elif final_risk == 'HIGH':
                            st.warning(decision_text)
                            st.warning(confidence_text)
                        elif final_risk == 'MODERATE' or final_risk == 'MODERATE-HIGH':
                            st.info(decision_text)
                            st.info(confidence_text)
                        else:
                            st.success(decision_text)
                            st.success(confidence_text)

                        reasoning_text = final_decision.get('reasoning_ar', '') if lang == 'ar' else final_decision.get('reasoning', final_decision.get('reasoning_ar', ''))
                        if reasoning_text:
                            st.markdown(f"**{t('reasoning', lang)}:** {reasoning_text}")

                        sources = final_decision.get('sources', {})
                        if sources:
                            with st.expander(t('decision_sources', lang), expanded=True):
                                col1, col2 = st.columns(2)

                                with col1:
                                    st.markdown(f"**{t('medical_rules', lang)}**")
                                    domain_src = sources.get('domain_rules', {})
                                    st.markdown(f"• {t('risk_level_label', lang)}: {domain_src.get('risk_level', 'N/A')}")
                                    st.markdown(f"• {t('applied_rules', lang)}: {domain_src.get('triggered_rules', 0)}")
                                    st.markdown(f"• Framingham: {domain_src.get('framingham_score', 0)}/7")

                                with col2:
                                    st.markdown(f"**{t('ml_model', lang)}**")
                                    ml_src = sources.get('ml_model', {})
                                    st.markdown(f"• {t('probability', lang)}: {ml_src.get('probability', 0)*100:.1f}%")
                                    st.markdown(f"• {t('prediction', lang)}: {ml_src.get('prediction', 'N/A')}")
                                    st.markdown(f"• {t('source', lang)}: {ml_src.get('source', 'N/A')}")

                        recommendations = final_decision.get('recommendations', [])
                        if recommendations:
                            st.markdown(f"#### {t('final_recommendations', lang)}")
                            for i, rec in enumerate(recommendations[:6], 1):
                                st.markdown(f"{i}. {rec}")

                        st.markdown("---")

                        st.markdown(f"#### {t('decision_tree_title', lang)}")
                        st.markdown(f"**{t('decision_tree_subtitle', lang)}**")

                        _tab_triggered_label = ('القواعد المُطبَّقة' if lang == 'ar'
                                                else 'Triggered Domain Rules')
                        tab1, tab2, tab_triggered, tab3 = st.tabs([
                            t('tab_tree', lang),
                            t('tab_rules', lang),
                            _tab_triggered_label,
                            t('tab_flow', lang)
                        ])

                        with tab1:
                            st.markdown("**sklearn Decision Tree Diagram**")
                            st.markdown("*Trained tree showing decision splits and classifications*")
                            fig_tree = create_decision_tree_diagram(final_decision)
                            st.plotly_chart(fig_tree, use_container_width=True)

                        with tab2:
                            st.markdown("**All 10 Decision Rules**")
                            st.markdown("*Conditions and confidence levels for each rule*")
                            fig_table = create_decision_rules_table(final_decision)
                            st.plotly_chart(fig_table, use_container_width=True)

                        with tab_triggered:
                            # Show ALL triggered domain rules (the N/48 list).
                            _triggered = (final_decision.get('metadata', {})
                                          .get('triggered_rules', []) or [])
                            _total_rules = 48
                            _hdr = (f"**القواعد المُطبَّقة: {len(_triggered)} / {_total_rules}**"
                                    if lang == 'ar'
                                    else f"**Triggered Rules: {len(_triggered)} / {_total_rules}**")
                            _sub = ("الشروط ودرجات الثقة لكل قاعدة (مُرتَّبة حسب الأهمية)"
                                    if lang == 'ar'
                                    else "Conditions and confidence levels for each rule "
                                         "(sorted by importance)")
                            st.markdown(_hdr)
                            st.markdown(f"*{_sub}*")

                            if _triggered:
                                # Kill the hover shadow/highlight on the
                                # triggered-rules dataframe so rows stay
                                # visually calm when the cursor passes over.
                                st.html("""
                                <style>
                                  div[data-testid="stDataFrame"] [role="row"]:hover,
                                  div[data-testid="stDataFrame"] [role="gridcell"]:hover,
                                  div[data-testid="stDataFrameResizable"] [role="row"]:hover,
                                  div[data-testid="stDataFrameResizable"] [role="gridcell"]:hover {
                                      background-color: transparent !important;
                                      box-shadow: none !important;
                                      filter: none !important;
                                  }
                                  div[data-testid="stDataFrame"] div[data-testid="stDataFrameResizable"] *:hover {
                                      box-shadow: none !important;
                                      filter: none !important;
                                  }
                                </style>
                                """)
                                import pandas as _pd
                                _rows = []
                                _max_w = max((float(_r.get('weight', 0)) for _r in _triggered), default=1.0)
                                for _i, _r in enumerate(_triggered, 1):
                                    _rows.append({
                                        '#': _i,
                                        'Rule ID': _r.get('rule_id', f'R{_i}'),
                                        'Feature': _r.get('feature_name', '') or '—',
                                        'Condition': _r.get('condition', ''),
                                        'Weight': round(float(_r.get('weight', 0)), 3),
                                        'Confidence': float(_r.get('confidence', 0)),
                                        'Lift': round(float(_r.get('lift', 0)), 2),
                                    })
                                _df = _pd.DataFrame(_rows)
                                # Use native Streamlit column_config (no matplotlib needed)
                                # to render Weight as a progress bar and Confidence as %.
                                st.dataframe(
                                    _df,
                                    use_container_width=True,
                                    height=560,
                                    hide_index=True,
                                    column_config={
                                        'Weight': st.column_config.ProgressColumn(
                                            'Weight',
                                            help='Rule weight (importance) — relative to the strongest triggered rule',
                                            format='%.3f',
                                            min_value=0.0,
                                            max_value=float(_max_w) or 1.0,
                                        ),
                                        'Confidence': st.column_config.ProgressColumn(
                                            'Confidence',
                                            help='Posterior confidence of the rule (0–100%)',
                                            format='%.1f%%',
                                            min_value=0.0,
                                            max_value=1.0,
                                        ),
                                    },
                                )
                            else:
                                _empty = ('لم يتم تفعيل أي قاعدة (جميع المؤشرات ضمن الحدود الطبيعية).'
                                          if lang == 'ar'
                                          else 'No domain rule was triggered for this patient '
                                               '(all features within normal ranges).')
                                st.info(_empty)

                        with tab3:
                            st.markdown("**Complete Decision Process**")
                            st.markdown("*From input to final decision*")
                            fig_flow = create_simple_decision_tree_flow(final_decision)
                            st.plotly_chart(fig_flow, use_container_width=True)
                    
                    st.markdown("---")

                    # ========================================
                    # PDF Report Download (Arabic-aware)
                    # ========================================
                    _pdf_label = ('⬇️ تحميل التقرير PDF' if lang == 'ar'
                                  else '⬇️ Download PDF Report')
                    _pdf_help = ('سيتم تنزيل التقرير بصيغة PDF مع دعم كامل للغة العربية'
                                 if lang == 'ar'
                                 else 'Generates an Arabic-aware PDF copy of this assessment')
                    try:
                        from core.pdf_report import generate_pdf_report
                        _user_obj = st.session_state.get('user', {}) or {}
                        _patient_name = (_user_obj.get('full_name')
                                         or _user_obj.get('username', ''))
                        _session_id_for_pdf = st.session_state.get('current_session_id', '')
                        _facts_for_pdf = (st.session_state.chatbot.facts
                                          if st.session_state.chatbot else {})
                        _pdf_bytes = generate_pdf_report(
                            final_assessment,
                            lang=lang,
                            patient_name=_patient_name,
                            session_id=_session_id_for_pdf,
                            facts=_facts_for_pdf,
                        )
                        _pdf_filename = (
                            f"assessment_{_session_id_for_pdf or 'report'}.pdf"
                        )
                        st.download_button(
                            label=_pdf_label,
                            data=_pdf_bytes,
                            file_name=_pdf_filename,
                            mime='application/pdf',
                            help=_pdf_help,
                            use_container_width=True,
                            type='primary',
                        )
                    except Exception as _pdf_err:
                        st.warning(
                            (f"تعذّر إنشاء PDF: {_pdf_err}"
                             if lang == 'ar'
                             else f"Could not build PDF: {_pdf_err}")
                        )

                    st.markdown("---")

                    # ========================================
                    # Section 5: Groq AI Enhancement (v7.0.0)
                    # ========================================
                    groq_interpretation = final_assessment.get('groq_interpretation')
                    groq_recommendations = final_assessment.get('groq_recommendations')

                    if groq_interpretation or groq_recommendations:
                        st.markdown(f"### {t('section5_groq', lang)}")
                        st.markdown(f"**{t('section5_subtitle', lang)}**")

                        if groq_interpretation:
                            st.html(f"""
                            <div style='background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
                                        padding: 25px; border-radius: 16px; margin: 15px 0;
                                        border-left: 5px solid #4caf50;
                                        box-shadow: 0 4px 12px rgba(76,175,80,0.15);'>
                                <div style='font-size: 1.1rem; font-weight: 700; color: #2e7d32;
                                            margin-bottom: 12px; display: flex; align-items: center; gap: 8px;'>
                                    {t('ai_interpretation', lang)}
                                </div>
                                <div style='color: #1b5e20; font-size: 1.05rem; line-height: 1.8;'>
                                    {groq_interpretation}
                                </div>
                            </div>
                            """)

                        if groq_recommendations:
                            recs_html = "".join([
                                f"<div style='background: rgba(255,255,255,0.7); padding: 12px 16px; "
                                f"margin: 8px 0; border-radius: 10px; font-size: 1rem; "
                                f"border-left: 3px solid #7b1fa2;'>{rec}</div>"
                                for rec in groq_recommendations
                            ])
                            st.html(f"""
                            <div style='background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
                                        padding: 25px; border-radius: 16px; margin: 15px 0;
                                        border-left: 5px solid #9c27b0;
                                        box-shadow: 0 4px 12px rgba(156,39,176,0.15);'>
                                <div style='font-size: 1.1rem; font-weight: 700; color: #6a1b9a;
                                            margin-bottom: 12px;'>
                                    {t('personalized_recommendations', lang)}
                                </div>
                                <div>{recs_html}</div>
                            </div>
                            """)

                        st.caption(t('powered_by_groq', lang))
                        st.markdown("---")

                    elif not final_assessment.get('groq_available', False):
                        st.info(t('groq_not_connected', lang))
                        st.markdown("---")

                    # Optional: Full JSON view
                    with st.expander(t('show_full_json', lang), expanded=False):
                        st.json(final_assessment)

                # The legacy "Show Final Report" button has been removed; the
                # downloadable Arabic-aware PDF report now serves the same
                # purpose in a much cleaner format.

    # (لوحة المعلومات انتقلت للشريط الجانبي)

    # ═══ End-of-session longitudinal report ═══
    _user = st.session_state.get('user', {}) or {}
    _username = _user.get('username', '')
    _chatbot = st.session_state.get('chatbot')
    if _username and _chatbot and _chatbot.facts:
        _tracked_answered = [f for f in _chatbot.facts if f in TRACKED_FIELDS]
        _show_report = st.session_state.get('show_final_report', False)

        if _tracked_answered:
            # Manual "show report" toggle — the report is rendered ONLY when
            # the patient has explicitly turned it on (button click) or when
            # the chatbot itself flips show_final_report=True after all 11
            # fields are collected. The previous auto-show on >= 3 fields
            # was unwanted, so it has been removed.
            _hide_label = ('🔽 إخفاء تقرير تطور حالتي'
                           if lang == 'ar' else '🔽 Hide my trend report')
            _show_label = ('📊 عرض تقرير تطور حالتي'
                           if lang == 'ar' else '📊 Show my trend report')
            _rep_label = _hide_label if _show_report else _show_label
            if st.button(_rep_label, use_container_width=True, key='toggle_report_btn'):
                st.session_state.show_final_report = not _show_report
                st.rerun()

            if _show_report:
                render_patient_report(
                    _username,
                    _chatbot.facts,
                    st.session_state.get('current_session_id', ''),
                    lang,
                )

#
#  التطبيق الرئيسي | Main Application
#

def main():
    """الوظيفة الرئيسية"""
    init_streamlit_config()

    # ==== Authentication gate ====
    # Block everything until the user signs in.
    if not require_login():
        return

    initialize_session_state()

    # RTL/LTR direction based on language
    lang = get_lang()
    if lang == 'en':
        st.markdown("""<style>
            .stApp, .main, .block-container { direction: ltr !important; text-align: left !important; }
            .stSidebar { direction: ltr !important; text-align: left !important; }
        </style>""", unsafe_allow_html=True)
    else:
        st.markdown("""<style>
            .stApp, .main, .block-container { direction: rtl !important; text-align: right !important; }
            .stSidebar { direction: rtl !important; text-align: right !important; }
        </style>""", unsafe_allow_html=True)

    render_sidebar()
    render_main_area()

    # Footer
    st.markdown("---")

if __name__ == "__main__":
    main()
