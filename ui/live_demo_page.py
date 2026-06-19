"""
Live Demo Page - Interactive Heart Disease Risk Analysis
Provides step-by-step visualization of how each engine component processes patient data.
"""

import streamlit as st
import pandas as pd
import time
from typing import Dict
from ui.decision_tree_viz import create_simple_decision_tree_flow, create_decision_tree_diagram


# =========================================================
#  Bilingual Text
# =========================================================

TEXT = {
    'ar': {
        'page_title': 'العرض التفاعلي المباشر',
        'page_subtitle': 'أدخل بيانات المريض وشاهد كيف يعالجها كل مكون خطوة بخطوة',
        'patient_data': 'بيانات المريض',
        'age': 'العمر',
        'sex': 'الجنس',
        'male': 'ذكر',
        'female': 'أنثى',
        'chest_pain': 'نوع ألم الصدر',
        'blood_pressure': 'ضغط الدم',
        'systolic': 'الانقباضي',
        'diastolic': 'الانبساطي',
        'cholesterol': 'الكوليسترول',
        'fasting_bs': 'سكر الصيام',
        'resting_ecg': 'تخطيط القلب',
        'max_hr': 'أقصى معدل نبض',
        'exercise_angina': 'ذبحة صدرية عند المجهود',
        'yes': 'نعم',
        'no': 'لا',
        'oldpeak': 'انخفاض ST',
        'st_slope': 'ميل ST',
        'run_analysis': 'تشغيل التحليل',
        'step1_title': 'الخطوة 1: محرك القواعد الطبية',
        'step1_desc': 'تطبيق القواعد الطبية المتخصصة على بيانات المريض',
        'step2_title': 'الخطوة 2: توليد الخصائص المتقدمة',
        'step2_desc': 'توليد 59 خاصية متقدمة من البيانات الأساسية',
        'step3_title': 'الخطوة 3: تنبؤ نموذج التعلم العميق',
        'step3_desc': 'تنبؤ النموذج باحتمالية مرض القلب',
        'step4_title': 'الخطوة 4: القرار النهائي',
        'step4_desc': 'دمج جميع المصادر في تقييم خطر شامل',
        'processing': 'جارٍ المعالجة...',
        'risk_level': 'مستوى الخطورة',
        'triggered_rules': 'القواعد المفعّلة',
        'risk_factors': 'عوامل الخطر',
        'no_risk_factors': 'لا توجد عوامل خطر ملحوظة',
        'features_generated': 'خاصية تم توليدها',
        'feature_summary': 'ملخص الخصائص',
        'probability': 'الاحتمالية',
        'prediction': 'التنبؤ',
        'positive': 'إيجابي (مرض محتمل)',
        'negative': 'سلبي (طبيعي)',
        'confidence': 'الثقة',
        'model_source': 'مصدر النموذج',
        'final_risk': 'مستوى الخطر النهائي',
        'reasoning': 'التفسير',
        'recommendations': 'التوصيات',
        'processing_time': 'وقت المعالجة',
        'seconds': 'ثانية',
        'rules_count': 'عدد القواعد المفعّلة',
        'top_rules': 'أهم القواعد المفعّلة',
        'rule_id': 'معرّف القاعدة',
        'condition': 'الشرط',
        'weight': 'الوزن',
        'base_features': 'الخصائص الأساسية (12)',
        'advanced_features': 'الخصائص المتقدمة (41)',
        'frequency_features': 'خصائص التكرار (6)',
        'error_msg': 'حدث خطأ أثناء المعالجة',
        'warning_fallback': 'تحذير: يُستخدم التنبؤ الاحتياطي لعدم توفر نموذج DL',
        'all_steps_complete': 'اكتمل التحليل بنجاح',
        'analysis_pipeline': 'مسار التحليل',
    },
    'en': {
        'page_title': 'Interactive Live Demo',
        'page_subtitle': 'Enter patient data and watch how each component processes it step-by-step',
        'patient_data': 'Patient Data',
        'age': 'Age',
        'sex': 'Sex',
        'male': 'Male',
        'female': 'Female',
        'chest_pain': 'Chest Pain Type',
        'blood_pressure': 'Blood Pressure',
        'systolic': 'Systolic',
        'diastolic': 'Diastolic',
        'cholesterol': 'Cholesterol',
        'fasting_bs': 'Fasting Blood Sugar',
        'resting_ecg': 'Resting ECG',
        'max_hr': 'Max Heart Rate',
        'exercise_angina': 'Exercise Angina',
        'yes': 'Yes',
        'no': 'No',
        'oldpeak': 'ST Depression (Oldpeak)',
        'st_slope': 'ST Slope',
        'run_analysis': 'Run Analysis',
        'step1_title': 'Step 1: Domain Rules Engine',
        'step1_desc': 'Applying specialized medical rules to patient data',
        'step2_title': 'Step 2: Advanced Features Generation',
        'step2_desc': 'Generating 58 advanced features from base data',
        'step3_title': 'Step 3: DL Model Prediction',
        'step3_desc': 'Predicting heart disease probability',
        'step4_title': 'Step 4: Final Decision',
        'step4_desc': 'Combining all sources into a comprehensive risk assessment',
        'processing': 'Processing...',
        'risk_level': 'Risk Level',
        'triggered_rules': 'Triggered Rules',
        'risk_factors': 'Risk Factors',
        'no_risk_factors': 'No notable risk factors detected',
        'features_generated': 'features generated',
        'feature_summary': 'Feature Summary',
        'probability': 'Probability',
        'prediction': 'Prediction',
        'positive': 'Positive (Disease Likely)',
        'negative': 'Negative (Normal)',
        'confidence': 'Confidence',
        'model_source': 'Model Source',
        'final_risk': 'Final Risk Level',
        'reasoning': 'Reasoning',
        'recommendations': 'Recommendations',
        'processing_time': 'Processing Time',
        'seconds': 'seconds',
        'rules_count': 'Triggered Rules Count',
        'top_rules': 'Top Triggered Rules',
        'rule_id': 'Rule ID',
        'condition': 'Condition',
        'weight': 'Weight',
        'base_features': 'Base Features (12)',
        'advanced_features': 'Advanced Features (41)',
        'frequency_features': 'Frequency Features (6)',
        'error_msg': 'An error occurred during processing',
        'warning_fallback': 'Warning: Fallback prediction used because DL model is unavailable',
        'all_steps_complete': 'Analysis completed successfully',
        'analysis_pipeline': 'Analysis Pipeline',
    }
}


