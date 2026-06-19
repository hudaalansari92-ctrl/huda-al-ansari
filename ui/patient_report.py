"""
Patient Report UI — End-of-session longitudinal comparison report.

Renders:
  - Alert cards for each tracked field (improved/stable/worsened/crisis)
  - Line charts for historical trends
  - Audio summary of key changes
"""
import io
import streamlit as st
import plotly.graph_objects as go
from typing import Dict, List, Any

from core.history_tracker import HistoryTracker, FIELD_THRESHOLDS


# ═══════════════════════════════════════════════════════════
#  Helpers
# ═══════════════════════════════════════════════════════════

def _card_bg(level: str) -> str:
    return {
        'crisis':   '#FEE2E2',
        'worsened': '#FEE2E2',
        'improved': '#D1FAE5',
        'changed':  '#FEF3C7',
        'stable':   '#F1F5F9',
    }.get(level, '#F1F5F9')


def _render_alert_card(alert: Dict[str, Any], lang: str = 'ar') -> None:
    bg = _card_bg(alert.get('level', 'stable'))
    color = alert.get('color', '#64748B')
    icon = alert.get('icon', 'ℹ️')
    title = alert.get('title', '')
    message = alert.get('message', '')
    align = 'right' if lang == 'ar' else 'left'
    direction = 'rtl' if lang == 'ar' else 'ltr'

    comp = alert.get('comparison', {})
    current = comp.get('current', '')
    previous = comp.get('previous', '')
    unit = comp.get('unit', '')
    change = comp.get('change', 0)
    sign = '+' if change and change > 0 else ''

    st.html(f"""
    <div style="direction: {direction}; text-align: {align};
                background: {bg}; border-left: 5px solid {color};
                padding: 14px 18px; border-radius: 10px; margin: 10px 0;">
        <div style="font-size: 18px; font-weight: 700; color: {color}; margin-bottom: 6px;">
            {icon} {title}
        </div>
        <div style="font-size: 14px; color: #1E293B; margin-bottom: 8px;">
            {message}
        </div>
        <div style="display: flex; gap: 18px; font-size: 13px; color: #475569;">
            <div><b>{'السابق' if lang == 'ar' else 'Previous'}:</b> {previous} {unit}</div>
            <div><b>{'الحالي' if lang == 'ar' else 'Current'}:</b> {current} {unit}</div>
            <div><b>{'الفرق' if lang == 'ar' else 'Change'}:</b> {sign}{change} {unit}</div>
        </div>
    </div>
    """)


