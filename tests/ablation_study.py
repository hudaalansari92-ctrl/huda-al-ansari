"""
Ablation Study — دراسة إزالة المكونات
يختبر النظام بإزالة مكوّن واحد في كل تجربة لقياس مساهمة كل مكوّن

يستخدم بيانات Heart Disease من UCI
ويدرّب نموذج ML محلياً (RandomForest) + القواعد الطبية + الميزات المتقدمة

الاستخدام:
    python tests/ablation_study.py
"""

import sys
import os
import json
import logging
import warnings
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple

# إضافة مسار المشروع
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.WARNING)
warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════
#  تحميل البيانات
# ═══════════════════════════════════════════════════════

def load_heart_disease_data() -> pd.DataFrame:
    """تحميل بيانات Heart Disease"""
    local_path = Path(__file__).parent.parent / 'data' / 'heart.csv'

    if local_path.exists():
        print(f"[+] Loading data from {local_path}")
        return pd.read_csv(local_path)

    urls = [
        'https://raw.githubusercontent.com/kb22/Heart-Disease-Prediction/master/dataset.csv',
        'https://raw.githubusercontent.com/sharmaroshan/Heart-UCI-Dataset/master/heart.csv',
    ]

    for url in urls:
        try:
            print(f"[*] Downloading from {url}...")
            df = pd.read_csv(url)
            if len(df) > 0:
                print(f"[+] Loaded {len(df)} records")
                local_path.parent.mkdir(exist_ok=True)
                df.to_csv(local_path, index=False)
                return df
        except Exception as e:
            print(f"[-] Failed: {e}")
            continue

    print("[!] Cannot download data. Generating synthetic dataset...")
    return generate_synthetic_data()