# =========================================================
#  Risk Level Color Mapping
# =========================================================

RISK_COLORS = {
    'LOW': '#10B981',
    'Low': '#10B981',
    'MODERATE': '#F59E0B',
    'Medium': '#F59E0B',
    'LOW-MODERATE': '#84CC16',
    'MODERATE-HIGH': '#F97316',
    'HIGH': '#F97316',
    'High': '#F97316',
    'CRITICAL': '#EF4444',
}


def _get_risk_color(risk_level: str) -> str:
    """Return hex color for a given risk level string."""
    return RISK_COLORS.get(risk_level, '#6B7280')


def _risk_badge(label: str, risk_level: str) -> str:
    """Return an HTML badge for a risk level."""
    color = _get_risk_color(risk_level)
    return (
        f'<span style="background:{color}; color:white; padding:4px 14px; '
        f'border-radius:20px; font-weight:600; font-size:0.95rem;">'
        f'{label}</span>'
    )


# =========================================================
#  Page CSS
# =========================================================

PAGE_CSS = """
<style>
.demo-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem 1.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    color: white;
    text-align: center;
}
.demo-header h1 { margin: 0; font-size: 1.8rem; }
.demo-header p { margin: 0.4rem 0 0; opacity: 0.9; font-size: 1rem; }

.step-card {
    background: white;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
    border-left: 4px solid #667eea;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.step-card.success { border-left-color: #10B981; }
.step-card.error { border-left-color: #EF4444; }

.step-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #1E293B;
    margin-bottom: 0.3rem;
}
.step-desc {
    font-size: 0.85rem;
    color: #64748B;
    margin-bottom: 0.6rem;
}
.step-time {
    font-size: 0.78rem;
    color: #94A3B8;
}

.metric-row {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin: 0.6rem 0;
}
.metric-box {
    background: #F8FAFC;
    border-radius: 8px;
    padding: 0.7rem 1rem;
    flex: 1;
    min-width: 140px;
    text-align: center;
}
.metric-box .label {
    font-size: 0.78rem;
    color: #64748B;
    margin-bottom: 0.2rem;
}
.metric-box .value {
    font-size: 1.2rem;
    font-weight: 700;
    color: #1E293B;
}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 0.5rem;
    max-height: 320px;
    overflow-y: auto;
    padding: 0.5rem;
}
.feature-item {
    background: #F1F5F9;
    padding: 0.4rem 0.7rem;
    border-radius: 6px;
    font-size: 0.8rem;
    display: flex;
    justify-content: space-between;
}
.feature-item .fname { color: #475569; }
.feature-item .fval { font-weight: 600; color: #1E293B; }

.rules-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
}
.rules-table th {
    background: #F1F5F9;
    padding: 0.5rem 0.7rem;
    text-align: left;
    font-weight: 600;
    color: #475569;
}
.rules-table td {
    padding: 0.5rem 0.7rem;
    border-bottom: 1px solid #F1F5F9;
    color: #1E293B;
}

.final-box {
    background: linear-gradient(135deg, #F8FAFC, #EFF6FF);
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    margin: 1rem 0;
    border: 1px solid #E2E8F0;
}
.final-box .final-level {
    font-size: 1.6rem;
    font-weight: 800;
    margin: 0.5rem 0;
}
</style>
"""


