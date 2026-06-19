"""
Login UI
Provides the login page, logout button, and role-checking helpers.
"""
import streamlit as st
from .auth_manager import AuthManager


# Translations for the login UI
LOGIN_TEXT = {
    'ar': {
        'title': 'تسجيل الدخول',
        'subtitle': 'Healthcare Chatbot System Based on Intelligent Techniques',
        'username': 'اسم المستخدم',
        'password': 'كلمة المرور',
        'login_btn': 'دخول',
        'invalid': 'اسم المستخدم أو كلمة المرور غير صحيحة',
        'welcome': 'مرحباً',
        'role_admin': 'مسؤول النظام',
        'role_patient': 'مريض',
        'logout': 'تسجيل الخروج',
        'logged_in_as': 'تم تسجيل الدخول كـ',
        'demo_accounts': 'حسابات تجريبية',
        'admin_label': 'مسؤول',
        'patient_label': 'مريض',
        'lang_label': 'اللغة / Language',
    },
    'en': {
        'title': 'Login',
        'subtitle': 'Healthcare Chatbot System Based on Intelligent Techniques',
        'username': 'Username',
        'password': 'Password',
        'login_btn': 'Sign In',
        'invalid': 'Invalid username or password',
        'welcome': 'Welcome',
        'role_admin': 'Administrator',
        'role_patient': 'Patient',
        'logout': 'Logout',
        'logged_in_as': 'Logged in as',
        'demo_accounts': 'Demo Accounts',
        'admin_label': 'Admin',
        'patient_label': 'Patient',
        'lang_label': 'Language',
    }
}


def _get_auth_manager() -> AuthManager:
    if 'auth_manager' not in st.session_state:
        st.session_state.auth_manager = AuthManager()
    return st.session_state.auth_manager


def _get_login_lang() -> str:
    return st.session_state.get('login_lang', 'ar')


def render_login_page() -> None:
    """Full-page login form. Sets st.session_state.user on success and reruns."""
    auth = _get_auth_manager()
    lang = _get_login_lang()
    T = LOGIN_TEXT[lang]

    direction = 'rtl' if lang == 'ar' else 'ltr'
    align = 'right' if lang == 'ar' else 'left'

    # Hide default Streamlit chrome on the login page
    st.markdown(f"""
    <style>
        .stApp, .main, .block-container {{
            direction: {direction} !important;
            text-align: {align} !important;
        }}
        [data-testid="stSidebar"] {{ display: none; }}
        [data-testid="collapsedControl"] {{ display: none; }}
        .login-card {{
            max-width: 460px;
            margin: 40px auto;
            padding: 36px 32px;
            background: white;
            border-radius: 18px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.08);
            border: 1px solid #e5e7eb;
        }}
        .login-hero {{
            text-align: center;
            margin-bottom: 24px;
        }}
        .login-hero h1 {{
            color: #059669;
            margin: 0 0 6px 0;
            font-size: 28px;
        }}
        .login-hero p {{
            color: #64748B;
            margin: 0;
            font-size: 14px;
        }}
        .demo-box {{
            margin-top: 18px;
            padding: 12px 14px;
            background: #F0FDF4;
            border: 1px dashed #34D399;
            border-radius: 10px;
            font-size: 13px;
            color: #065F46;
            text-align: {align};
        }}
        .demo-box code {{
            background: white;
            padding: 2px 6px;
            border-radius: 4px;
            color: #1E293B;
        }}
    </style>
    """, unsafe_allow_html=True)

    # Center the form using columns
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown(f"""
        <div class="login-hero">
            <h1>&#128151; {T['title']}</h1>
            <p>{T['subtitle']}</p>
        </div>
        """, unsafe_allow_html=True)

        # Language switcher
        st.selectbox(
            T['lang_label'],
            options=['ar', 'en'],
            index=0 if lang == 'ar' else 1,
            format_func=lambda x: 'العربية' if x == 'ar' else 'English',
            key='login_lang',
        )

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(T['username'], key='login_username')
            password = st.text_input(T['password'], type='password', key='login_password')
            submitted = st.form_submit_button(T['login_btn'], use_container_width=True, type='primary')

        if submitted:
            user = auth.verify(username, password)
            if user:
                st.session_state.user = user
                st.session_state.language_select = lang  # propagate chosen language
                st.rerun()
            else:
                st.error(T['invalid'])

        # Demo accounts hint
        st.markdown(f"""
        <div class="demo-box">
            <b>{T['demo_accounts']}:</b><br>
            &#128272; {T['admin_label']}: <code>admin</code> / <code>admin123</code><br>
            &#128100; {T['patient_label']}: <code>patient</code> / <code>patient123</code>
        </div>
        """, unsafe_allow_html=True)


def render_logout_button() -> None:
    """Render a logout button + user info. Should be called inside the sidebar."""
    if 'user' not in st.session_state:
        return
    user = st.session_state.user
    lang = st.session_state.get('language_select', 'ar')
    T = LOGIN_TEXT.get(lang, LOGIN_TEXT['ar'])

    role_display = T['role_admin'] if user['role'] == 'admin' else T['role_patient']
    role_color = '#059669' if user['role'] == 'admin' else '#2563EB'

    st.markdown(f"""
    <div style="padding: 10px 12px; background: #F8FAFC; border-radius: 10px;
                border-left: 3px solid {role_color}; margin-bottom: 8px;">
        <div style="font-size: 12px; color: #64748B;">{T['logged_in_as']}</div>
        <div style="font-size: 15px; font-weight: 600; color: #1E293B;">
            {user['full_name']}
        </div>
        <div style="font-size: 12px; color: {role_color}; font-weight: 600;">
            &#9679; {role_display}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button(T['logout'], use_container_width=True, key='logout_btn'):
        # Clear user-related session state but keep language
        saved_lang = st.session_state.get('language_select', 'ar')
        for key in list(st.session_state.keys()):
            if key not in ('auth_manager',):
                del st.session_state[key]
        st.session_state.language_select = saved_lang
        st.rerun()


def require_login() -> bool:
    """Returns True if user is logged in, otherwise renders the login page and returns False."""
    if 'user' not in st.session_state or not st.session_state.user:
        render_login_page()
        return False
    return True


def is_admin() -> bool:
    user = st.session_state.get('user')
    return bool(user and user.get('role') == 'admin')


def is_patient() -> bool:
    user = st.session_state.get('user')
    return bool(user and user.get('role') == 'patient')