def generate_synthetic_data(n=701) -> pd.DataFrame:
    """توليد بيانات اصطناعية مبنية على إحصائيات domain_rules.json"""
    np.random.seed(42)
    n_high = 449
    n_low = 252

    data = []
    for label, count in [(1, n_high), (0, n_low)]:
        for _ in range(count):
            if label == 1:
                age = np.random.randint(45, 75)
                sex = np.random.choice(['Male', 'Female'], p=[0.75, 0.25])
                chest_pain = np.random.choice(['ASY', 'NAP', 'ATA', 'TA'], p=[0.55, 0.20, 0.15, 0.10])
                systolic = np.random.randint(130, 180)
                diastolic = np.random.randint(80, 110)
                cholesterol = np.random.randint(220, 400)
                fasting_bs = np.random.choice([0, 1], p=[0.55, 0.45])
                resting_ecg = np.random.choice(['Normal', 'ST', 'LVH'], p=[0.40, 0.40, 0.20])
                max_hr = np.random.randint(90, 160)
                exercise_angina = np.random.choice(['Y', 'N'], p=[0.55, 0.45])
                oldpeak = round(np.random.uniform(0.5, 4.0), 1)
                st_slope = np.random.choice(['Flat', 'Down', 'Up'], p=[0.55, 0.25, 0.20])
            else:
                age = np.random.randint(25, 55)
                sex = np.random.choice(['Male', 'Female'], p=[0.50, 0.50])
                chest_pain = np.random.choice(['ASY', 'NAP', 'ATA', 'TA'], p=[0.15, 0.25, 0.35, 0.25])
                systolic = np.random.randint(100, 135)
                diastolic = np.random.randint(60, 85)
                cholesterol = np.random.randint(150, 250)
                fasting_bs = np.random.choice([0, 1], p=[0.85, 0.15])
                resting_ecg = np.random.choice(['Normal', 'ST', 'LVH'], p=[0.75, 0.15, 0.10])
                max_hr = np.random.randint(140, 200)
                exercise_angina = np.random.choice(['Y', 'N'], p=[0.15, 0.85])
                oldpeak = round(np.random.uniform(0.0, 1.5), 1)
                st_slope = np.random.choice(['Flat', 'Down', 'Up'], p=[0.25, 0.15, 0.60])

            data.append({
                'Age': age, 'Sex': sex, 'ChestPain': chest_pain,
                'BloodPressure': f'{systolic}/{diastolic}',
                'Cholesterol': cholesterol, 'FastingBS': fasting_bs,
                'RestingECG': resting_ecg, 'MaxHR': max_hr,
                'ExerciseAngina': exercise_angina, 'Oldpeak': oldpeak,
                'ST_Slope': st_slope, 'HeartDisease': label,
            })

    df = pd.DataFrame(data)
    return df.sample(frac=1, random_state=42).reset_index(drop=True)


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """تطبيع أعمدة DataFrame"""
    col_mapping = {
        'age': 'Age', 'sex': 'Sex', 'cp': 'ChestPain',
        'chestpaintype': 'ChestPain', 'trestbps': 'BloodPressure',
        'restingbp': 'BloodPressure', 'restingbloodpressure': 'BloodPressure',
        'chol': 'Cholesterol', 'cholesterol': 'Cholesterol',
        'fbs': 'FastingBS', 'fastingbs': 'FastingBS',
        'restecg': 'RestingECG', 'restingecg': 'RestingECG',
        'thalach': 'MaxHR', 'maxhr': 'MaxHR', 'maxheartrate': 'MaxHR',
        'exang': 'ExerciseAngina', 'exerciseangina': 'ExerciseAngina',
        'oldpeak': 'Oldpeak', 'slope': 'ST_Slope', 'st_slope': 'ST_Slope',
        'target': 'HeartDisease', 'heartdisease': 'HeartDisease', 'num': 'HeartDisease',
    }
    df.columns = [col_mapping.get(c.lower().strip(), c) for c in df.columns]

    if 'Sex' in df.columns and df['Sex'].dtype in ['int64', 'float64']:
        df['Sex'] = df['Sex'].map({1: 'Male', 0: 'Female'})
    if 'ChestPain' in df.columns and df['ChestPain'].dtype in ['int64', 'float64']:
        df['ChestPain'] = df['ChestPain'].map({0: 'ATA', 1: 'NAP', 2: 'ASY', 3: 'TA'})
    if 'RestingECG' in df.columns and df['RestingECG'].dtype in ['int64', 'float64']:
        df['RestingECG'] = df['RestingECG'].map({0: 'Normal', 1: 'ST', 2: 'LVH'})
    if 'ExerciseAngina' in df.columns and df['ExerciseAngina'].dtype in ['int64', 'float64']:
        df['ExerciseAngina'] = df['ExerciseAngina'].map({1: 'Y', 0: 'N'})
    if 'ST_Slope' in df.columns and df['ST_Slope'].dtype in ['int64', 'float64']:
        df['ST_Slope'] = df['ST_Slope'].map({0: 'Up', 1: 'Flat', 2: 'Down'})
    if 'BloodPressure' in df.columns and df['BloodPressure'].dtype in ['int64', 'float64']:
        df['BloodPressure'] = df['BloodPressure'].astype(int).astype(str) + '/80'
    if 'HeartDisease' in df.columns:
        df['HeartDisease'] = (df['HeartDisease'] > 0).astype(int)

    return df


# ═══════════════════════════════════════════════════════
#  تدريب ML Model محلياً (بدلاً من TensorFlow)
# ═══════════════════════════════════════════════════════

def train_ml_model(df: pd.DataFrame):
    """
    تدريب RandomForest على الميزات المتقدمة
    يعيد الموديل المدرّب + أسماء الميزات
    """
    from sklearn.ensemble import RandomForestClassifier
    from engine.advanced_features import AdvancedFeaturesGenerator

    feat_gen = AdvancedFeaturesGenerator()
    print("[*] Generating advanced features for training...")

    all_features = []
    for _, row in df.iterrows():
        facts = row_to_facts(row)
        features_df = feat_gen.generate(facts)
        all_features.append(features_df.iloc[0].to_dict())

    X = pd.DataFrame(all_features)
    y = df['HeartDisease'].values

    # تعبئة القيم الناقصة
    X = X.fillna(0)

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X, y)

    print(f"[+] ML Model trained: {X.shape[1]} features, {len(y)} samples")
    return model, X.columns.tolist(), feat_gen


