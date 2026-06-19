import plotly.graph_objects as go
from typing import Dict, List, Optional


# ═══════════════════════════════════════════════════════════════
# ألوان مستويات الخطر
# ═══════════════════════════════════════════════════════════════

RISK_COLORS = {
    'CRITICAL':      '#dc2626',
    'HIGH':          '#f97316',
    'MODERATE-HIGH': '#eab308',
    'MODERATE':      '#22c55e',
    'LOW-MODERATE':  '#6ee7b7',
    'LOW':           '#3b82f6',
}

RISK_BG = {
    'CRITICAL':      'rgba(220,38,38,0.12)',
    'HIGH':          'rgba(249,115,22,0.12)',
    'MODERATE-HIGH': 'rgba(234,179,8,0.12)',
    'MODERATE':      'rgba(34,197,94,0.12)',
    'LOW-MODERATE':  'rgba(110,231,183,0.12)',
    'LOW':           'rgba(59,130,246,0.12)',
}

INACTIVE_COLOR = '#cbd5e1'
ACTIVE_EDGE_COLOR = '#7c3aed'
NODE_BORDER = '#e2e8f0'


# ═══════════════════════════════════════════════════════════════
# Helper: استخراج بيانات المريض من final_decision
# ═══════════════════════════════════════════════════════════════

def _extract_patient(fd: Optional[Dict]) -> Dict:
    """استخراج قيم المريض الثلاث + القاعدة النشطة."""
    if not fd:
        return {'ml': None, 'domain': None, 'fram': None, 'rule': None,
                'risk': None, 'conf': None}
    sources = fd.get('sources', {})
    meta = fd.get('metadata', {})
    ml_src = sources.get('ml_model', {})
    dom_src = sources.get('domain_rules', {})
    return {
        'ml':     ml_src.get('probability'),
        'domain': dom_src.get('risk_level'),
        'fram':   dom_src.get('framingham_score'),
        'rule':   meta.get('decision_rule'),
        'risk':   fd.get('final_risk_level'),
        'conf':   fd.get('confidence'),
    }


# ═══════════════════════════════════════════════════════════════
# 1. شجرة القرار — يدوية مبنية على الـ 10 قواعد
# ═══════════════════════════════════════════════════════════════

# كل عقدة: (id, label_condition, depth, x, children_yes, children_no, rule_id, leaf_risk)
# rule_id is set only for leaf nodes; leaf_risk is the final classification