def _render_trend_chart(history: List, field: str, lang: str = 'ar') -> None:
    """
    Line chart of the full history for one field.

    Properly parses ISO timestamps so multiple sessions on the same day
    are plotted at their actual time, distinguishes the current point
    from historical ones, and shows clear value labels on every point.
    """
    from datetime import datetime
    cfg = FIELD_THRESHOLDS.get(field, {})
    field_name = cfg.get('name_ar') if lang == 'ar' else cfg.get('name_en')
    unit = cfg.get('unit', '')

    if not history:
        return

    # ---------- Parse timestamps to real datetime objects ----------
    def _parse(ts):
        if isinstance(ts, datetime):
            return ts
        if not ts:
            return None
        try:
            # Accept ISO with or without timezone
            return datetime.fromisoformat(str(ts).replace('Z', ''))
        except Exception:
            try:
                return datetime.strptime(str(ts)[:19], '%Y-%m-%dT%H:%M:%S')
            except Exception:
                return None

    parsed = []
    for ts, val in history:
        dt = _parse(ts)
        try:
            v = float(val)
        except (TypeError, ValueError):
            continue
        parsed.append((dt, v))

    # The last point (current) may have no timestamp — anchor it to "now"
    if parsed and parsed[-1][0] is None:
        parsed[-1] = (datetime.now(), parsed[-1][1])
    # Anything else missing a timestamp is dropped (cannot be plotted on a date axis)
    parsed = [(dt, v) for dt, v in parsed if dt is not None]
    if not parsed:
        return
    parsed.sort(key=lambda p: p[0])

    dates = [dt for dt, _ in parsed]
    values = [v for _, v in parsed]
    n = len(values)

    # Split historical vs current (last point)
    hist_dates, hist_values = dates[:-1], values[:-1]
    cur_date, cur_value = dates[-1], values[-1]

    # Tick text — keep the date readable, append HH:MM only when needed
    same_day = len({d.date() for d in dates}) < n  # any duplicates?
    fmt = '%Y-%m-%d %H:%M' if same_day else '%Y-%m-%d'
    hover_dates = [d.strftime('%Y-%m-%d %H:%M') for d in dates]

    fig = go.Figure()

    # ---------- Historical points (line + small dots) ----------
    if hist_dates:
        fig.add_trace(go.Scatter(
            x=hist_dates, y=hist_values,
            mode='lines+markers+text',
            line=dict(color='#059669', width=3),
            marker=dict(size=12, color='#34D399',
                        line=dict(width=2, color='white')),
            text=[f"{v:g}" for v in hist_values],
            textposition='top center',
            textfont=dict(size=11, color='#065F46'),
            customdata=hover_dates[:-1],
            hovertemplate=(f'<b>%{{customdata}}</b><br>'
                           f'{field_name}: %{{y:.1f}} {unit}<extra></extra>'),
            name=('قيم سابقة' if lang == 'ar' else 'Past values'),
        ))

    # ---------- Current point (highlighted) ----------
    fig.add_trace(go.Scatter(
        x=[cur_date], y=[cur_value],
        mode='markers+text',
        marker=dict(size=20, color='#DC2626', symbol='star',
                    line=dict(width=2, color='white')),
        text=[f"<b>{cur_value:g}</b>"],
        textposition='top center',
        textfont=dict(size=13, color='#7F1D1D'),
        customdata=[hover_dates[-1]],
        hovertemplate=(f'<b>%{{customdata}} (الآن)</b><br>'
                       f'{field_name}: %{{y:.1f}} {unit}<extra></extra>')
                       if lang == 'ar' else
                      (f'<b>%{{customdata}} (now)</b><br>'
                       f'{field_name}: %{{y:.1f}} {unit}<extra></extra>'),
        name=('القيمة الحالية' if lang == 'ar' else 'Current value'),
    ))

    # Connect last historical point to current with a faint line
    if hist_dates:
        fig.add_trace(go.Scatter(
            x=[hist_dates[-1], cur_date],
            y=[hist_values[-1], cur_value],
            mode='lines',
            line=dict(color='#34D399', width=2, dash='dash'),
            showlegend=False,
            hoverinfo='skip',
        ))

    # ---------- Reference lines ----------
    normal_max = cfg.get('normal_max')
    if normal_max:
        fig.add_hline(y=normal_max, line_dash='dash', line_color='#64748B',
                      line_width=1,
                      annotation_text=('الحد الطبيعي' if lang == 'ar' else 'Normal max'),
                      annotation_position='top left',
                      annotation_font=dict(size=10, color='#64748B'))

    crisis_high = cfg.get('crisis_high')
    if crisis_high:
        fig.add_hline(y=crisis_high, line_dash='dot', line_color='#DC2626',
                      line_width=1.5,
                      annotation_text=('منطقة الخطر' if lang == 'ar' else 'Danger zone'),
                      annotation_position='top right',
                      annotation_font=dict(size=10, color='#DC2626'))

    # ---------- Axis range with padding so labels are visible ----------
    y_min, y_max = min(values), max(values)
    if crisis_high and crisis_high > y_max:
        y_max = crisis_high
    span = max(y_max - y_min, max(y_max, 1) * 0.1)
    y_lo = max(0, y_min - span * 0.25)
    y_hi = y_max + span * 0.40

    # X-axis range: a touch of padding on both sides
    if len(dates) == 1:
        from datetime import timedelta
        x_min = dates[0] - timedelta(hours=1)
        x_max = dates[0] + timedelta(hours=1)
    else:
        from datetime import timedelta
        pad = (dates[-1] - dates[0]).total_seconds() * 0.08
        x_min = dates[0] - timedelta(seconds=pad)
        x_max = dates[-1] + timedelta(seconds=pad)

    # ---------- Subtitle: number of sessions + delta ----------
    if n >= 2:
        delta = cur_value - values[0]
        delta_str = f'{"+" if delta > 0 else ""}{delta:.1f}'
        subtitle = (f"{n} قياسات • التغيّر الكلي: {delta_str} {unit}"
                    if lang == 'ar' else
                    f"{n} measurements • total change: {delta_str} {unit}")
    else:
        subtitle = ('قياس واحد فقط — احفظ مزيداً من الجلسات لرؤية الاتجاه'
                    if lang == 'ar' else
                    'Only one measurement — save more sessions to see a trend')

    fig.update_layout(
        title=dict(
            text=(f"<b>{field_name}</b> — "
                  f"{'تطور عبر الزمن' if lang == 'ar' else 'Trend over time'}<br>"
                  f"<span style='font-size:12px;color:#64748B'>{subtitle}</span>"),
            x=0.5, font=dict(size=15),
        ),
        xaxis=dict(
            title=('التاريخ والوقت' if lang == 'ar' else 'Date / time'),
            type='date',
            tickformat=fmt,
            range=[x_min, x_max],
            gridcolor='#F1F5F9',
            tickfont=dict(size=10),
        ),
        yaxis=dict(
            title=f"{field_name} ({unit})",
            range=[y_lo, y_hi],
            gridcolor='#F1F5F9',
        ),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='white',
        height=370,
        margin=dict(t=70, b=50, l=60, r=30),
        legend=dict(orientation='h', yanchor='bottom', y=1.02,
                    xanchor='right', x=1, font=dict(size=11),
                    bgcolor='rgba(255,255,255,0.85)',
                    bordercolor='#e2e8f0', borderwidth=0.5),
    )
    st.plotly_chart(fig, use_container_width=True)


