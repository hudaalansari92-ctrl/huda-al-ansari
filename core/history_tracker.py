"""
History Tracker — Longitudinal Patient Monitoring

For each patient (identified by username), compares new measurements with
previously recorded values and generates trend alerts:
    improved / stable / worsened / crisis

Thresholds are based on medical standards:
    - AHA/ACC 2017 (Blood Pressure)
    - ACC/AHA (Cholesterol)
    - ADA (Fasting Blood Sugar — stored but binary in this schema)
    - AHA (Heart Rate)
"""
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


# ═══════════════════════════════════════════════════════════════════
#  Medical Thresholds (clinically meaningful change magnitudes)
# ═══════════════════════════════════════════════════════════════════
# For each numeric field we track:
#   - "meaningful": minimum abs(change) to flag improvement/worsening
#   - "direction": which direction counts as IMPROVEMENT
#         "down" => lower = better  (e.g. BP, cholesterol, Oldpeak)
#         "up"   => higher = better (e.g. MaxHR for young healthy folks — nuanced)
#   - "crisis_high" / "crisis_low": emergency thresholds
#   - "unit": display unit
# ═══════════════════════════════════════════════════════════════════

FIELD_THRESHOLDS: Dict[str, Dict[str, Any]] = {
    # Systolic Blood Pressure (mmHg) — AHA 2017
    "BloodPressure": {
        "meaningful": 5,
        "strong_change": 10,
        "direction": "down",
        "crisis_high": 180,
        "crisis_low": 80,
        "normal_max": 120,
        "unit": "mmHg",
        "name_ar": "ضغط الدم",
        "name_en": "Blood Pressure",
    },
    # Total Cholesterol (mg/dL) — ACC/AHA
    "Cholesterol": {
        "meaningful": 10,
        "strong_change": 25,
        "direction": "down",
        "crisis_high": 300,
        "crisis_low": None,
        "normal_max": 200,
        "unit": "mg/dL",
        "name_ar": "الكوليسترول",
        "name_en": "Cholesterol",
    },
    # Max Heart Rate (bpm) — context-dependent; we flag large swings
    "MaxHR": {
        "meaningful": 10,
        "strong_change": 20,
        "direction": "neutral",  # neither up nor down is "improvement" alone
        "crisis_high": 200,
        "crisis_low": 40,
        "normal_max": 100,  # resting reference; MaxHR is exercise-induced
        "unit": "bpm",
        "name_ar": "معدل ضربات القلب",
        "name_en": "Heart Rate",
    },
    # ST Depression (mm) — lower = better (less ischemia)
    "Oldpeak": {
        "meaningful": 0.5,
        "strong_change": 1.0,
        "direction": "down",
        "crisis_high": 3.0,
        "crisis_low": None,
        "normal_max": 1.0,
        "unit": "mm",
        "name_ar": "انخفاض ST",
        "name_en": "ST Depression",
    },
}


# ═══════════════════════════════════════════════════════════════════
#  HistoryTracker
# ═══════════════════════════════════════════════════════════════════