_TREE = [
    # depth 0
    {'id': 'n0',  'cond': 'DL >= 95%?',           'depth': 0, 'x': 0.50,
     'yes': 'L1', 'no': 'n1', 'leaf': None},

    # depth 1
    {'id': 'L1',  'cond': 'CRITICAL',             'depth': 1, 'x': 0.15,
     'yes': None, 'no': None, 'leaf': 'CRITICAL', 'rule': 'Rule 1'},
    {'id': 'n1',  'cond': 'DL >= 90%?',           'depth': 1, 'x': 0.70,
     'yes': 'n2', 'no': 'n3', 'leaf': None},

    # depth 2
    {'id': 'n2',  'cond': 'Domain = HIGH?',       'depth': 2, 'x': 0.50,
     'yes': 'L2', 'no': 'n4', 'leaf': None},
    {'id': 'n3',  'cond': 'DL >= 70%?',           'depth': 2, 'x': 0.85,
     'yes': 'n5', 'no': 'n8', 'leaf': None},

    # depth 3 — from n2
    {'id': 'L2',  'cond': 'CRITICAL',             'depth': 3, 'x': 0.38,
     'yes': None, 'no': None, 'leaf': 'CRITICAL', 'rule': 'Rule 2'},
    {'id': 'n4',  'cond': 'Domain = CRITICAL?',   'depth': 3, 'x': 0.55,
     'yes': 'L5', 'no': 'L_mod', 'leaf': None},

    # depth 3 — from n3
    {'id': 'n5',  'cond': 'Domain = HIGH?',       'depth': 3, 'x': 0.75,
     'yes': 'L3', 'no': 'n6', 'leaf': None},
    {'id': 'n8',  'cond': 'DL >= 50%?',           'depth': 3, 'x': 0.95,
     'yes': 'n9', 'no': 'n10', 'leaf': None},

    # depth 4 — from n4
    {'id': 'L5',  'cond': 'HIGH',                 'depth': 4, 'x': 0.48,
     'yes': None, 'no': None, 'leaf': 'HIGH',     'rule': 'Rule 5'},
    {'id': 'L_mod', 'cond': 'MODERATE-HIGH',      'depth': 4, 'x': 0.60,
     'yes': None, 'no': None, 'leaf': 'MODERATE-HIGH', 'rule': 'Rule 7'},

    # depth 4 — from n5
    {'id': 'L3',  'cond': 'HIGH',                 'depth': 4, 'x': 0.68,
     'yes': None, 'no': None, 'leaf': 'HIGH',     'rule': 'Rule 3'},
    {'id': 'n6',  'cond': 'Framingham >= 4?',     'depth': 4, 'x': 0.82,
     'yes': 'L4', 'no': 'L7', 'leaf': None},

    # depth 4 — from n8
    {'id': 'n9',  'cond': 'Domain = HIGH?',       'depth': 4, 'x': 0.90,
     'yes': 'L6', 'no': 'L8', 'leaf': None},
    {'id': 'n10', 'cond': 'DL >= 40%?',           'depth': 4, 'x': 1.00,
     'yes': 'L8b', 'no': 'n11', 'leaf': None},

    # depth 5 — from n6
    {'id': 'L4',  'cond': 'HIGH',                 'depth': 5, 'x': 0.77,
     'yes': None, 'no': None, 'leaf': 'HIGH',     'rule': 'Rule 4'},
    {'id': 'L7',  'cond': 'MODERATE-HIGH',        'depth': 5, 'x': 0.86,
     'yes': None, 'no': None, 'leaf': 'MODERATE-HIGH', 'rule': 'Rule 7'},

    # depth 5 — from n9
    {'id': 'L6',  'cond': 'MODERATE-HIGH',        'depth': 5, 'x': 0.87,
     'yes': None, 'no': None, 'leaf': 'MODERATE-HIGH', 'rule': 'Rule 6'},
    {'id': 'L8',  'cond': 'MODERATE',             'depth': 5, 'x': 0.93,
     'yes': None, 'no': None, 'leaf': 'MODERATE', 'rule': 'Rule 8'},

    # depth 5 — from n10
    {'id': 'L8b', 'cond': 'MODERATE',             'depth': 5, 'x': 0.97,
     'yes': None, 'no': None, 'leaf': 'MODERATE', 'rule': 'Rule 8'},
    {'id': 'n11', 'cond': 'Domain = HIGH?',       'depth': 5, 'x': 1.05,
     'yes': 'L9', 'no': 'n12', 'leaf': None},

    # depth 6 — from n11
    {'id': 'L9',  'cond': 'LOW-MODERATE',         'depth': 6, 'x': 1.01,
     'yes': None, 'no': None, 'leaf': 'LOW-MODERATE', 'rule': 'Rule 9'},
    {'id': 'n12', 'cond': 'DL < 30%?',            'depth': 6, 'x': 1.10,
     'yes': 'L10', 'no': 'L_def', 'leaf': None},

    # depth 7
    {'id': 'L10', 'cond': 'LOW',                  'depth': 7, 'x': 1.06,
     'yes': None, 'no': None, 'leaf': 'LOW',      'rule': 'Rule 10'},
    {'id': 'L_def', 'cond': 'MODERATE',           'depth': 7, 'x': 1.14,
     'yes': None, 'no': None, 'leaf': 'MODERATE', 'rule': 'Default'},
]


def _build_lookup():
    return {n['id']: n for n in _TREE}


def _trace_active_path(patient: Dict) -> set:
    """Determine which node IDs fall on the active decision path."""
    ml = patient.get('ml')
    domain = (patient.get('domain') or '').upper()
    fram = patient.get('fram') or 0
    active_rule = patient.get('rule') or ''

    if ml is None:
        return set()

    path = set()
    lookup = _build_lookup()

    def walk(nid):
        node = lookup.get(nid)
        if not node:
            return False
        path.add(nid)
        if node['leaf']:
            rule = node.get('rule', '')
            if rule and rule.lower().replace(' ', '') in active_rule.lower().replace(' ', ''):
                return True
            if patient.get('risk') and node['leaf'] == patient['risk']:
                return True
            path.discard(nid)
            return False
        # Evaluate condition to decide branch
        go_yes = _eval_cond(node['cond'], ml, domain, fram)
        child = node['yes'] if go_yes else node['no']
        if child and walk(child):
            return True
        # Try other branch as fallback
        other = node['no'] if go_yes else node['yes']
        if other and walk(other):
            return True
        path.discard(nid)
        return False

    walk('n0')
    return path