# ═══════════════════════════════════════════════════════
#  أدوات مساعدة
# ═══════════════════════════════════════════════════════

def row_to_facts(row) -> Dict:
    """تحويل صف DataFrame إلى facts dict"""
    return {
        'Age': int(row.get('Age', 50)),
        'Sex': str(row.get('Sex', 'Male')),
        'ChestPain': str(row.get('ChestPain', 'ATA')),
        'BloodPressure': str(row.get('BloodPressure', '120/80')),
        'Cholesterol': int(row.get('Cholesterol', 200)),
        'FastingBS': int(row.get('FastingBS', 0)),
        'RestingECG': str(row.get('RestingECG', 'Normal')),
        'MaxHR': int(row.get('MaxHR', 150)),
        'ExerciseAngina': str(row.get('ExerciseAngina', 'N')),
        'Oldpeak': float(row.get('Oldpeak', 0.0)),
        'ST_Slope': str(row.get('ST_Slope', 'Flat')),
    }


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
    """حساب مقاييس الأداء"""
    tp = np.sum((y_true == 1) & (y_pred == 1))
    tn = np.sum((y_true == 0) & (y_pred == 0))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))

    accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    balanced_acc = (recall + specificity) / 2

    return {
        'accuracy': round(accuracy * 100, 2),
        'precision': round(precision * 100, 2),
        'recall': round(recall * 100, 2),
        'f1_score': round(f1 * 100, 2),
        'specificity': round(specificity * 100, 2),
        'balanced_accuracy': round(balanced_acc * 100, 2),
    }


def calculate_metrics_cv(df: pd.DataFrame, predict_fn, n_folds=5) -> Dict:
    """
    حساب المقاييس باستخدام Cross-Validation
    لتجنب التحيز (خاصة للـ ML model)
    """
    from sklearn.model_selection import StratifiedKFold

    y_all = df['HeartDisease'].values
    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)

    fold_metrics = []
    for fold, (train_idx, test_idx) in enumerate(skf.split(df, y_all), 1):
        df_test = df.iloc[test_idx]
        y_true = y_all[test_idx]
        y_pred = predict_fn(df_test, train_idx=train_idx)
        metrics = calculate_metrics(y_true, y_pred)
        fold_metrics.append(metrics)

    # متوسط المقاييس
    avg = {}
    for key in fold_metrics[0]:
        values = [m[key] for m in fold_metrics]
        avg[key] = round(np.mean(values), 2)
        avg[f'{key}_std'] = round(np.std(values), 2)

    avg['fold_details'] = fold_metrics
    return avg


# ═══════════════════════════════════════════════════════
#  تجارب Ablation (مع Cross-Validation)
# ═══════════════════════════════════════════════════════

def _get_domain_features(engine, facts):
    """
    استخراج ميزات إضافية من محرك القواعد الطبية
    تُضاف كميزات إضافية للـ ML model (stacking)
    """
    result = engine.process_complete_data(facts)
    insights = result.get('insights', {})
    risk = insights.get('risk_level', 'Low')

    risk_map = {'Low': 0.0, 'Medium': 0.5, 'High': 0.8, 'Critical': 1.0}
    return {
        'domain_risk_score': risk_map.get(risk, 0.3),
        'domain_triggered_rules': insights.get('triggered_rules_count', 0),
        'domain_risk_is_high': 1 if risk in ['High', 'Critical'] else 0,
        'domain_risk_is_medium': 1 if risk == 'Medium' else 0,
    }