# =========================================================
#  Main Entry Point
# =========================================================

def render_live_demo_page(lang: str = 'en'):
    """
    Render the interactive live demo page.

    Args:
        lang: 'ar' or 'en' for bilingual support.
    """
    t = TEXT.get(lang, TEXT['en'])
    is_rtl = lang == 'ar'

    # Inject CSS
    st.markdown(PAGE_CSS, unsafe_allow_html=True)

    # Header
    st.markdown(
        f'<div class="demo-header">'
        f'<h1>{t["page_title"]}</h1>'
        f'<p>{t["page_subtitle"]}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ----- Input Form -----
    st.markdown(f'### {t["patient_data"]}')

    col1, col2, col3 = st.columns(3)

    with col1:
        age = st.slider(t['age'], 20, 90, 55, key='demo_age')
        sex_options = [t['male'], t['female']]
        sex_label = st.selectbox(t['sex'], sex_options, key='demo_sex')
        sex = 'Male' if sex_label == t['male'] else 'Female'
        chest_pain = st.selectbox(t['chest_pain'], ['ASY', 'NAP', 'ATA', 'TA'], key='demo_cp')
        resting_ecg = st.selectbox(t['resting_ecg'], ['Normal', 'ST', 'LVH'], key='demo_ecg')

    with col2:
        systolic = st.number_input(f"{t['blood_pressure']} - {t['systolic']}", 60, 250, 130, key='demo_sys')
        diastolic = st.number_input(f"{t['blood_pressure']} - {t['diastolic']}", 30, 150, 85, key='demo_dia')
        cholesterol = st.number_input(t['cholesterol'], 50, 600, 240, key='demo_chol')
        fbs_options = ['0', '1']
        fasting_bs = int(st.selectbox(t['fasting_bs'], fbs_options, key='demo_fbs'))

    with col3:
        max_hr = st.slider(t['max_hr'], 60, 220, 150, key='demo_hr')
        angina_options = [t['no'], t['yes']]
        angina_label = st.selectbox(t['exercise_angina'], angina_options, key='demo_angina')
        exercise_angina = 'Y' if angina_label == t['yes'] else 'N'
        oldpeak = st.slider(t['oldpeak'], 0.0, 6.0, 1.0, step=0.1, key='demo_oldpeak')
        st_slope = st.selectbox(t['st_slope'], ['Up', 'Flat', 'Down'], key='demo_slope')

    # Build facts dict
    facts = {
        'Age': age,
        'Sex': sex,
        'ChestPain': chest_pain,
        'BloodPressure': f'{systolic}/{diastolic}',
        'Cholesterol': cholesterol,
        'FastingBS': fasting_bs,
        'RestingECG': resting_ecg,
        'MaxHR': max_hr,
        'ExerciseAngina': exercise_angina,
        'Oldpeak': oldpeak,
        'ST_Slope': st_slope,
    }

    st.markdown('---')

    # ----- Run Analysis Button -----
    if st.button(t['run_analysis'], type='primary', use_container_width=True, key='demo_run'):
        _run_pipeline(facts, t, lang)


# =========================================================
#  Pipeline Execution
# =========================================================

def _run_pipeline(facts: Dict, t: Dict, lang: str):
    """Execute the four-step analysis pipeline and render results."""

    progress = st.progress(0, text=t['processing'])
    step_results = {}

    # ── Step 1: Domain Rules Engine ──
    progress.progress(5, text=f"{t['processing']} {t['step1_title']}")
    start = time.time()
    try:
        from engine.domain_rules_engine import DomainRulesEngine
        dre = DomainRulesEngine()
        domain_result = dre.process_complete_data(facts)
        step1_time = time.time() - start
        step_results['domain'] = domain_result
        step_results['domain_ok'] = True
    except Exception as e:
        step1_time = time.time() - start
        step_results['domain'] = {'error': str(e)}
        step_results['domain_ok'] = False
    progress.progress(25)

    # ── Step 2: Advanced Features ──
    progress.progress(30, text=f"{t['processing']} {t['step2_title']}")
    start = time.time()
    try:
        from engine.advanced_features import AdvancedFeaturesGenerator
        afg = AdvancedFeaturesGenerator()
        features_df = afg.generate(facts)
        feature_summary = afg.get_feature_summary(features_df)
        step2_time = time.time() - start
        step_results['features_df'] = features_df
        step_results['feature_summary'] = feature_summary
        step_results['features_ok'] = True
    except Exception as e:
        step2_time = time.time() - start
        step_results['features_df'] = pd.DataFrame()
        step_results['feature_summary'] = {}
        step_results['features_ok'] = False
        step_results['features_error'] = str(e)
    progress.progress(50)

    # ── Step 3: DL Prediction ──
    progress.progress(55, text=f"{t['processing']} {t['step3_title']}")
    start = time.time()
    try:
        from engine.ml_predictor import HeartDiseasePredictor
        import os
        model_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..', 'models', 'heart_disease_model.keras'
        )
        predictor = HeartDiseasePredictor(model_path=model_path)
        features_for_pred = step_results.get('features_df', pd.DataFrame())
        if features_for_pred.empty:
            ml_result = predictor._fallback_prediction(pd.DataFrame())
        else:
            ml_result = predictor.predict(features_for_pred)
        step3_time = time.time() - start
        step_results['ml'] = ml_result
        step_results['ml_ok'] = True
    except Exception as e:
        step3_time = time.time() - start
        step_results['ml'] = {'error': str(e)}
        step_results['ml_ok'] = False
    progress.progress(75)

    # ── Step 4: Final Decision ──
    progress.progress(80, text=f"{t['processing']} {t['step4_title']}")
    start = time.time()
    try:
        from engine.final_decision_engine import FinalDecisionEngine
        fde = FinalDecisionEngine()

        # Build domain_assessment in the format FinalDecisionEngine expects
        domain_data = step_results.get('domain', {})
        insights = domain_data.get('insights', {})
        domain_assessment = {
            'risk_level': insights.get('risk_level', 'UNKNOWN'),
            'insights': insights,
        }

        ml_pred = step_results.get('ml', {})
        if 'error' in ml_pred:
            ml_pred = {'probability': 0.5, 'prediction': 'Unknown',
                       'confidence': 0.5, 'risk_level': 'MODERATE', 'source': 'Error'}

        feat_df = step_results.get('features_df', pd.DataFrame())
        if feat_df.empty:
            feat_df = pd.DataFrame([{c: 0 for c in range(59)}])

        final_result = fde.make_decision(domain_assessment, ml_pred, feat_df)
        step4_time = time.time() - start
        step_results['final'] = final_result
        step_results['final_ok'] = True
    except Exception as e:
        step4_time = time.time() - start
        step_results['final'] = {'error': str(e)}
        step_results['final_ok'] = False
    progress.progress(100, text=t['all_steps_complete'])

    # Store step times
    step_times = [step1_time, step2_time, step3_time, step4_time]

    st.markdown('---')

    # ── Render results ──
    _render_step1(step_results, step_times[0], t, lang)
    _render_step2(step_results, step_times[1], t, lang)
    _render_step3(step_results, step_times[2], t, lang)
    _render_step4(step_results, step_times[3], t, lang)