def _eval_cond(cond: str, ml: float, domain: str, fram: int) -> bool:
    c = cond.strip()
    if c == 'DL >= 95%?':      return ml >= 0.95
    if c == 'DL >= 90%?':      return ml >= 0.90
    if c == 'DL >= 70%?':      return ml >= 0.70
    if c == 'DL >= 50%?':      return ml >= 0.50
    if c == 'DL >= 40%?':      return ml >= 0.40
    if c == 'DL < 30%?':       return ml < 0.30
    if c == 'Domain = HIGH?':  return domain in ('HIGH',)
    if c == 'Domain = CRITICAL?': return domain in ('CRITICAL',)
    if c == 'Framingham >= 4?': return fram >= 4
    return False


def create_decision_tree_diagram(final_decision: Dict = None) -> go.Figure:
    """شجرة قرار تفاعلية مبنية على الـ 10 قواعد مع تمييز مسار المريض."""
    patient = _extract_patient(final_decision)
    active_ids = _trace_active_path(patient)
    lookup = _build_lookup()

    fig = go.Figure()

    y_gap = 0.12
    max_depth = max(n['depth'] for n in _TREE)

    def y_pos(depth):
        return 1.0 - depth * y_gap

    # ——— Draw edges ———
    for node in _TREE:
        nid = node['id']
        px, py = node['x'], y_pos(node['depth'])
        for branch, label in [('yes', 'Yes'), ('no', 'No')]:
            child_id = node[branch]
            if not child_id:
                continue
            child = lookup.get(child_id)
            if not child:
                continue
            cx, cy = child['x'], y_pos(child['depth'])
            is_active = nid in active_ids and child_id in active_ids
            color = ACTIVE_EDGE_COLOR if is_active else INACTIVE_COLOR
            width = 3.5 if is_active else 1.5

            fig.add_trace(go.Scatter(
                x=[px, cx], y=[py, cy],
                mode='lines',
                line=dict(color=color, width=width,
                          dash='solid' if is_active else 'dot'),
                hoverinfo='none', showlegend=False,
            ))
            # Edge label
            mx, my = (px + cx) / 2, (py + cy) / 2
            fig.add_annotation(
                x=mx, y=my,
                text=f"<b>{label}</b>" if is_active else label,
                showarrow=False,
                font=dict(size=10 if is_active else 8,
                          color=ACTIVE_EDGE_COLOR if is_active else '#94a3b8'),
                bgcolor='white', borderpad=2,
            )

    # ——— Draw nodes ———
    for node in _TREE:
        nid = node['id']
        x, y = node['x'], y_pos(node['depth'])
        is_active = nid in active_ids
        is_leaf = node['leaf'] is not None

        if is_leaf:
            risk = node['leaf']
            rule_name = node.get('rule', '')
            color = RISK_COLORS.get(risk, '#64748b')
            bg = RISK_BG.get(risk, 'rgba(100,116,139,0.1)')

            # Build label
            label = f"<b>{risk}</b><br><sub>{rule_name}</sub>"
            hover = f"{rule_name}: {risk}"
            if is_active and patient.get('conf'):
                hover += f"<br>Confidence: {patient['conf']:.0%}"

            border_color = ACTIVE_EDGE_COLOR if is_active else color
            border_w = 3 if is_active else 1.5
            size = 42 if is_active else 32
        else:
            # Decision node
            label = f"<b>{node['cond']}</b>"
            # Show patient value in hover
            hover = node['cond']
            if patient.get('ml') is not None:
                hover += f"<br>Patient DL: {patient['ml']:.1%}"
            if patient.get('domain'):
                hover += f"<br>Domain: {patient['domain']}"
            if patient.get('fram') is not None:
                hover += f"<br>Framingham: {patient['fram']}"

            color = '#7c3aed' if is_active else '#64748b'
            border_color = ACTIVE_EDGE_COLOR if is_active else NODE_BORDER
            border_w = 3 if is_active else 1
            size = 38 if is_active else 30

        fig.add_trace(go.Scatter(
            x=[x], y=[y],
            mode='markers+text',
            marker=dict(
                size=size,
                color=color if is_leaf else ('rgba(124,58,237,0.15)' if is_active else 'white'),
                symbol='square' if is_leaf else 'diamond',
                line=dict(width=border_w, color=border_color),
            ),
            text=label,
            textposition='top center' if not is_leaf else 'middle center',
            textfont=dict(
                size=9 if is_leaf else 8,
                color='white' if is_leaf else ('#4c1d95' if is_active else '#334155'),
            ),
            hoverinfo='text',
            hovertext=hover,
            showlegend=False,
        ))

    # ——— Patient info box (top-right) ———
    if patient.get('ml') is not None:
        info_lines = [
            f"<b>Patient Values</b>",
            f"DL Prob: {patient['ml']:.1%}",
            f"Domain: {patient.get('domain', 'N/A')}",
            f"Framingham: {patient.get('fram', 'N/A')}",
        ]
        if patient.get('risk'):
            info_lines.append(f"<b>Result: {patient['risk']}</b>")
        fig.add_annotation(
            x=0.02, y=1.02, xref='paper', yref='paper',
            text='<br>'.join(info_lines),
            showarrow=False, align='left',
            font=dict(size=11, color='#1e293b'),
            bgcolor='rgba(241,245,249,0.95)',
            bordercolor='#7c3aed', borderwidth=2, borderpad=8,
        )

    # ——— Layout ———
    fig.update_layout(
        title=dict(
            text='Decision Tree — 10 Rules<br>'
                 '<sub>Purple path = patient decision route</sub>',
            x=0.5, xanchor='center',
            font=dict(size=18, color='#1e293b'),
        ),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                   range=[-0.05, 1.25]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                   range=[y_pos(max_depth + 1) - 0.05, 1.1]),
        plot_bgcolor='white',
        height=750,
        margin=dict(l=10, r=10, t=90, b=10),
        hovermode='closest',
    )

    return fig


