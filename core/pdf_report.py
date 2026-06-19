"""
PDF report generator with full Arabic (RTL + shaping) support.

The first time it runs it downloads the free open-source Amiri font
(SIL OFL licence) into assets/fonts/ so the produced PDF embeds a
font that genuinely renders Arabic letters correctly.

Public entry point:
    generate_pdf_report(assessment: Dict, lang: str = 'ar') -> bytes
"""
import io
import os
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# ---- optional Arabic shaping dependencies --------------------------------
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    _HAS_ARABIC = True
except Exception:                                            # pragma: no cover
    _HAS_ARABIC = False

# ---- ReportLab core ------------------------------------------------------
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)


# =========================================================================
#  Font handling
# =========================================================================

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_FONT_DIR = _PROJECT_ROOT / 'assets' / 'fonts'
_FONT_FILES = {
    'Amiri-Regular.ttf': 'https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf',
    'Amiri-Bold.ttf':    'https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Bold.ttf',
}
_FONT_REGULAR = 'AmiriArabic'
_FONT_BOLD = 'AmiriArabicBold'
_FONT_REGISTERED = False


def _ensure_font_files() -> bool:
    """Download the Amiri TTF files on first use. Returns True if available."""
    _FONT_DIR.mkdir(parents=True, exist_ok=True)
    ok = True
    for name, url in _FONT_FILES.items():
        path = _FONT_DIR / name
        if path.exists() and path.stat().st_size > 1000:
            continue
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as resp, open(path, 'wb') as f:
                f.write(resp.read())
        except Exception:
            ok = False
    return ok


def _register_arabic_font() -> bool:
    """Register the Amiri font family with ReportLab (idempotent)."""
    global _FONT_REGISTERED
    if _FONT_REGISTERED:
        return True
    if not _ensure_font_files():
        return False
    try:
        pdfmetrics.registerFont(
            TTFont(_FONT_REGULAR, str(_FONT_DIR / 'Amiri-Regular.ttf'))
        )
        pdfmetrics.registerFont(
            TTFont(_FONT_BOLD, str(_FONT_DIR / 'Amiri-Bold.ttf'))
        )
        _FONT_REGISTERED = True
        return True
    except Exception:
        return False


# =========================================================================
#  Arabic shaping helper
# =========================================================================

def _ar(text: Any, lang: str = 'ar') -> str:
    """Reshape Arabic text and apply BIDI so glyphs render right-to-left."""
    if text is None:
        return ''
    s = str(text)
    if lang != 'ar' or not _HAS_ARABIC or not s.strip():
        return s
    try:
        return get_display(arabic_reshaper.reshape(s))
    except Exception:
        return s


# =========================================================================
#  Style builder
# =========================================================================

def _build_styles(lang: str, font_ok: bool) -> Dict[str, ParagraphStyle]:
    """Create paragraph styles tuned for the chosen language."""
    align_body = 2 if lang == 'ar' else 0          # 0=left  1=center  2=right
    base_font = _FONT_REGULAR if font_ok else 'Helvetica'
    bold_font = _FONT_BOLD if font_ok else 'Helvetica-Bold'

    return {
        'title': ParagraphStyle(
            'Title', fontName=bold_font, fontSize=20, leading=26,
            alignment=1, textColor=colors.HexColor('#0F766E'),
            spaceAfter=4,
        ),
        'subtitle': ParagraphStyle(
            'Subtitle', fontName=base_font, fontSize=11, leading=14,
            alignment=1, textColor=colors.HexColor('#64748B'),
            spaceAfter=12,
        ),
        'h2': ParagraphStyle(
            'H2', fontName=bold_font, fontSize=14, leading=18,
            alignment=align_body, textColor=colors.HexColor('#059669'),
            spaceBefore=10, spaceAfter=6,
        ),
        'body': ParagraphStyle(
            'Body', fontName=base_font, fontSize=11, leading=16,
            alignment=align_body, textColor=colors.HexColor('#1E293B'),
            spaceAfter=4,
        ),
        'kv_label': ParagraphStyle(
            'KVLabel', fontName=bold_font, fontSize=10, leading=14,
            alignment=align_body, textColor=colors.HexColor('#475569'),
        ),
        'kv_value': ParagraphStyle(
            'KVValue', fontName=base_font, fontSize=11, leading=14,
            alignment=align_body, textColor=colors.HexColor('#0F172A'),
        ),
        'badge_high': ParagraphStyle(
            'BadgeHigh', fontName=bold_font, fontSize=13, leading=18,
            alignment=1, textColor=colors.white,
            backColor=colors.HexColor('#DC2626'),
        ),
        'badge_moderate': ParagraphStyle(
            'BadgeMod', fontName=bold_font, fontSize=13, leading=18,
            alignment=1, textColor=colors.white,
            backColor=colors.HexColor('#F59E0B'),
        ),
        'badge_low': ParagraphStyle(
            'BadgeLow', fontName=bold_font, fontSize=13, leading=18,
            alignment=1, textColor=colors.white,
            backColor=colors.HexColor('#059669'),
        ),
        'small': ParagraphStyle(
            'Small', fontName=base_font, fontSize=8, leading=11,
            alignment=1, textColor=colors.HexColor('#94A3B8'),
        ),
    }