# =========================================================
#  Step Renderers
# =========================================================

def _render_step1(results: Dict, elapsed: float, t: Dict, lang: str):
    """Render Step 1: Domain Rules Engine results."""
    with st.expander(t['step1_title'], expanded=True):
        st.caption(t['step1_desc'])
        st.caption(f"{t['processing_time']}: {elapsed:.4f} {t['seconds']}")

        if not results.get('domain_ok'):
            st.error(f"{t['error_msg']}: {results['domain'].get('error', '')}")
            return

        domain = results['domain']
        if domain.get('status') == 'incomplete':
            st.warning(domain.get('message_en', 'Incomplete data'))
            return

        insights = domain.get('insights', {})
        risk_level = insights.get('risk_level', 'Low')
        triggered = domain.get('triggered_rules', [])

        # Metrics row
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                f'**{t["risk_level"]}:** {_risk_badge(risk_level, risk_level)}',
                unsafe_allow_html=True,
            )
        with c2:
            st.metric(t['rules_count'], len(triggered))

        # Risk factors
        factors_key = 'risk_factors_ar' if lang == 'ar' else 'risk_factors_en'
        factors = insights.get(factors_key, [])
        if factors:
            st.markdown(f'**{t["risk_factors"]}**')
            for f in factors:
                st.markdown(f'- {f}')
        else:
            st.info(t['no_risk_factors'])

        # Top rules table
        if triggered:
            st.markdown(f'**{t["top_rules"]}**')
            top = triggered[:8]
            table_html = '<table class="rules-table"><tr>'
            table_html += f'<th>{t["rule_id"]}</th><th>{t["condition"]}</th><th>{t["weight"]}</th>'
            table_html += '</tr>'
            for r in top:
                table_html += (
                    f'<tr><td>{r.get("rule_id", "")}</td>'
                    f'<td style="font-family:monospace;font-size:0.8rem;">{r.get("condition", "")}</td>'
                    f'<td>{r.get("weight", 0):.2f}</td></tr>'
                )
            table_html += '</table>'
            st.markdown(table_html, unsafe_allow_html=True)


