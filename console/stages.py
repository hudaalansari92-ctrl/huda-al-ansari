"""Pretty-print the same 7 demo stages from the Streamlit step-by-step
walkthrough into the console. Pauses on Enter between stages."""
from typing import Dict, List

from config.translations import get_field_names_dict
from .colors import (
    cyan, green, yellow, red, blue, magenta, bold,
    header, subheader, risk_color,
)


_STR = {
    'ar': {
        'press_enter':       'اضغط Enter للمرحلة التالية...',
        'press_enter_start': 'اضغط Enter لبدء العرض المرحلي...',
        'what_happens':      'ما يحدث الآن',
        'demo_finished':     'انتهى العرض — تم تنفيذ كل المراحل الـ 7.',

        's1_title':   'المرحلة 1 من 7 — البيانات الخام للمريض',
        's1_explain': 'هذه هي الـ 11 معلومة التي جمعناها. كل القرارات التالية تنبني عليها.',
        's1_hdr_field':  'الحقل',
        's1_hdr_value':  'القيمة',
        's1_hdr_source': 'المصدر',

        's2_title':   'المرحلة 2 من 7 — هندسة الخصائص',
        's2_explain': 'حوّلنا 11 معلومة بسيطة إلى 58 مؤشّر طبي متقدّم.',
        's2_total':   'إجمالي المؤشّرات المُولّدة',
        's2_examples':'أمثلة على المؤشّرات المتقدّمة',

        's3_title':   'المرحلة 3 من 7 — القواعد الطبية',
        's3_explain': '48 قاعدة طبية معتمدة من جمعية القلب الأمريكية. هذه القواعد التي تنطبق على المريض:',
        's3_triggered':'القواعد المُفعّلة',
        's3_total':   'إجمالي القواعد المتاحة',

        's4_title':   'المرحلة 4 من 7 — الشبكة العصبية ERPM',
        's4_explain': 'نموذج تعلّم آلي بـ 79,809 معامل أعطى احتمالية إصابة المريض.',
        's4_pred':    'التنبؤ',
        's4_prob':    'الاحتمالية',

        's5_title':   'المرحلة 5 من 7 — دمج القرارات',
        's5_explain': 'دمجنا حكمة الأطباء (القواعد الطبية) مع قوة الحاسوب (الشبكة العصبية).',
        's5_domain':  'رأي القواعد الطبية',
        's5_ml':      'رأي الشبكة العصبية',
        's5_fused':   'القرار المُدمج',
        's5_rule':    'القاعدة المُطبَّقة',
        's5_conf':    'ثقة القرار',

        's6_title':   'المرحلة 6 من 7 — تصنيف مستوى الخطر',
        's6_explain': 'صنّفنا المريض وفق معايير ACC/AHA 2019: منخفض / حدّي / متوسط / عالي.',
        's6_final':   'تصنيف المريض',

        's7_title':   'المرحلة 7 من 7 — القرار النهائي والتوصيات',
        's7_explain': 'ملخّص كل ما سبق مع التوصيات الطبية.',
        's7_final':   'القرار النهائي',
        's7_recs':    'التوصيات الطبية',
        's7_none_recs':'لا توجد توصيات مخصّصة لهذه الحالة.',
    },
    'en': {
        'press_enter':       'Press Enter for the next stage...',
        'press_enter_start': 'Press Enter to start the walkthrough...',
        'what_happens':      'What happens now',
        'demo_finished':     'Demo complete — all 7 stages executed.',

        's1_title':   'Stage 1 of 7 — Raw Patient Data',
        's1_explain': 'The 11 inputs we collected. Everything that follows is built on these.',
        's1_hdr_field':  'Field',
        's1_hdr_value':  'Value',
        's1_hdr_source': 'Source',

        's2_title':   'Stage 2 of 7 — Feature Engineering',
        's2_explain': 'We turned 11 simple inputs into 58 advanced medical indicators.',
        's2_total':   'Total engineered indicators',
        's2_examples':'Examples of advanced indicators',

        's3_title':   'Stage 3 of 7 — Medical Rules',
        's3_explain': '48 rules grounded in ACC/AHA guidelines. These fired for the patient:',
        's3_triggered':'Rules triggered',
        's3_total':   'Total rules available',

        's4_title':   'Stage 4 of 7 — ERPM Neural Network',
        's4_explain': 'ML model with 79,809 parameters returns the disease probability.',
        's4_pred':    'Prediction',
        's4_prob':    'Probability',

        's5_title':   'Stage 5 of 7 — Decision Fusion',
        's5_explain': 'We combine clinical wisdom (rules) with computational power (ERPM).',
        's5_domain':  'Medical Rules verdict',
        's5_ml':      'Neural Network verdict',
        's5_fused':   'Fused decision',
        's5_rule':    'Rule applied',
        's5_conf':    'Decision confidence',

        's6_title':   'Stage 6 of 7 — Risk Stratification',
        's6_explain': 'Classified per ACC/AHA 2019 bands: Low / Borderline / Intermediate / High.',
        's6_final':   'Patient classification',

        's7_title':   'Stage 7 of 7 — Final Decision and Recommendations',
        's7_explain': 'Summary of everything above with the medical recommendations.',
        's7_final':   'Final decision',
        's7_recs':    'Medical recommendations',
        's7_none_recs':'No specific recommendations for this case.',
    },
}