# =========================================================================
#  Helpers to read assessment data safely
# =========================================================================

def _risk_badge_style(styles: Dict, level: str) -> ParagraphStyle:
    mapping = {
        'CRITICAL': 'badge_high', 'HIGH': 'badge_high',
        'MODERATE': 'badge_moderate', 'MEDIUM': 'badge_moderate',
        'LOW': 'badge_low',
    }
    return styles[mapping.get(str(level).upper(), 'badge_moderate')]


def _T(key: str, lang: str) -> str:
    """Tiny translation table for the labels used in this report."""
    table = {
        'report_title':       ('تقرير التقييم النهائي', 'Final Assessment Report'),
        'subtitle_system':    ('نظام شات بوت للرعاية الصحية مبني على التقنيات الذكية',
                                'Healthcare Chatbot System Based on Intelligent Techniques'),
        'patient':            ('المريض', 'Patient'),
        'date':               ('تاريخ التقرير', 'Report date'),
        'session':            ('رقم الجلسة', 'Session ID'),
        'risk_level':         ('مستوى الخطر النهائي', 'Final risk level'),
        'confidence':         ('درجة الثقة', 'Confidence'),
        'reasoning':          ('التفسير', 'Reasoning'),
        'sources':            ('مصادر القرار', 'Decision sources'),
        'medical_rules':      ('القواعد الطبية', 'Medical rules'),
        'ml_model':           ('نموذج التعلم الآلي', 'ML model'),
        'rules_applied':      ('القواعد المُطبَّقة', 'Triggered rules'),
        'framingham':         ('نقاط Framingham', 'Framingham score'),
        'probability':        ('الاحتمالية', 'Probability'),
        'prediction':         ('التنبؤ', 'Prediction'),
        'source':             ('المصدر', 'Source'),
        'recommendations':    ('التوصيات الطبية', 'Medical recommendations'),
        'facts_collected':    ('الحقائق المُجمَّعة', 'Collected facts'),
        'no_data':            ('لا توجد بيانات', 'No data'),
        'footer':             ('هذا التقرير ليس بديلاً عن الاستشارة الطبية.',
                                'This report is not a substitute for professional medical advice.'),
    }
    pair = table.get(key, (key, key))
    return pair[0] if lang == 'ar' else pair[1]


# =========================================================================
#  Public entry point
# =========================================================================