def _render_step2(results: Dict, elapsed: float, t: Dict, lang: str):
    """Render Step 2: Advanced Features results."""
    with st.expander(t['step2_title'], expanded=True):
        st.caption(t['step2_desc'])
        st.caption(f"{t['processing_time']}: {elapsed:.4f} {t['seconds']}")

        if not results.get('features_ok'):
            st.error(f"{t['error_msg']}: {results.get('features_error', '')}")
            return

        features_df = results['features_df']
        summary = results.get('feature_summary', {})

        st.metric(t['features_generated'], f'{len(features_df.columns)}')

        # Summary cards
        if summary:
            st.markdown(f'**{t["feature_summary"]}**')
            cols = st.columns(3)
            summary_items = list(summary.items())
            for i, (key, val) in enumerate(summary_items):
                with cols[i % 3]:
                    display_key = key.replace('_', ' ').title()
                    st.markdown(
                        f'<div class="metric-box">'
                        f'<div class="label">{display_key}</div>'
                        f'<div class="value">{val}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

        # Feature groups
        all_cols = list(features_df.columns)
        base_cols = all_cols[:12] if len(all_cols) >= 12 else all_cols
        freq_cols = [c for c in all_cols if c.endswith('_frequency')]
        adv_cols = [c for c in all_cols if c not in base_cols and c not in freq_cols]

        tab_labels = [t['base_features'], t['advanced_features'], t['frequency_features']]
        tab1, tab2, tab3 = st.tabs(tab_labels)

        with tab1:
            _render_feature_grid(features_df, base_cols)
        with tab2:
            _render_feature_grid(features_df, adv_cols)
        with tab3:
            _render_feature_grid(features_df, freq_cols)


def _render_feature_grid(df: pd.DataFrame, columns: list):
    """Render a grid of feature name-value pairs."""
    if not columns:
        st.info('---')
        return
    html = '<div class="feature-grid">'
    for col in columns:
        val = df[col].iloc[0]
        if isinstance(val, float):
            val_str = f'{val:.4f}' if abs(val) < 10 else f'{val:.2f}'
        else:
            val_str = str(val)
        html += (
            f'<div class="feature-item">'
            f'<span class="fname">{col}</span>'
            f'<span class="fval">{val_str}</span>'
            f'</div>'
        )
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def _render_step3(results: Dict, elapsed: float, t: Dict, lang: str):
    """Render Step 3: DL Prediction results."""
    with st.expander(t['step3_title'], expanded=True):
        st.caption(t['step3_desc'])
        st.caption(f"{t['processing_time']}: {elapsed:.4f} {t['seconds']}")

        if not results.get('ml_ok'):
            st.error(f"{t['error_msg']}: {results['ml'].get('error', '')}")
            return

        ml = results['ml']

        # Fallback warning
        if ml.get('warning'):
            st.warning(t['warning_fallback'])

        probability = ml.get('probability', 0.0)
        prediction = ml.get('prediction', 'Unknown')
        confidence = ml.get('confidence', 0.0)
        risk_level = ml.get('risk_level', 'MODERATE')
        source = ml.get('source', 'Unknown')

        # Metrics
        c1, c2, c3 = st.columns(3)
        with c1:
            prob_color = _get_risk_color(risk_level)
            st.markdown(
                f'<div class="metric-box">'
                f'<div class="label">{t["probability"]}</div>'
                f'<div class="value" style="color:{prob_color};">{probability:.1%}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with c2:
            pred_label = t['positive'] if prediction == 'Positive' else t['negative']
            pred_color = '#EF4444' if prediction == 'Positive' else '#10B981'
            st.markdown(
                f'<div class="metric-box">'
                f'<div class="label">{t["prediction"]}</div>'
                f'<div class="value" style="color:{pred_color};">{pred_label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f'<div class="metric-box">'
                f'<div class="label">{t["confidence"]}</div>'
                f'<div class="value">{confidence:.1%}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # Probability bar
        st.progress(min(probability, 1.0))

        # Source
        st.caption(f'{t["model_source"]}: {source}')


def _render_step4(results: Dict, elapsed: float, t: Dict, lang: str):
    """Render Step 4: Final Decision results."""
    with st.expander(t['step4_title'], expanded=True):
        st.caption(t['step4_desc'])
        st.caption(f"{t['processing_time']}: {elapsed:.4f} {t['seconds']}")

        if not results.get('final_ok'):
            st.error(f"{t['error_msg']}: {results['final'].get('error', '')}")
            return

        final = results['final']
        risk_level = final.get('final_risk_level', 'MODERATE')
        risk_level_display = final.get('final_risk_level_ar', risk_level) if lang == 'ar' else risk_level
        confidence = final.get('confidence', 0.0)
        reasoning_key = 'reasoning_ar' if lang == 'ar' else 'reasoning_en'
        reasoning = final.get(reasoning_key, '')

        color = _get_risk_color(risk_level)

        # Final decision box
        st.markdown(
            f'<div class="final-box">'
            f'<div class="label" style="font-size:0.9rem;color:#64748B;">{t["final_risk"]}</div>'
            f'<div class="final-level" style="color:{color};">{risk_level_display}</div>'
            f'<div style="margin:0.3rem 0;">{t["confidence"]}: {confidence:.0%}</div>'
            f'<div style="font-size:0.9rem; color:#475569;">{reasoning}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Sources breakdown
        sources = final.get('sources', {})
        if sources:
            c1, c2 = st.columns(2)
            domain_src = sources.get('domain_rules', {})
            ml_src = sources.get('ml_model', {})

            with c1:
                st.markdown(f'**{t["step1_title"]}**')
                st.markdown(f'- {t["risk_level"]}: {domain_src.get("risk_level", "N/A")}')
                st.markdown(f'- {t["triggered_rules"]}: {domain_src.get("triggered_rules", 0)}')

            with c2:
                st.markdown(f'**{t["step3_title"]}**')
                ml_prob = ml_src.get('probability', 0.0)
                st.markdown(f'- {t["probability"]}: {ml_prob:.1%}')
                st.markdown(f'- {t["prediction"]}: {ml_src.get("prediction", "N/A")}')

        # Decision Tree Visualization
        tree_title = 'مخطط شجرة القرار' if lang == 'ar' else 'Decision Tree Diagram'
        st.markdown(f'**{tree_title}**')
        try:
            tree_fig = create_simple_decision_tree_flow(final)
            st.plotly_chart(tree_fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Decision Tree: {e}")

        # Detailed Decision Tree
        detail_title = 'شجرة القرار التفصيلية' if lang == 'ar' else 'Detailed Decision Tree'
        st.markdown(f'**{detail_title}**')
        try:
            detail_fig = create_decision_tree_diagram(final)
            st.plotly_chart(detail_fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Detailed Tree: {e}")

        # Recommendations
        recs = final.get('recommendations', [])
        if recs:
            st.markdown(f'**{t["recommendations"]}**')
            for rec in recs:
                st.markdown(f'- {rec}')