def experiment_full_system(df: pd.DataFrame, n_folds=5) -> Dict:
    """
    تجربة 1: النظام الكامل (Baseline)
    Domain Rules (as features) + ML Model + Advanced Features
    Stacking: domain signals injected as extra ML features
    """
    from sklearn.ensemble import RandomForestClassifier
    from engine.domain_rules_engine import DomainRulesEngine
    from engine.advanced_features import AdvancedFeaturesGenerator

    engine = DomainRulesEngine()
    feat_gen = AdvancedFeaturesGenerator()

    def predict_fn(df_test, train_idx=None):
        # تدريب ML على بيانات التدريب + ميزات Domain
        train_features = []
        y_train = df.iloc[train_idx]['HeartDisease'].values
        for _, row in df.iloc[train_idx].iterrows():
            facts = row_to_facts(row)
            features = feat_gen.generate(facts)
            feat_dict = features.iloc[0].to_dict()
            # إضافة ميزات Domain Rules
            domain_feats = _get_domain_features(engine, facts)
            feat_dict.update(domain_feats)
            train_features.append(feat_dict)

        X_train = pd.DataFrame(train_features).fillna(0)
        ml_model = RandomForestClassifier(
            n_estimators=200, max_depth=12, min_samples_split=5,
            min_samples_leaf=2, random_state=42, n_jobs=-1
        )
        ml_model.fit(X_train, y_train)

        predictions = []
        for _, row in df_test.iterrows():
            facts = row_to_facts(row)

            # Advanced Features + Domain Features
            features_df = feat_gen.generate(facts)
            feat_dict = features_df.iloc[0].to_dict()
            domain_feats = _get_domain_features(engine, facts)
            feat_dict.update(domain_feats)
            features_df = pd.DataFrame([feat_dict]).fillna(0)

            for col in X_train.columns:
                if col not in features_df.columns:
                    features_df[col] = 0
            features_df = features_df[X_train.columns]

            proba = ml_model.predict_proba(features_df)[0]
            ml_prob = float(proba[1]) if len(proba) > 1 else float(proba[0])
            pred = 1 if ml_prob >= 0.5 else 0
            predictions.append(pred)

        return np.array(predictions)

    return calculate_metrics_cv(df, predict_fn, n_folds)


def experiment_no_ml(df: pd.DataFrame, n_folds=5) -> Dict:
    """
    تجربة 2: بدون ML Model
    Domain Rules فقط
    """
    from engine.domain_rules_engine import DomainRulesEngine
    engine = DomainRulesEngine()

    def predict_fn(df_test, train_idx=None):
        predictions = []
        for _, row in df_test.iterrows():
            facts = row_to_facts(row)
            result = engine.process_complete_data(facts)
            risk = result.get('insights', {}).get('risk_level', 'Low')
            pred = 1 if risk in ['High', 'Medium'] else 0
            predictions.append(pred)
        return np.array(predictions)

    return calculate_metrics_cv(df, predict_fn, n_folds)


def experiment_no_rules(df: pd.DataFrame, n_folds=5) -> Dict:
    """
    تجربة 3: بدون Domain Rules
    ML Model + Advanced Features فقط
    """
    from sklearn.ensemble import RandomForestClassifier
    from engine.advanced_features import AdvancedFeaturesGenerator

    feat_gen = AdvancedFeaturesGenerator()

    def predict_fn(df_test, train_idx=None):
        # تدريب ML
        train_features = []
        y_train = df.iloc[train_idx]['HeartDisease'].values
        for _, row in df.iloc[train_idx].iterrows():
            facts = row_to_facts(row)
            features = feat_gen.generate(facts)
            train_features.append(features.iloc[0].to_dict())

        X_train = pd.DataFrame(train_features).fillna(0)
        ml_model = RandomForestClassifier(
            n_estimators=200, max_depth=12, min_samples_split=5,
            min_samples_leaf=2, random_state=42, n_jobs=-1
        )
        ml_model.fit(X_train, y_train)

        predictions = []
        for _, row in df_test.iterrows():
            facts = row_to_facts(row)
            features_df = feat_gen.generate(facts)
            features_df = features_df.fillna(0)
            for col in X_train.columns:
                if col not in features_df.columns:
                    features_df[col] = 0
            features_df = features_df[X_train.columns]

            prob = ml_model.predict_proba(features_df)[0]
            pred = 1 if (prob[1] if len(prob) > 1 else prob[0]) >= 0.5 else 0
            predictions.append(pred)

        return np.array(predictions)

    return calculate_metrics_cv(df, predict_fn, n_folds)