def _print_table(rows: List[List[str]], headers: List[str], lang: str = 'ar') -> None:
    """Tiny pure-ASCII table — works in any terminal, no extra deps."""
    cols = len(headers)
    widths = [len(str(h)) for h in headers]
    for row in rows:
        for i in range(cols):
            cell = '' if i >= len(row) else str(row[i])
            widths[i] = max(widths[i], len(cell))
    # Cap absurdly wide columns so the table doesn't blow past 110 chars
    widths = [min(w, 60) for w in widths]

    def fmt(row):
        cells = []
        for i in range(cols):
            cell = '' if i >= len(row) else str(row[i])
            if len(cell) > widths[i]:
                cell = cell[: widths[i] - 1] + '…'
            cells.append(cell.ljust(widths[i]))
        return '│ ' + ' │ '.join(cells) + ' │'

    sep = '┼'.join('─' * (w + 2) for w in widths)
    print('┌' + sep.replace('┼', '┬') + '┐')
    print(fmt(headers))
    print('├' + sep + '┤')
    for row in rows:
        print(fmt(row))
    print('└' + sep.replace('┼', '┴') + '┘')


def _pause(lang: str, start: bool = False) -> None:
    s = _STR[lang]
    msg = s['press_enter_start'] if start else s['press_enter']
    try:
        input(cyan(f'\n  ▸ {msg}'))
    except EOFError:
        pass


def _explain(title: str, body: str, lang: str) -> None:
    print(header(title))
    print(yellow(f'  {_STR[lang]["what_happens"]}: ') + body)
    print()


