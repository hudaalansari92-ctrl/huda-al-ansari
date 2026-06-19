"""
صفحة هيكل النظام - System Architecture Page
Interactive system architecture diagram for the Healthcare Chatbot System Based on Intelligent Techniques
"""

import streamlit as st

# ═══════════════════════════════════════════════════════
#  النصوص ثنائية اللغة
# ═══════════════════════════════════════════════════════

ARCH_TEXT = {
    'ar': {
        'page_title': 'هيكل النظام',
        'page_subtitle': 'خط أنابيب البيانات للتشخيص الذاتي التفكير',
        'pipeline_title': 'خط أنابيب معالجة البيانات',
        'pipeline_subtitle': 'من إدخال المريض إلى تقييم المخاطر النهائي',
        'sr_title': 'ما الذي يجعل هذا النظام "ذاتي التفكير"؟',
        'sr_subtitle': 'مقارنة بين النهج التقليدي والنهج المقترح',
        'traditional_title': 'النهج التقليدي',
        'proposed_title': 'النهج المقترح (ذاتي التفكير)',
        'trad_points': [
            'إدخال ← نموذج DL ← إخراج',
            'صندوق أسود بدون تفسير',
            'لا يوجد تحقق من القواعد الطبية',
            'ثقة واحدة بدون سياق',
            'لا يوجد محادثة تفاعلية',
        ],
        'prop_points': [
            'إدخال ← NER ← تفكير ← قواعد ← DL ← قرار',
            'سلسلة تفكير داخلية تشرح كل خطوة',
            '48 قاعدة طبية للتحقق',
            'درجات ثقة متعددة المصادر',
            'محادثة ذكية مع متابعة',
        ],
        'stats_title': 'إحصائيات النظام الرئيسية',
        'stat_rules': 'قاعدة طبية',
        'stat_features': 'ميزة مولدة',
        'stat_params': 'معامل شبكة',
        'stat_binary': 'ميزة ثنائية',
        'stat_continuous': 'ميزة مستمرة',
        'stat_decisions': 'قواعد قرار',
        'comp_user': 'المستخدم',
        'comp_user_desc': 'يدخل الأعراض عبر المحادثة',
        'comp_biobert': 'التعرف على الكيانات',
        'comp_biobert_desc': 'استخراج الكيانات الطبية',
        'comp_groq': 'إدارة المحادثة',
        'comp_groq_desc': 'التعرف + إدارة الحوار',
        'comp_sr': 'محرك التفكير الذاتي',
        'comp_sr_desc': 'سلسلة تفكير داخلية للاستدلال',
        'comp_domain': 'محرك القواعد الطبية',
        'comp_domain_desc': '48 قاعدة، 31 ثنائية، 9 مستمرة',
        'comp_features': 'مولد الميزات المتقدمة',
        'comp_features_desc': '58 ميزة (11 أساسية + 41 متقدمة + 6 تكرارية)',
        'comp_ml': 'نموذج التعلم العميق',
        'comp_ml_desc': 'شبكة Keras (79,809 معامل، 58 إدخال)',
        'comp_decision': 'محرك القرار النهائي',
        'comp_decision_desc': 'شجرة قرار 10 قواعد (قواعد + DL)',
        'comp_output': 'تقييم المخاطر',
        'comp_output_desc': 'منخفض / متوسط / مرتفع / حرج',
        'legend_title': 'دليل الألوان',
        'legend_nlp': 'معالجة اللغة الطبيعية',
        'legend_rules': 'القواعد والمعرفة',
        'legend_ml': 'التعلم العميق',
        'legend_decision': 'القرار والإخراج',
    },
    'en': {
        'page_title': 'System Architecture',
        'page_subtitle': 'Self-Reasoning Diagnostic Data Pipeline',
        'pipeline_title': 'Data Processing Pipeline',
        'pipeline_subtitle': 'From Patient Input to Final Risk Assessment',
        'sr_title': 'What Makes This a "Self-Reasoning" System?',
        'sr_subtitle': 'Traditional Approach vs Proposed Approach',
        'traditional_title': 'Traditional Approach',
        'proposed_title': 'Proposed (Self-Reasoning)',
        'trad_points': [
            'Input → DL Model → Output',
            'Black box with no explanation',
            'No medical rule validation',
            'Single confidence without context',
            'No interactive conversation',
        ],
        'prop_points': [
            'Input → NER → Reasoning → Rules → DL → Decision',
            'Internal monologue explains each step',
            '48 medical rules for validation',
            'Multi-source confidence scores',
            'Smart conversation with follow-ups',
        ],
        'stats_title': 'Key System Statistics',
        'stat_rules': 'Medical Rules',
        'stat_features': 'Generated Features',
        'stat_params': 'Network Parameters',
        'stat_binary': 'Binary Features',
        'stat_continuous': 'Continuous Features',
        'stat_decisions': 'Decision Rules',
        'comp_user': 'User Input',
        'comp_user_desc': 'Patient enters symptoms via chatbot',
        'comp_biobert': 'BioBERT NER',
        'comp_biobert_desc': 'Named Entity Recognition extracts medical entities',
        'comp_groq': 'Groq LLaMA 3.3 70B',
        'comp_groq_desc': 'NER + Conversation management',
        'comp_sr': 'Self-Reasoning Engine',
        'comp_sr_desc': 'Internal Chain-of-Thought for reasoning',
        'comp_domain': 'Domain Rules Engine',
        'comp_domain_desc': '48 medical rules, 31 binary, 9 continuous features',
        'comp_features': 'Advanced Features Generator',
        'comp_features_desc': '58 features (11 base + 41 advanced + 6 frequency)',
        'comp_ml': 'DL Model',
        'comp_ml_desc': 'Keras Neural Network (79,809 params, 58 inputs)',
        'comp_decision': 'Final Decision Engine',
        'comp_decision_desc': '10-rule decision tree combining domain + DL',
        'comp_output': 'Risk Assessment Output',
        'comp_output_desc': 'Final risk level (Low / Medium / High / Critical)',
        'legend_title': 'Color Legend',
        'legend_nlp': 'Natural Language Processing',
        'legend_rules': 'Rules & Knowledge',
        'legend_ml': 'Deep Learning',
        'legend_decision': 'Decision & Output',
    },
}