def experiment_base_features_only(df: pd.DataFrame, n_folds=5) -> Dict:
    """
    تجربة 4: 12 ميزة أساسية فقط (بدون الميزات المتقدمة)
    """
    from sklearn.ensemble import RandomForestClassifier
    from engine.advanced_features import AdvancedFeaturesGenerator

    feat_gen = AdvancedFeaturesGenerator()

    # 12 ميزة أساسية فقط
    base_feature_names = [
        'age', 'sex_male', 'chest_pain_asy', 'chest_pain_nap',
        'chest_pain_ata', 'resting_bp', 'cholesterol', 'fasting_bs',
        'resting_ecg_st', 'resting_ecg_lvh', 'max_hr', 'exercise_angina',
    ]

    def predict_fn(df_test, train_idx=None):
        # تدريب ML على الميزات الأساسية فقط
        train_features = []
        y_train = df.iloc[train_idx]['HeartDisease'].values
        for _, row in df.iloc[train_idx].iterrows():
            facts = row_to_facts(row)
            features = feat_gen.generate(facts)
            feat_dict = features.iloc[0].to_dict()
            # إبقاء الميزات الأساسية فقط
            base_dict = {k: feat_dict.get(k, 0) for k in base_feature_names}
            train_features.append(base_dict)

        X_train = pd.DataFrame(train_features).fillna(0)
        ml_model = RandomForestClassifier(
            n_estimators=200, max_depth=12, min_samples_split=5,
            min_samples_leaf=2, random_state=42, n_jobs=-1
        )
        ml_model.fit(X_train, y_train)

        predictions = []
        for _, row in df_test.iterrows():
            facts = row_to_facts(row)
            features = feat_gen.generate(facts)
            feat_dict = features.iloc[0].to_dict()
            base_dict = {k: feat_dict.get(k, 0) for k in base_feature_names}
            X_test = pd.DataFrame([base_dict]).fillna(0)

            prob = ml_model.predict_proba(X_test)[0]
            pred = 1 if (prob[1] if len(prob) > 1 else prob[0]) >= 0.5 else 0
            predictions.append(pred)

        return np.array(predictions)

    return calculate_metrics_cv(df, predict_fn, n_folds)


def experiment_no_framingham(df: pd.DataFrame, n_folds=5) -> Dict:
    """
    تجربة 5: بدون Framingham Score
    ML + Domain Rules + Advanced Features (minus Framingham)
    """
    from sklearn.ensemble import RandomForestClassifier
    from engine.domain_rules_engine import DomainRulesEngine
    from engine.advanced_features import AdvancedFeaturesGenerator

    engine = DomainRulesEngine()
    feat_gen = AdvancedFeaturesGenerator()
    framingham_cols = ['framingham_risk_score', 'high_risk_profile']

    def predict_fn(df_test, train_idx=None):
        train_features = []
        y_train = df.iloc[train_idx]['HeartDisease'].values
        for _, row in df.iloc[train_idx].iterrows():
            facts = row_to_facts(row)
            features = feat_gen.generate(facts)
            feat_dict = features.iloc[0].to_dict()
            # إضافة ميزات Domain
            domain_feats = _get_domain_features(engine, facts)
            feat_dict.update(domain_feats)
            # إزالة Framingham
            for col in framingham_cols:
                feat_dict.pop(col, None)
            train_features.append(feat_dict)

        X_train = pd.DataFrame(train_features).fillna(0)
        ml_model = RandomForestClassifier(
            n_estimators=200, max_depth=12, min_samples_split=5,
            min_samples_leaf=2, random_state=42, n_jobs=-1
        )
        ml_model.fit(X_train, y_train)

        predictions = []
        for _, row in df_test.iterrows():
            facts = row_to_facts(row)

            features_df = feat_gen.generate(facts)
            feat_dict = features_df.iloc[0].to_dict()
            domain_feats = _get_domain_features(engine, facts)
            feat_dict.update(domain_feats)
            for col in framingham_cols:
                feat_dict.pop(col, None)
            features_df = pd.DataFrame([feat_dict]).fillna(0)

            for col in X_train.columns:
                if col not in features_df.columns:
                    features_df[col] = 0
            features_df = features_df[X_train.columns]

            proba = ml_model.predict_proba(features_df)[0]
            ml_prob = float(proba[1]) if len(proba) > 1 else float(proba[0])
            pred = 1 if ml_prob >= 0.5 else 0
            predictions.append(pred)

        return np.array(predictions)

    return calculate_metrics_cv(df, predict_fn, n_folds)


