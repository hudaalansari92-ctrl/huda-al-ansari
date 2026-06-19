"""Authentication module for role-based access control."""
from .auth_manager import AuthManager
from .login_ui import render_login_page, render_logout_button, require_login, is_admin, is_patient

__all__ = [
    'AuthManager',
    'render_login_page',
    'render_logout_button',
    'require_login',
    'is_admin',
    'is_patient',
]