# ═══════════════════════════════════════════════════════════════
# 2. جدول القواعد مع بيانات المريض
# ═══════════════════════════════════════════════════════════════

def create_decision_rules_table(final_decision: Dict = None) -> go.Figure:
    """جدول القواعد العشر مع تمييز القاعدة النشطة وقيم المريض."""
    patient = _extract_patient(final_decision)
    active_rule = (patient.get('rule') or '').strip()

    rules = [
        ('Rule 1',  'DL >= 95%',                    'CRITICAL',      0.90),
        ('Rule 2',  'DL >= 90% AND Domain = HIGH',  'CRITICAL',      0.95),
        ('Rule 3',  'DL >= 70% AND Domain = HIGH',  'HIGH',          0.85),
        ('Rule 4',  'DL >= 70% AND Framingham >= 4', 'HIGH',         0.80),
        ('Rule 5',  'Domain = CRITICAL',             'HIGH',          0.75),
        ('Rule 6',  'DL 50-70% AND Domain = HIGH',  'MODERATE-HIGH', 0.70),
        ('Rule 7',  'DL >= 70% AND Domain = MODERATE', 'MODERATE-HIGH', 0.70),
        ('Rule 8',  'DL 40-70% AND Domain = MODERATE', 'MODERATE',   0.65),
        ('Rule 9',  'DL < 40% AND Domain = HIGH',   'LOW-MODERATE',  0.60),
        ('Rule 10', 'DL < 30% AND Domain = LOW',    'LOW',           0.80),
    ]

    col_rule, col_cond, col_dec, col_conf, col_status = [], [], [], [], []
    row_fills = []

    for name, cond, decision, conf in rules:
        is_active = name.lower().replace(' ', '') in active_rule.lower().replace(' ', '')
        col_rule.append(f"<b>{name}</b>" if is_active else name)
        col_cond.append(f"<b>{cond}</b>" if is_active else cond)
        col_dec.append(f"<b>{decision}</b>" if is_active else decision)
        col_conf.append(f"<b>{conf:.0%}</b>" if is_active else f"{conf:.0%}")
        col_status.append('<b>ACTIVE</b>' if is_active else '')
        if is_active:
            row_fills.append(RISK_BG.get(decision, '#dbeafe'))
        else:
            row_fills.append('#fafbfc')

    # Decision column colored by risk
    dec_colors = []
    for _, _, decision, _ in rules:
        dec_colors.append(RISK_COLORS.get(decision, '#64748b'))

    fig = go.Figure(data=[go.Table(
        columnwidth=[80, 250, 130, 90, 80],
        header=dict(
            values=['<b>Rule</b>', '<b>Condition</b>', '<b>Decision</b>',
                    '<b>Confidence</b>', '<b>Status</b>'],
            fill_color='#1e293b',
            align='center',
            font=dict(color='white', size=12),
            height=35,
        ),
        cells=dict(
            values=[col_rule, col_cond, col_dec, col_conf, col_status],
            fill_color=[row_fills],
            align='center',
            font=dict(size=12),
            height=32,
        ),
    )])

    # Title with patient info
    subtitle = '10 Rules for Risk Classification'
    if patient.get('ml') is not None:
        subtitle = (f"Patient: DL={patient['ml']:.1%}, "
                    f"Domain={patient.get('domain', '?')}, "
                    f"Framingham={patient.get('fram', '?')}")

    fig.update_layout(
        title=dict(
            text=f'Decision Rules<br><sub>{subtitle}</sub>',
            x=0.5, xanchor='center',
            font=dict(size=18, color='#1e293b'),
        ),
        height=480,
        margin=dict(l=10, r=10, t=80, b=10),
    )

    return fig