def experiment_simple_rules(df: pd.DataFrame, n_folds=5) -> Dict:
    """
    تجربة 6: قواعد IF/ELSE بسيطة (Chatbot العادي)
    5 قواعد بسيطة فقط — بدون ML, بدون ميزات متقدمة
    """
    def predict_fn(df_test, train_idx=None):
        predictions = []
        for _, row in df_test.iterrows():
            facts = row_to_facts(row)
            score = 0

            if facts['Age'] >= 55:
                score += 1
            if facts['Cholesterol'] >= 240:
                score += 1
            bp = str(facts['BloodPressure'])
            if '/' in bp:
                systolic = int(bp.split('/')[0])
                if systolic >= 140:
                    score += 1
            if facts['ChestPain'] in ['ASY', 'TA']:
                score += 1
            if facts['ExerciseAngina'] == 'Y':
                score += 1

            pred = 1 if score >= 3 else 0
            predictions.append(pred)
        return np.array(predictions)

    return calculate_metrics_cv(df, predict_fn, n_folds)


# ═══════════════════════════════════════════════════════
#  التنفيذ الرئيسي
# ═══════════════════════════════════════════════════════

def run_ablation_study():
    """تنفيذ Ablation Study الكامل مع 5-Fold Cross-Validation"""

    print("=" * 70)
    print("  Ablation Study — دراسة إزالة المكونات")
    print("  Heart Disease Risk Assessment System")
    print("  Method: 5-Fold Stratified Cross-Validation")
    print("=" * 70)

    # تحميل البيانات
    df = load_heart_disease_data()
    df = normalize_dataframe(df)

    if 'HeartDisease' not in df.columns:
        print("[!] ERROR: No 'HeartDisease' label column found!")
        return

    y_true = df['HeartDisease'].values
    print(f"\n[+] Dataset: {len(df)} records")
    print(f"    High risk: {sum(y_true)} ({sum(y_true)/len(y_true)*100:.1f}%)")
    print(f"    Low risk:  {len(y_true) - sum(y_true)} ({(len(y_true)-sum(y_true))/len(y_true)*100:.1f}%)")

    # التجارب
    experiments = [
        ("1. Full System (Baseline)", "النظام الكامل", experiment_full_system),
        ("2. Without ML Model", "بدون نموذج ML", experiment_no_ml),
        ("3. Without Domain Rules", "بدون القواعد الطبية", experiment_no_rules),
        ("4. Base Features Only (12)", "12 ميزة أساسية فقط", experiment_base_features_only),
        ("5. Without Framingham Score", "بدون نقاط فرامنغهام", experiment_no_framingham),
        ("6. Simple IF/ELSE (Traditional)", "قواعد بسيطة (تقليدي)", experiment_simple_rules),
    ]

    results = []
    baseline_acc = None

    print(f"\n{'='*70}")
    print(f"  {'Experiment':<35} {'Accuracy':>10} {'F1-Score':>10} {'Drop':>10}")
    print(f"{'='*70}")

    for name, name_ar, func in experiments:
        try:
            print(f"\n[*] Running: {name}...")
            metrics = func(df, n_folds=5)

            if baseline_acc is None:
                baseline_acc = metrics['accuracy']
                drop = 0
            else:
                drop = round(baseline_acc - metrics['accuracy'], 2)

            results.append({
                'experiment': name,
                'experiment_ar': name_ar,
                'metrics': metrics,
                'drop': drop,
            })

            drop_str = "—" if drop == 0 else f"-{drop:.2f}%"
            print(f"  {name:<35} {metrics['accuracy']:>8.2f}% {metrics['f1_score']:>9.2f}% {drop_str:>10}")

        except Exception as e:
            print(f"  [!] ERROR in {name}: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                'experiment': name,
                'experiment_ar': name_ar,
                'metrics': {'accuracy': 0, 'f1_score': 0, 'precision': 0, 'recall': 0,
                            'specificity': 0, 'balanced_accuracy': 0},
                'drop': baseline_acc or 0,
            })

    # ═══════ النتائج التفصيلية ═══════
    print(f"\n{'='*70}")
    print("  DETAILED RESULTS (5-Fold CV Average ± Std)")
    print(f"{'='*70}")

    for r in results:
        m = r['metrics']
        print(f"\n  {r['experiment']}")
        print(f"    Accuracy:    {m['accuracy']:.2f}% ± {m.get('accuracy_std', 0):.2f}%")
        print(f"    F1-Score:    {m['f1_score']:.2f}% ± {m.get('f1_score_std', 0):.2f}%")
        print(f"    Precision:   {m['precision']:.2f}% ± {m.get('precision_std', 0):.2f}%")
        print(f"    Recall:      {m['recall']:.2f}% ± {m.get('recall_std', 0):.2f}%")
        print(f"    Specificity: {m['specificity']:.2f}% ± {m.get('specificity_std', 0):.2f}%")
        if r['drop'] > 0:
            print(f"    Drop:        -{r['drop']:.2f}%")

    # ═══════ حفظ النتائج ═══════
    output = {
        'dataset': {
            'total_records': len(df),
            'high_risk': int(sum(y_true)),
            'low_risk': int(len(y_true) - sum(y_true)),
        },
        'method': '5-Fold Stratified Cross-Validation',
        'experiments': []
    }

    for r in results:
        m = r['metrics']
        exp_data = {
            'name': r['experiment'],
            'name_ar': r['experiment_ar'],
            'accuracy': m['accuracy'],
            'accuracy_std': m.get('accuracy_std', 0),
            'f1_score': m['f1_score'],
            'f1_score_std': m.get('f1_score_std', 0),
            'precision': m['precision'],
            'precision_std': m.get('precision_std', 0),
            'recall': m['recall'],
            'recall_std': m.get('recall_std', 0),
            'specificity': m['specificity'],
            'specificity_std': m.get('specificity_std', 0),
            'drop_from_baseline': r['drop'],
        }
        # إضافة تفاصيل كل fold
        if 'fold_details' in m:
            exp_data['fold_details'] = m['fold_details']
        output['experiments'].append(exp_data)

    output_path = Path(__file__).parent / 'ablation_results.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n[+] Results saved to: {output_path}")

    # ═══════ مساهمة كل مكوّن ═══════
    print(f"\n{'='*70}")
    print("  COMPONENT CONTRIBUTION (sorted by impact)")
    print(f"{'='*70}")

    contributions = [(r['experiment'], r['drop']) for r in results if r['drop'] > 0]
    contributions.sort(key=lambda x: x[1], reverse=True)

    for name, drop in contributions:
        bar = '#' * int(drop)
        print(f"  {name:<35} -{drop:.2f}% {bar}")

    if not contributions:
        print("  (No positive drops — baseline may need more data)")

    print(f"\n{'='*70}")
    print("  CONCLUSION")
    print(f"{'='*70}")
    if baseline_acc and results:
        simple_acc = results[-1]['metrics']['accuracy']
        improvement = baseline_acc - simple_acc
        print(f"  Full system accuracy:      {baseline_acc:.2f}%")
        print(f"  Simple rules accuracy:     {simple_acc:.2f}%")
        print(f"  Improvement over simple:   +{improvement:.2f}%")
        if contributions:
            top = contributions[0]
            print(f"  Most impactful component:  {top[0]} (-{top[1]:.2f}% when removed)")

    return output


if __name__ == '__main__':
    run_ablation_study()