def generate_pdf_report(
    assessment: Dict[str, Any],
    lang: str = 'ar',
    patient_name: str = '',
    session_id: str = '',
    facts: Dict[str, Any] = None,
) -> bytes:
    """
    Build the final assessment report as a PDF (bytes) ready for download.

    Parameters
    ----------
    assessment : the final_assessment dict from the chatbot
                 (contains 'final_decision', 'domain_rules', etc.).
    lang       : 'ar' or 'en'.
    patient_name : optional name to print in the header.
    session_id   : optional session identifier to print.
    facts        : optional dict of collected patient facts.
    """
    font_ok = _register_arabic_font()
    styles = _build_styles(lang, font_ok)
    facts = facts or {}

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=1.5 * cm, rightMargin=1.5 * cm,
        topMargin=1.5 * cm, bottomMargin=1.5 * cm,
        title=_T('report_title', lang),
    )
    story: List = []

    # ---------- Header ----------
    story.append(Paragraph(_ar(_T('report_title', lang), lang), styles['title']))
    story.append(Paragraph(_ar(_T('subtitle_system', lang), lang), styles['subtitle']))

    # ---------- Meta info (Patient / Date / Session) ----------
    meta_rows = [
        [_ar(_T('patient', lang), lang),
         _ar(patient_name or '-', lang)],
        [_ar(_T('date', lang), lang),
         datetime.now().strftime('%Y-%m-%d %H:%M')],
        [_ar(_T('session', lang), lang),
         session_id or '-'],
    ]
    meta_table = Table(meta_rows, colWidths=[4.5 * cm, 12 * cm])
    meta_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), _FONT_REGULAR if font_ok else 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#64748B')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#0F172A')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#E2E8F0')),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT' if lang == 'ar' else 'LEFT'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.5 * cm))

    # ---------- Final risk + confidence ----------
    final_dec = assessment.get('final_decision', {}) or {}
    risk_level = (final_dec.get('final_risk_level')
                  or final_dec.get('final_risk_level_ar')
                  or _T('no_data', lang))
    risk_level_str = str(risk_level).upper()
    confidence = final_dec.get('confidence', 0.0)
    try:
        confidence_pct = f"{float(confidence) * 100:.1f}%"
    except (TypeError, ValueError):
        confidence_pct = str(confidence)

    story.append(Paragraph(_ar(_T('risk_level', lang), lang), styles['h2']))
    risk_badge = Paragraph(_ar(risk_level_str, lang),
                           _risk_badge_style(styles, risk_level_str))
    conf_par = Paragraph(
        _ar(f"{_T('confidence', lang)}: {confidence_pct}", lang),
        styles['body']
    )
    risk_table = Table([[risk_badge, conf_par]],
                       colWidths=[4 * cm, 12.5 * cm])
    risk_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(risk_table)
    story.append(Spacer(1, 0.3 * cm))

    # ---------- Reasoning ----------
    reasoning_key = 'reasoning_ar' if lang == 'ar' else 'reasoning_en'
    reasoning_text = (final_dec.get(reasoning_key)
                      or final_dec.get('reasoning_ar')
                      or final_dec.get('reasoning_en')
                      or '')
    if reasoning_text:
        story.append(Paragraph(_ar(_T('reasoning', lang), lang), styles['h2']))
        story.append(Paragraph(_ar(reasoning_text, lang), styles['body']))

    # ---------- Decision sources ----------
    sources = final_dec.get('sources', {}) or {}
    if sources:
        story.append(Paragraph(_ar(_T('sources', lang), lang), styles['h2']))

        # Medical Rules sub-block
        dom = sources.get('domain_rules', {}) or {}
        dom_rows = [
            [_ar(_T('risk_level', lang), lang),
             _ar(str(dom.get('risk_level', '-')).upper(), lang)],
            [_ar(_T('rules_applied', lang), lang),
             f"{dom.get('triggered_rules', 0)} / 48"],
            [_ar(_T('framingham', lang), lang),
             f"{dom.get('framingham_score', 0)} / 7"],
        ]
        story.append(Paragraph(
            _ar(_T('medical_rules', lang), lang),
            ParagraphStyle('rules_h',
                           parent=styles['body'],
                           fontName=_FONT_BOLD if font_ok else 'Helvetica-Bold',
                           textColor=colors.HexColor('#1D4ED8'),
                           fontSize=12),
        ))
        story.append(_kv_table(dom_rows, font_ok, lang))
        story.append(Spacer(1, 0.2 * cm))

        # ML Model sub-block
        ml = sources.get('ml_model', {}) or {}
        ml_prob = ml.get('probability', 0.0)
        try:
            ml_prob_str = f"{float(ml_prob) * 100:.1f}%"
        except (TypeError, ValueError):
            ml_prob_str = str(ml_prob)
        ml_rows = [
            [_ar(_T('probability', lang), lang), ml_prob_str],
            [_ar(_T('prediction', lang), lang),
             _ar(str(ml.get('prediction', '-')), lang)],
            [_ar(_T('source', lang), lang),
             _ar(str(ml.get('source', '-')), lang)],
        ]
        story.append(Paragraph(
            _ar(_T('ml_model', lang), lang),
            ParagraphStyle('ml_h',
                           parent=styles['body'],
                           fontName=_FONT_BOLD if font_ok else 'Helvetica-Bold',
                           textColor=colors.HexColor('#7C3AED'),
                           fontSize=12),
        ))
        story.append(_kv_table(ml_rows, font_ok, lang))

    # ---------- Recommendations ----------
    recs = final_dec.get('recommendations', []) or []
    if recs:
        story.append(Spacer(1, 0.4 * cm))
        story.append(Paragraph(_ar(_T('recommendations', lang), lang), styles['h2']))
        for i, rec in enumerate(recs[:10], 1):
            bullet = '•' if lang == 'ar' else f'{i}.'
            story.append(Paragraph(_ar(f"{bullet} {rec}", lang), styles['body']))

    # ---------- Collected facts (compact table) ----------
    if facts:
        story.append(Spacer(1, 0.4 * cm))
        story.append(Paragraph(_ar(_T('facts_collected', lang), lang), styles['h2']))
        f_rows = []
        for k, v in list(facts.items())[:20]:
            f_rows.append([_ar(str(k), lang), _ar(str(v), lang)])
        if f_rows:
            story.append(_kv_table(f_rows, font_ok, lang))

    # ---------- Footer ----------
    story.append(Spacer(1, 0.6 * cm))
    story.append(Paragraph(_ar(_T('footer', lang), lang), styles['small']))

    doc.build(story)
    return buf.getvalue()


def _kv_table(rows: List[List[str]], font_ok: bool, lang: str) -> Table:
    """Helper to render a clean key/value table."""
    tbl = Table(rows, colWidths=[5 * cm, 11.5 * cm])
    tbl.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1),
         _FONT_REGULAR if font_ok else 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#64748B')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#0F172A')),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F1F5F9')),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#E2E8F0')),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT' if lang == 'ar' else 'LEFT'),
    ]))
    return tbl
