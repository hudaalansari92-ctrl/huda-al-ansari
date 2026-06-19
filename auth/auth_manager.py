"""
Authentication Manager
Handles user registration, login verification, and password hashing.
"""
import json
import hashlib
import secrets
from pathlib import Path
from typing import Dict, Optional, List


class AuthManager:
    """Manages user accounts with roles: 'admin' or 'patient'."""

    def __init__(self, users_file: Optional[str] = None):
        if users_file is None:
            users_file = Path(__file__).parent / 'users.json'
        self.users_file = Path(users_file)
        self._ensure_defaults()

    # ---------- Password helpers ----------
    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        """Hash a password with a salt using SHA-256."""
        return hashlib.sha256((salt + password).encode('utf-8')).hexdigest()

    @staticmethod
    def _generate_salt() -> str:
        return secrets.token_hex(16)

    # ---------- User storage ----------
    def _load_users(self) -> Dict:
        if not self.users_file.exists():
            return {}
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_users(self, users: Dict) -> None:
        self.users_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)

    def _ensure_defaults(self) -> None:
        """Create default admin & patient accounts on first run."""
        users = self._load_users()
        changed = False
        if 'admin' not in users:
            salt = self._generate_salt()
            users['admin'] = {
                'salt': salt,
                'password_hash': self._hash_password('admin123', salt),
                'role': 'admin',
                'full_name': 'Administrator',
            }
            changed = True
        if 'patient' not in users:
            salt = self._generate_salt()
            users['patient'] = {
                'salt': salt,
                'password_hash': self._hash_password('patient123', salt),
                'role': 'patient',
                'full_name': 'Default Patient',
            }
            changed = True
        if changed:
            self._save_users(users)

    # ---------- Public API ----------
    def verify(self, username: str, password: str) -> Optional[Dict]:
        """Verify credentials. Returns user info dict on success, None on failure."""
        if not username or not password:
            return None
        users = self._load_users()
        user = users.get(username.strip().lower())
        if not user:
            return None
        expected_hash = self._hash_password(password, user['salt'])
        if secrets.compare_digest(expected_hash, user['password_hash']):
            return {
                'username': username.strip().lower(),
                'role': user.get('role', 'patient'),
                'full_name': user.get('full_name', username),
            }
        return None

    def add_user(self, username: str, password: str,
                 role: str = 'patient', full_name: str = '') -> bool:
        """Add a new user. Returns True if added, False if username already exists."""
        username = username.strip().lower()
        if not username or not password:
            return False
        if role not in ('admin', 'patient'):
            role = 'patient'
        users = self._load_users()
        if username in users:
            return False
        salt = self._generate_salt()
        users[username] = {
            'salt': salt,
            'password_hash': self._hash_password(password, salt),
            'role': role,
            'full_name': full_name or username,
        }
        self._save_users(users)
        return True

    def delete_user(self, username: str) -> bool:
        """Remove a user. Returns True if deleted."""
        username = username.strip().lower()
        users = self._load_users()
        if username in users and username != 'admin':
            del users[username]
            self._save_users(users)
            return True
        return False

    def change_password(self, username: str, new_password: str) -> bool:
        """Change a user's password."""
        username = username.strip().lower()
        users = self._load_users()
        if username not in users or not new_password:
            return False
        salt = self._generate_salt()
        users[username]['salt'] = salt
        users[username]['password_hash'] = self._hash_password(new_password, salt)
        self._save_users(users)
        return True

    def list_users(self) -> List[Dict]:
        """Return a list of users (without password hashes)."""
        users = self._load_users()
        return [
            {
                'username': u,
                'role': info.get('role', 'patient'),
                'full_name': info.get('full_name', u),
            }
            for u, info in users.items()
        ]