def _play_tts_summary(alerts: List[Dict[str, Any]], lang: str = 'ar') -> None:
    """Concatenate non-stable alert TTS texts and auto-play them once."""
    texts = [a.get('tts_text') for a in alerts if a.get('tts_text')]
    if not texts:
        return
    full_text = '. '.join(texts)
    try:
        from gtts import gTTS
        tts = gTTS(text=full_text, lang='ar' if lang == 'ar' else 'en')
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        st.audio(buf, format='audio/mp3', autoplay=True)
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════
#  Public API
# ═══════════════════════════════════════════════════════════

def render_instant_alert(username: str, field: str, current_value: float,
                         current_session_id: str, lang: str = 'ar') -> None:
    """
    Live alert shown right after the patient answers a question.
    Call this from the input handler in app.py.
    """
    if not username or field not in FIELD_THRESHOLDS:
        return
    tracker = HistoryTracker()
    comp = tracker.compare_with_previous(
        username, field, current_value, exclude_session_id=current_session_id
    )
    if not comp:
        return  # first visit — nothing to compare
    alert = tracker.generate_alert_text(comp, lang)
    if not alert or alert.get('level') == 'stable':
        return
    alert['comparison'] = comp
    _render_alert_card(alert, lang)

    # Instant voice cue
    tts_text = alert.get('tts_text')
    if tts_text:
        try:
            from gtts import gTTS
            tts = gTTS(text=tts_text, lang='ar' if lang == 'ar' else 'en')
            buf = io.BytesIO()
            tts.write_to_fp(buf)
            buf.seek(0)
            st.audio(buf, format='audio/mp3', autoplay=True)
        except Exception:
            pass


def render_patient_report(username: str, current_facts: Dict[str, Any],
                          current_session_id: str, lang: str = 'ar') -> None:
    """
    Full end-of-session longitudinal report for a patient.
    Shows trend alerts + line charts + audio summary.
    """
    tracker = HistoryTracker()
    alerts = tracker.analyze_session(
        username, current_facts,
        exclude_session_id=current_session_id, lang=lang
    )

    st.markdown("---")
    header = "📊 تقرير تطور حالتك الصحية" if lang == 'ar' \
             else "📊 Your Health Trend Report"
    st.markdown(f"## {header}")

    if not alerts:
        no_history = ("هذه جلستك الأولى — لا يوجد تاريخ سابق للمقارنة. "
                      "سيتم حفظ نتائجك لمقارنتها في الزيارات القادمة."
                      if lang == 'ar'
                      else "This is your first session — no past data to compare with. "
                           "Your results will be saved for future visits.")
        st.info(no_history)
        return

    # Alert cards first
    for alert in alerts:
        _render_alert_card(alert, lang)

    # Audio summary
    _play_tts_summary(alerts, lang)

    # Historical charts
    st.markdown("---")
    chart_title = "📈 تطور القيم عبر الزمن" if lang == 'ar' \
                  else "📈 Values Over Time"
    st.markdown(f"### {chart_title}")

    from datetime import datetime
    for alert in alerts:
        field = alert['comparison']['field']
        history = tracker.get_field_history(
            username, field, exclude_session_id=current_session_id
        )
        # Append the current point with a real datetime so Plotly can place
        # it correctly on the date axis (string 'Now' previously caused
        # weird microsecond-level tick marks).
        current_val = alert['comparison']['current']
        history_with_current = history + [(datetime.now().isoformat(timespec='seconds'),
                                           current_val)]
        _render_trend_chart(history_with_current, field, lang)