def render_stages(final_assessment: Dict, facts: Dict, field_meta: Dict, lang: str) -> None:
    s = _STR[lang]
    _pause(lang, start=True)

    domain  = final_assessment.get('domain_rules', {}) or {}
    adv     = final_assessment.get('advanced_features', {}) or {}
    ml      = final_assessment.get('ml_prediction', {}) or {}
    final_d = final_assessment.get('final_decision', {}) or {}
    field_names = get_field_names_dict(lang)

    # ── Stage 1 ─────────────────────────────────────────────────────────
    _explain(s['s1_title'], s['s1_explain'], lang)
    rows = []
    for fname, val in facts.items():
        meta = field_meta.get(fname) or {}
        if meta.get('source') == 'skipped':
            src = yellow('Skipped' if lang == 'en' else 'مُتخطى')
        elif meta.get('source') == 'user':
            src = green('User' if lang == 'en' else 'المريض')
        else:
            src = '—'
        rows.append([field_names.get(fname, fname), str(val), src])
    _print_table(rows, [s['s1_hdr_field'], s['s1_hdr_value'], s['s1_hdr_source']], lang)
    _pause(lang)

    # ── Stage 2 ─────────────────────────────────────────────────────────
    _explain(s['s2_title'], s['s2_explain'], lang)
    print(f'  {bold(s["s2_total"])}: {green(str(adv.get("total_features", 58)))}')
    summary = adv.get('summary', {}) or {}
    if summary:
        print(f'\n  {bold(s["s2_examples"])}:')
        for k, v in summary.items():
            print(f'    • {magenta(k):<35} → {cyan(str(v))}')
    _pause(lang)

    # ── Stage 3 ─────────────────────────────────────────────────────────
    _explain(s['s3_title'], s['s3_explain'], lang)
    triggered = (final_d.get('metadata', {}) or {}).get('triggered_rules', []) or []
    if not triggered:
        triggered = (domain.get('insights', {}) or {}).get('triggered_rules', []) or []
    print(f'  {bold(s["s3_triggered"])}: {green(str(len(triggered)))}  '
          f'/ {bold(s["s3_total"])}: 48')
    print()
    if triggered:
        rows = []
        for r in triggered[:10]:
            rows.append([
                str(r.get('rule_id', '—')),
                str(r.get('condition', ''))[:60],
                f'{float(r.get("confidence", 0)) * 100:.0f}%',
            ])
        _print_table(rows, ['Rule ID', 'Condition', 'Confidence'], lang)
    _pause(lang)

    # ── Stage 4 ─────────────────────────────────────────────────────────
    _explain(s['s4_title'], s['s4_explain'], lang)
    prediction = ml.get('prediction', 'Unknown')
    probability = float(ml.get('probability', 0) or 0)
    pred_colored = red(prediction) if prediction == 'Positive' else green(prediction)
    print(f'  {bold(s["s4_pred"])}: {pred_colored}')
    print(f'  {bold(s["s4_prob"])}: {magenta(f"{probability*100:.1f}%")}')
    print(f'  {cyan("ERPM • 79,809 parameters • 21 layers")}')
    _pause(lang)

    # ── Stage 5 ─────────────────────────────────────────────────────────
    _explain(s['s5_title'], s['s5_explain'], lang)
    domain_risk = ((domain.get('insights', {}) or {}).get('risk_level') or 'UNKNOWN').upper()
    ml_risk = ml.get('risk_level', 'UNKNOWN')
    fused = final_d.get('final_risk_level', 'UNKNOWN')
    print(f'  {bold(s["s5_domain"])} : {risk_color(domain_risk)}')
    print(f'  {bold(s["s5_ml"])}     : {risk_color(ml_risk)}')
    print(f'  {bold(s["s5_fused"])}  : {risk_color(fused)}')
    print()
    reasoning = (final_d.get('reasoning_ar') if lang == 'ar'
                 else final_d.get('reasoning_en')) or '—'
    conf = float(final_d.get('confidence', 0) or 0)
    print(f'  {bold(s["s5_rule"])}: {reasoning}')
    print(f'  {bold(s["s5_conf"])}: {magenta(f"{conf*100:.0f}%")}')
    _pause(lang)

    # ── Stage 6 ─────────────────────────────────────────────────────────
    _explain(s['s6_title'], s['s6_explain'], lang)
    final_risk = final_d.get('final_risk_level', 'UNKNOWN')
    final_display = (final_d.get('final_risk_level_ar', final_risk)
                     if lang == 'ar' else final_risk)
    print(f'  {bold(s["s6_final"])}: {risk_color(final_display)}')
    print(f'  {cyan("< 5% Low • 5-7.5% Borderline • 7.5-20% Intermediate • > 20% High")}')
    _pause(lang)

    # ── Stage 7 ─────────────────────────────────────────────────────────
    _explain(s['s7_title'], s['s7_explain'], lang)
    print(f'  {bold(s["s7_final"])}: {risk_color(final_display)}')
    rec_key = 'recommendations_ar' if lang == 'ar' else 'recommendations'
    recs = ((domain.get('insights', {}) or {}).get(rec_key)
            or (domain.get('insights', {}) or {}).get('recommendations_ar')
            or [])
    print()
    if recs:
        print(f'  {bold(s["s7_recs"])}:')
        for r in recs[:5]:
            print(f'    • {r}')
    else:
        print(f'  {yellow(s["s7_none_recs"])}')
    print()
    print(green(bold('  ' + s['demo_finished'])))