# ═══════════════════════════════════════════════════════
#  ثوابت الألوان
# ═══════════════════════════════════════════════════════

COLORS = {
    'proposed': '#34D399',
    'traditional': '#5B8DEF',
    'accent': '#8B5CF6',
    'nlp_primary': '#3B82F6',
    'nlp_light': '#DBEAFE',
    'nlp_glow': 'rgba(59,130,246,0.25)',
    'rules_primary': '#F97316',
    'rules_light': '#FFF7ED',
    'rules_glow': 'rgba(249,115,22,0.25)',
    'ml_primary': '#8B5CF6',
    'ml_light': '#F3E8FF',
    'ml_glow': 'rgba(139,92,246,0.25)',
    'decision_primary': '#10B981',
    'decision_light': '#D1FAE5',
    'decision_glow': 'rgba(16,185,129,0.25)',
    'user_primary': '#6366F1',
    'user_light': '#E0E7FF',
    'user_glow': 'rgba(99,102,241,0.25)',
}


def _build_diagram_html(t: dict, is_rtl: bool) -> str:
    """Build the full HTML/CSS for the architecture diagram."""

    direction = 'rtl' if is_rtl else 'ltr'
    text_align = 'right' if is_rtl else 'left'
    font_family = "'Segoe UI', Tahoma, sans-serif"

    # Each component: (key_prefix, label, desc, category, stat_badge)
    components = [
        ('user',     t['comp_user'],     t['comp_user_desc'],     'user',     None),
        ('biobert',  t['comp_biobert'],   t['comp_biobert_desc'],  'nlp',      'BioBERT'),
        ('groq',     t['comp_groq'],      t['comp_groq_desc'],     'nlp',      'LLaMA 3.3 70B'),
        ('sr',       t['comp_sr'],        t['comp_sr_desc'],       'nlp',      'Chain-of-Thought'),
        ('domain',   t['comp_domain'],    t['comp_domain_desc'],   'rules',    '48 rules'),
        ('features', t['comp_features'],  t['comp_features_desc'], 'rules',    '58 features'),
        ('ml',       t['comp_ml'],        t['comp_ml_desc'],       'ml',       '79,809 params'),
        ('decision', t['comp_decision'],  t['comp_decision_desc'], 'decision', '10 rules'),
        ('output',   t['comp_output'],    t['comp_output_desc'],   'decision', '4 levels'),
    ]

    cat_colors = {
        'user':     (COLORS['user_primary'],     COLORS['user_light'],     COLORS['user_glow']),
        'nlp':      (COLORS['nlp_primary'],      COLORS['nlp_light'],      COLORS['nlp_glow']),
        'rules':    (COLORS['rules_primary'],     COLORS['rules_light'],    COLORS['rules_glow']),
        'ml':       (COLORS['ml_primary'],        COLORS['ml_light'],       COLORS['ml_glow']),
        'decision': (COLORS['decision_primary'],  COLORS['decision_light'], COLORS['decision_glow']),
    }

    # Category icons (pure CSS/unicode)
    cat_icons = {
        'user':     '',
        'nlp':      '',
        'rules':    '',
        'ml':       '',
        'decision': '',
    }

    # Build component cards
    arrow_html = '<div class="arrow-connector"><div class="arrow-line"></div><div class="arrow-head">&#9660;</div></div>'
    cards_html = []
    for idx, (key, label, desc, cat, badge) in enumerate(components):
        primary, light, glow = cat_colors[cat]
        icon = cat_icons[cat]
        delay = idx * 0.12

        badge_html = ''
        if badge:
            badge_html = f'''
            <span class="comp-badge" style="
                background: {primary};
                color: white;
            ">{badge}</span>'''

        cards_html.append(f'''
        <div class="comp-card" style="
            --card-primary: {primary};
            --card-light: {light};
            --card-glow: {glow};
            animation-delay: {delay}s;
        ">
            <div class="comp-icon">{icon}</div>
            <div class="comp-content">
                <div class="comp-header">
                    <span class="comp-number">{idx + 1}</span>
                    <h3 class="comp-label">{label}</h3>
                    {badge_html}
                </div>
                <p class="comp-desc">{desc}</p>
            </div>
            <div class="comp-accent-bar"></div>
        </div>
        {arrow_html if idx < len(components) - 1 else ""}
        ''')

    cards_block = '\n'.join(cards_html)

    # Legend items
    legend_items = [
        (COLORS['nlp_primary'],      t['legend_nlp']),
        (COLORS['rules_primary'],    t['legend_rules']),
        (COLORS['ml_primary'],       t['legend_ml']),
        (COLORS['decision_primary'], t['legend_decision']),
    ]
    legend_html = '\n'.join(
        f'<div class="legend-item"><span class="legend-dot" style="background:{c};"></span>{lbl}</div>'
        for c, lbl in legend_items
    )

    # Stats bar
    stats = [
        ('48',     t['stat_rules'],      COLORS['rules_primary']),
        ('58',     t['stat_features'],    COLORS['ml_primary']),
        ('79,809', t['stat_params'],      COLORS['accent']),
        ('31',     t['stat_binary'],      COLORS['nlp_primary']),
        ('9',      t['stat_continuous'],  COLORS['proposed']),
        ('10',     t['stat_decisions'],   COLORS['decision_primary']),
    ]
    stats_html = '\n'.join(
        f'''<div class="stat-card" style="--stat-color: {c};">
            <div class="stat-value">{v}</div>
            <div class="stat-label">{lbl}</div>
        </div>'''
        for v, lbl, c in stats
    )

    # Self-Reasoning comparison
    trad_items = '\n'.join(
        f'<li><span class="list-icon trad-icon">&#10005;</span>{p}</li>'
        for p in t['trad_points']
    )
    prop_items = '\n'.join(
        f'<li><span class="list-icon prop-icon">&#10003;</span>{p}</li>'
        for p in t['prop_points']
    )

    html = f'''
    <div id="arch-root" style="direction:{direction}; font-family:{font_family}; text-align:{text_align};">
    <style>
        /* ═══ Reset & Base ═══ */
        #arch-root * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        #arch-root {{
            max-width: 900px;
            margin: 0 auto;
            padding: 0 1rem;
        }}

        /* ═══ Animations ═══ */
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes pulseGlow {{
            0%, 100% {{ box-shadow: 0 4px 20px var(--card-glow); }}
            50%      {{ box-shadow: 0 8px 40px var(--card-glow), 0 0 60px var(--card-glow); }}
        }}
        @keyframes flowDown {{
            0%   {{ background-position: 0 0; }}
            100% {{ background-position: 0 20px; }}
        }}
        @keyframes arrowBounce {{
            0%, 100% {{ transform: translateY(0); }}
            50%      {{ transform: translateY(4px); }}
        }}
        @keyframes slideIn {{
            from {{ opacity: 0; transform: translateX({30 if is_rtl else -30}px); }}
            to   {{ opacity: 1; transform: translateX(0); }}
        }}

        /* ═══ Section Header ═══ */
        .section-header {{
            text-align: center;
            margin-bottom: 2rem;
            animation: fadeInUp 0.6s ease-out;
        }}
        .section-header h2 {{
            font-size: 1.6rem;
            font-weight: 700;
            color: #1E293B;
            margin-bottom: 0.3rem;
        }}
        .section-header p {{
            font-size: 0.95rem;
            color: #64748B;
        }}

        /* ═══ Component Card ═══ */
        .comp-card {{
            background: white;
            border-radius: 16px;
            padding: 1.2rem 1.5rem;
            display: flex;
            align-items: center;
            gap: 1rem;
            position: relative;
            overflow: hidden;
            border: 1px solid #E2E8F0;
            box-shadow: 0 4px 20px var(--card-glow);
            opacity: 0;
            animation: fadeInUp 0.6s ease-out forwards, pulseGlow 4s ease-in-out infinite;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        .comp-card:hover {{
            transform: translateY(-3px) scale(1.01);
            box-shadow: 0 12px 40px var(--card-glow);
        }}
        .comp-accent-bar {{
            position: absolute;
            top: 0;
            {('right' if is_rtl else 'left')}: 0;
            width: 5px;
            height: 100%;
            background: linear-gradient(180deg, var(--card-primary), transparent);
            border-radius: 0 0 5px 5px;
        }}
        .comp-icon {{
            font-size: 2rem;
            width: 56px;
            height: 56px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--card-light);
            border-radius: 14px;
            flex-shrink: 0;
            border: 2px solid var(--card-primary);
        }}
        .comp-content {{
            flex: 1;
            min-width: 0;
        }}
        .comp-header {{
            display: flex;
            align-items: center;
            gap: 0.6rem;
            flex-wrap: wrap;
            margin-bottom: 0.3rem;
        }}
        .comp-number {{
            width: 26px;
            height: 26px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--card-primary);
            color: white;
            border-radius: 50%;
            font-size: 0.75rem;
            font-weight: 700;
            flex-shrink: 0;
        }}
        .comp-label {{
            font-size: 1.05rem;
            font-weight: 700;
            color: #1E293B;
        }}
        .comp-badge {{
            font-size: 0.7rem;
            font-weight: 600;
            padding: 0.2rem 0.6rem;
            border-radius: 20px;
            letter-spacing: 0.02em;
            white-space: nowrap;
        }}
        .comp-desc {{
            font-size: 0.85rem;
            color: #64748B;
            line-height: 1.5;
        }}

        /* ═══ Arrow Connector ═══ */
        .arrow-connector {{
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 0.15rem 0;
        }}
        .arrow-line {{
            width: 3px;
            height: 22px;
            background: repeating-linear-gradient(
                180deg,
                #94A3B8 0px,
                #94A3B8 4px,
                transparent 4px,
                transparent 8px
            );
            animation: flowDown 0.8s linear infinite;
        }}
        .arrow-head {{
            color: #94A3B8;
            font-size: 0.7rem;
            line-height: 1;
            animation: arrowBounce 1.2s ease-in-out infinite;
        }}

        /* ═══ Legend ═══ */
        .legend-bar {{
            display: flex;
            flex-wrap: wrap;
            gap: 1.2rem;
            justify-content: center;
            margin: 1.5rem 0 2.5rem;
            padding: 1rem 1.5rem;
            background: white;
            border-radius: 12px;
            border: 1px solid #E2E8F0;
            animation: fadeInUp 0.6s ease-out 1.1s forwards;
            opacity: 0;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 0.4rem;
            font-size: 0.82rem;
            color: #475569;
            font-weight: 500;
        }}
        .legend-dot {{
            width: 12px;
            height: 12px;
            border-radius: 4px;
            flex-shrink: 0;
        }}

        /* ═══ Stats Grid ═══ */
        .stats-header {{
            text-align: center;
            margin: 2.5rem 0 1.2rem;
            animation: fadeInUp 0.6s ease-out 1.3s forwards;
            opacity: 0;
        }}
        .stats-header h2 {{
            font-size: 1.4rem;
            font-weight: 700;
            color: #1E293B;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
            margin-bottom: 2.5rem;
            animation: fadeInUp 0.6s ease-out 1.5s forwards;
            opacity: 0;
        }}
        .stat-card {{
            background: white;
            border-radius: 14px;
            padding: 1.3rem 1rem;
            text-align: center;
            border: 1px solid #E2E8F0;
            box-shadow: 0 2px 12px rgba(0,0,0,0.04);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border-top: 4px solid var(--stat-color);
        }}
        .stat-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        }}
        .stat-value {{
            font-size: 1.8rem;
            font-weight: 800;
            color: var(--stat-color);
            line-height: 1.2;
        }}
        .stat-label {{
            font-size: 0.78rem;
            color: #64748B;
            margin-top: 0.3rem;
            font-weight: 500;
        }}

        /* ═══ Self-Reasoning Comparison ═══ */
        .sr-section {{
            margin-top: 1rem;
            animation: fadeInUp 0.6s ease-out 1.7s forwards;
            opacity: 0;
        }}
        .sr-header {{
            text-align: center;
            margin-bottom: 1.5rem;
        }}
        .sr-header h2 {{
            font-size: 1.4rem;
            font-weight: 700;
            color: #1E293B;
            margin-bottom: 0.3rem;
        }}
        .sr-header p {{
            font-size: 0.9rem;
            color: #64748B;
        }}
        .sr-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
        }}
        .sr-card {{
            border-radius: 16px;
            padding: 1.5rem;
            border: 1px solid #E2E8F0;
        }}
        .sr-card.traditional {{
            background: linear-gradient(135deg, #EFF6FF 0%, #F8FAFC 100%);
            border-color: {COLORS['traditional']};
        }}
        .sr-card.proposed {{
            background: linear-gradient(135deg, #ECFDF5 0%, #F0FDF4 100%);
            border-color: {COLORS['proposed']};
        }}
        .sr-card h3 {{
            font-size: 1.05rem;
            font-weight: 700;
            margin-bottom: 1rem;
            padding-bottom: 0.7rem;
            border-bottom: 2px solid #E2E8F0;
        }}
        .sr-card.traditional h3 {{
            color: {COLORS['traditional']};
        }}
        .sr-card.proposed h3 {{
            color: {COLORS['proposed']};
        }}
        .sr-card ul {{
            list-style: none;
            padding: 0;
        }}
        .sr-card li {{
            display: flex;
            align-items: flex-start;
            gap: 0.5rem;
            font-size: 0.85rem;
            color: #334155;
            margin-bottom: 0.7rem;
            line-height: 1.5;
            animation: slideIn 0.4s ease-out forwards;
            opacity: 0;
        }}
        .sr-card li:nth-child(1) {{ animation-delay: 1.9s; }}
        .sr-card li:nth-child(2) {{ animation-delay: 2.05s; }}
        .sr-card li:nth-child(3) {{ animation-delay: 2.2s; }}
        .sr-card li:nth-child(4) {{ animation-delay: 2.35s; }}
        .sr-card li:nth-child(5) {{ animation-delay: 2.5s; }}
        .list-icon {{
            font-size: 0.85rem;
            font-weight: 700;
            flex-shrink: 0;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
        }}
        .trad-icon {{
            color: #EF4444;
            background: #FEE2E2;
        }}
        .prop-icon {{
            color: #10B981;
            background: #D1FAE5;
        }}

        /* ═══ Responsive ═══ */
        @media (max-width: 700px) {{
            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            .sr-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>

    <!-- Pipeline Header -->
    <div class="section-header">
        <h2>{t['pipeline_title']}</h2>
        <p>{t['pipeline_subtitle']}</p>
    </div>

    <!-- Legend -->
    <div class="legend-bar">
        {legend_html}
    </div>

    <!-- Pipeline Diagram -->
    <div class="pipeline">
        {cards_block}
    </div>

    <!-- Stats -->
    <div class="stats-header">
        <h2>{t['stats_title']}</h2>
    </div>
    <div class="stats-grid">
        {stats_html}
    </div>

    <!-- Self-Reasoning Section -->
    <div class="sr-section">
        <div class="sr-header">
            <h2>{t['sr_title']}</h2>
            <p>{t['sr_subtitle']}</p>
        </div>
        <div class="sr-grid">
            <div class="sr-card traditional">
                <h3>{t['traditional_title']}</h3>
                <ul>{trad_items}</ul>
            </div>
            <div class="sr-card proposed">
                <h3>{t['proposed_title']}</h3>
                <ul>{prop_items}</ul>
            </div>
        </div>
    </div>
    </div>
    '''
    return html


# ═══════════════════════════════════════════════════════
#  نقطة الدخول الرئيسية
# ═══════════════════════════════════════════════════════

def render_architecture_page(lang: str = 'ar') -> None:
    """Render the interactive system architecture page.

    Parameters
    ----------
    lang : str
        Language code, either ``'ar'`` (Arabic) or ``'en'`` (English).
    """
    t = ARCH_TEXT.get(lang, ARCH_TEXT['en'])
    is_rtl = lang == 'ar'

    # Page header
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem 2rem;
            border-radius: 20px;
            margin-bottom: 1.5rem;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
            text-align: center;
            position: relative;
            overflow: hidden;
        ">
            <div style="position:relative; z-index:1;">
                <h1 style="color:white; font-size:2rem; font-weight:800; margin:0 0 0.3rem;">
                    {t['page_title']}
                </h1>
                <p style="color:rgba(255,255,255,0.85); font-size:1rem; margin:0;">
                    {t['page_subtitle']}
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Main diagram via st.html
    diagram_html = _build_diagram_html(t, is_rtl)
    st.html(diagram_html)