# ═══════════════════════════════════════════════════════════════
# 3. مخطط التدفق مع بيانات المريض الفعلية
# ═══════════════════════════════════════════════════════════════

def create_simple_decision_tree_flow(final_decision: Dict = None) -> go.Figure:
    """مخطط تدفق يوضح مراحل القرار مع القيم الفعلية للمريض."""
    patient = _extract_patient(final_decision)

    # Build dynamic descriptions
    ml_val = f"{patient['ml']:.1%}" if patient.get('ml') is not None else '—'
    domain_val = patient.get('domain') or '—'
    fram_val = str(patient.get('fram')) if patient.get('fram') is not None else '—'
    risk_val = patient.get('risk') or '—'
    conf_val = f"{patient['conf']:.0%}" if patient.get('conf') is not None else '—'
    facts_count = '11' if patient.get('ml') is not None else '?'

    stages = [
        {'name': 'Input Data',          'val': f'{facts_count} Fields Collected',
         'icon': 'clipboard',           'color': '#6366f1'},
        {'name': 'Feature Engineering', 'val': '58 Advanced Features',
         'icon': 'cpu',                 'color': '#8b5cf6'},
        {'name': 'Domain Rules',        'val': f'Risk = {domain_val}  |  Framingham = {fram_val}',
         'icon': 'book-open',           'color': '#a855f7'},
        {'name': 'DL Prediction',       'val': f'Probability = {ml_val}',
         'icon': 'brain',               'color': '#d946ef'},
        {'name': 'Decision Tree',       'val': f'{patient.get("rule") or "10 Rules"} Applied',
         'icon': 'git-branch',          'color': '#7c3aed'},
        {'name': 'Final Decision',      'val': f'{risk_val}  ({conf_val})',
         'icon': 'shield-check',
         'color': RISK_COLORS.get(risk_val, '#dc2626')},
    ]

    fig = go.Figure()

    n = len(stages)
    y_top, y_bot = 0.92, 0.08
    y_step = (y_top - y_bot) / (n - 1) if n > 1 else 0

    for i, stage in enumerate(stages):
        y = y_top - i * y_step
        color = stage['color']
        is_last = (i == n - 1)

        # Main node — rounded rect via marker
        fig.add_trace(go.Scatter(
            x=[0.5], y=[y],
            mode='markers',
            marker=dict(
                size=55 if is_last else 48,
                color=color,
                symbol='square',
                line=dict(width=3, color='white'),
            ),
            hoverinfo='text',
            hovertext=f"{stage['name']}: {stage['val']}",
            showlegend=False,
        ))

        # Stage name
        fig.add_annotation(
            x=0.5, y=y + 0.005,
            text=f"<b>{stage['name']}</b>",
            showarrow=False,
            font=dict(size=12 if is_last else 11, color='white'),
        )

        # Value — to the right
        fig.add_annotation(
            x=0.82, y=y,
            text=stage['val'],
            showarrow=False, align='left',
            font=dict(size=11, color=color),
            bgcolor='rgba(255,255,255,0.85)',
            bordercolor=color, borderwidth=1, borderpad=6,
        )

        # Arrow
        if i < n - 1:
            y_next = y_top - (i + 1) * y_step
            fig.add_annotation(
                x=0.5, y=y - 0.035,
                ax=0.5, ay=y_next + 0.035,
                xref='x', yref='y', axref='x', ayref='y',
                showarrow=True,
                arrowhead=3, arrowsize=1.2, arrowwidth=2.5,
                arrowcolor=stages[i + 1]['color'],
            )

    fig.update_layout(
        title=dict(
            text='Decision Pipeline<br>'
                 '<sub>From Patient Input to Final Risk Level</sub>',
            x=0.5, xanchor='center',
            font=dict(size=18, color='#1e293b'),
        ),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                   range=[0, 1.3]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                   range=[-0.02, 1.05]),
        plot_bgcolor='white',
        height=700,
        margin=dict(l=10, r=10, t=80, b=10),
    )

    return fig