class HistoryTracker:
    """Per-patient longitudinal value tracker."""

    def __init__(self, sessions_dir: str = "sessions"):
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(exist_ok=True)

    # ---------- Patient history lookup ----------
    def get_patient_sessions(self, username: str,
                              exclude_session_id: Optional[str] = None) -> List[Dict]:
        """Return chronologically sorted list of sessions belonging to `username`."""
        if not username:
            return []
        username = username.strip().lower()
        sessions: List[Dict] = []
        for file in self.sessions_dir.glob("*.json"):
            if exclude_session_id and file.stem == exclude_session_id:
                continue
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if (data.get('username', '') or '').strip().lower() == username:
                    data['_session_id'] = file.stem
                    sessions.append(data)
            except Exception:
                continue
        sessions.sort(key=lambda s: s.get('created_at', ''))
        return sessions

    def get_field_history(self, username: str, field: str,
                          exclude_session_id: Optional[str] = None) -> List[Tuple[str, float]]:
        """
        Return [(timestamp, value), ...] for the given field across all
        of this patient's past sessions, oldest → newest.
        """
        result: List[Tuple[str, float]] = []
        for s in self.get_patient_sessions(username, exclude_session_id):
            facts = s.get('facts', {}) or {}
            if field in facts:
                try:
                    val = float(facts[field])
                    ts = s.get('created_at', '')
                    result.append((ts, val))
                except (ValueError, TypeError):
                    continue
        return result

    # ---------- Comparison ----------
    def compare_with_previous(self, username: str, field: str,
                              current_value: float,
                              exclude_session_id: Optional[str] = None
                              ) -> Optional[Dict[str, Any]]:
        """
        Compare current_value with the most recent previous value for this
        patient+field. Returns None if no prior data exists or field is not tracked.
        """
        if field not in FIELD_THRESHOLDS:
            return None
        try:
            current_value = float(current_value)
        except (ValueError, TypeError):
            return None

        history = self.get_field_history(username, field, exclude_session_id)
        if not history:
            return None  # first time — no comparison possible

        prev_ts, prev_value = history[-1]
        change = current_value - prev_value
        cfg = FIELD_THRESHOLDS[field]
        meaningful = cfg['meaningful']
        strong = cfg['strong_change']
        direction = cfg['direction']

        # Classify trend
        abs_change = abs(change)
        if abs_change < meaningful:
            trend = 'stable'
        else:
            if direction == 'down':
                trend = 'improved' if change < 0 else 'worsened'
            elif direction == 'up':
                trend = 'improved' if change > 0 else 'worsened'
            else:  # neutral
                trend = 'changed'

        strength = 'strong' if abs_change >= strong else 'mild'

        # Crisis check
        crisis = False
        if cfg.get('crisis_high') is not None and current_value >= cfg['crisis_high']:
            crisis = True
        if cfg.get('crisis_low') is not None and current_value <= cfg['crisis_low']:
            crisis = True

        percent_change = (change / prev_value * 100) if prev_value else 0.0

        return {
            'field': field,
            'field_name_ar': cfg['name_ar'],
            'field_name_en': cfg['name_en'],
            'unit': cfg['unit'],
            'current': current_value,
            'previous': prev_value,
            'previous_date': prev_ts,
            'change': round(change, 2),
            'percent_change': round(percent_change, 1),
            'trend': trend,          # improved | stable | worsened | changed
            'strength': strength,    # mild | strong
            'crisis': crisis,
            'history_length': len(history),
        }

    # ---------- Alert text generation ----------
    @staticmethod
    def generate_alert_text(comparison: Dict[str, Any], lang: str = 'ar') -> Dict[str, str]:
        """
        Generate a user-facing alert from a comparison dict.
        Returns dict with: title, message, tts_text, color, icon.
        """
        if not comparison:
            return {}

        field_name = comparison['field_name_ar'] if lang == 'ar' else comparison['field_name_en']
        current = comparison['current']
        previous = comparison['previous']
        change = comparison['change']
        abs_change = abs(change)
        unit = comparison['unit']
        trend = comparison['trend']
        crisis = comparison['crisis']

        sign = '+' if change > 0 else ''

        # Crisis takes precedence
        if crisis:
            if lang == 'ar':
                title = f"🚨 تنبيه طارئ — {field_name}"
                message = (f"قيمتك الحالية {current} {unit} ضمن منطقة الخطر. "
                           f"ننصح بمراجعة طبيب فوراً.")
                tts = f"تنبيه طارئ، {field_name} عندك {current}، يرجى مراجعة طبيب فوراً"
            else:
                title = f"Emergency Alert — {field_name}"
                message = (f"Your current {field_name.lower()} of {current} {unit} is in the danger zone. "
                           f"Please consult a doctor immediately.")
                tts = f"Emergency alert. Your {field_name} is {current}. Please see a doctor immediately."
            return {'title': title, 'message': message, 'tts_text': tts,
                    'color': '#DC2626', 'icon': '🚨', 'level': 'crisis'}

        # Normal trend alerts
        if trend == 'improved':
            if lang == 'ar':
                title = f"تحسّن في {field_name}"
                message = (f"ممتاز! {field_name} انخفض من {previous} إلى {current} {unit} "
                           f"({sign}{change} {unit}). استمر على نفس المسار.")
                tts = f"خبر ممتاز، {field_name} تحسّن من {previous} إلى {current}. استمر على نفس المسار."
            else:
                title = f"Improvement in {field_name}"
                message = (f"Great news! Your {field_name.lower()} went from {previous} to {current} {unit} "
                           f"({sign}{change} {unit}). Keep it up!")
                tts = f"Great news. Your {field_name} improved from {previous} to {current}. Keep it up."
            return {'title': title, 'message': message, 'tts_text': tts,
                    'color': '#059669', 'icon': '🟢', 'level': 'improved'}

        if trend == 'worsened':
            if lang == 'ar':
                title = f"تدهور في {field_name}"
                message = (f"انتبه! {field_name} ارتفع من {previous} إلى {current} {unit} "
                           f"({sign}{change} {unit}). يُنصح بمراجعة طبيبك.")
                tts = f"انتبه، {field_name} ارتفع من {previous} إلى {current}. يُنصح بمراجعة طبيبك."
            else:
                title = f"Worsening in {field_name}"
                message = (f"Warning! Your {field_name.lower()} increased from {previous} to {current} {unit} "
                           f"({sign}{change} {unit}). Consider consulting your doctor.")
                tts = f"Warning. Your {field_name} increased from {previous} to {current}. Please consult your doctor."
            return {'title': title, 'message': message, 'tts_text': tts,
                    'color': '#DC2626', 'icon': '🔴', 'level': 'worsened'}

        if trend == 'changed':
            if lang == 'ar':
                title = f"تغيّر ملحوظ في {field_name}"
                message = f"{field_name} تغيّر من {previous} إلى {current} {unit} ({sign}{change} {unit})."
                tts = f"{field_name} تغيّر من {previous} إلى {current}."
            else:
                title = f"Notable change in {field_name}"
                message = f"Your {field_name.lower()} changed from {previous} to {current} {unit} ({sign}{change} {unit})."
                tts = f"Your {field_name} changed from {previous} to {current}."
            return {'title': title, 'message': message, 'tts_text': tts,
                    'color': '#F59E0B', 'icon': '🟡', 'level': 'changed'}

        # stable
        if lang == 'ar':
            title = f"{field_name} مستقر"
            message = (f"{field_name} مستقر عند {current} {unit} "
                       f"(كان {previous} {unit}). حافظ على نمط حياتك الحالي.")
            tts = ""  # no TTS for stable — avoid noise
        else:
            title = f"{field_name} stable"
            message = (f"Your {field_name.lower()} is stable at {current} {unit} "
                       f"(was {previous} {unit}). Keep your current lifestyle.")
            tts = ""
        return {'title': title, 'message': message, 'tts_text': tts,
                'color': '#64748B', 'icon': '🟡', 'level': 'stable'}

    # ---------- Full-session comparison ----------
    def analyze_session(self, username: str, facts: Dict[str, Any],
                        exclude_session_id: Optional[str] = None,
                        lang: str = 'ar') -> List[Dict[str, Any]]:
        """Run comparison on every tracked field in `facts`. Returns a list of alerts."""
        alerts: List[Dict[str, Any]] = []
        for field in FIELD_THRESHOLDS:
            if field not in facts:
                continue
            comp = self.compare_with_previous(
                username, field, facts[field], exclude_session_id
            )
            if not comp:
                continue
            alert = self.generate_alert_text(comp, lang)
            if not alert:
                continue
            alert['comparison'] = comp
            alerts.append(alert)
        # Prioritize: crisis > worsened > improved > changed > stable
        order = {'crisis': 0, 'worsened': 1, 'improved': 2, 'changed': 3, 'stable': 4}
        alerts.sort(key=lambda a: order.get(a['level'], 99))
        return alerts
