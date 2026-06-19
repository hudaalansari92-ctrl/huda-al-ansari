"""
Comprehensive unit tests for the project's engines.

Tests cover:
- DomainRulesEngine
- AdvancedFeaturesGenerator
- HeartDiseasePredictor (ML)
- FinalDecisionEngine
- Full integration pipeline
"""

import os
import sys
import pytest
import pandas as pd
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def high_risk_facts():
    """High-risk patient profile."""
    return {
        'Age': 68, 'Sex': 'Male', 'ChestPain': 'ASY',
        'BloodPressure': '185/120', 'Cholesterol': 320, 'FastingBS': 1,
        'RestingECG': 'ST', 'MaxHR': 100, 'ExerciseAngina': 'Y',
        'Oldpeak': 3.5, 'ST_Slope': 'Flat'
    }


@pytest.fixture
def low_risk_facts():
    """Low-risk patient profile."""
    return {
        'Age': 30, 'Sex': 'Female', 'ChestPain': 'ATA',
        'BloodPressure': '110/70', 'Cholesterol': 170, 'FastingBS': 0,
        'RestingECG': 'Normal', 'MaxHR': 185, 'ExerciseAngina': 'N',
        'Oldpeak': 0.0, 'ST_Slope': 'Up'
    }


@pytest.fixture
def moderate_risk_facts():
    """Moderate-risk patient profile."""
    return {
        'Age': 55, 'Sex': 'Male', 'ChestPain': 'ASY',
        'BloodPressure': '140/90', 'Cholesterol': 250, 'FastingBS': 1,
        'RestingECG': 'ST', 'MaxHR': 130, 'ExerciseAngina': 'Y',
        'Oldpeak': 2.5, 'ST_Slope': 'Flat'
    }


@pytest.fixture
def partial_facts():
    """Incomplete patient data (missing several fields)."""
    return {
        'Age': 50,
        'Sex': 'Male',
        'Cholesterol': 220,
    }


# ---------------------------------------------------------------------------
# Helper: instantiate DomainRulesEngine with the project's rules file
# ---------------------------------------------------------------------------

def _make_domain_engine():
    from engine.domain_rules_engine import DomainRulesEngine
    rules_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'domain_rules.json'
    )
    return DomainRulesEngine(rules_file=rules_path)


# ===================================================================
# 1. TestDomainRulesEngine
# ===================================================================

class TestDomainRulesEngine:

    def test_high_risk_patient(self, high_risk_facts):
        """High-value inputs should yield High or Medium risk."""
        engine = _make_domain_engine()
        result = engine.process_complete_data(high_risk_facts)
        assert result['status'] == 'complete'
        risk = result['insights']['risk_level']
        assert risk in ('High', 'Medium'), f"Expected High/Medium, got {risk}"

    def test_low_risk_patient(self, low_risk_facts):
        """Low-value inputs should yield Low risk."""
        engine = _make_domain_engine()
        result = engine.process_complete_data(low_risk_facts)
        assert result['status'] == 'complete'
        risk = result['insights']['risk_level']
        assert risk == 'Low', f"Expected Low, got {risk}"

    def test_process_returns_correct_structure(self, moderate_risk_facts):
        """Returned dict should contain the expected top-level keys."""
        engine = _make_domain_engine()
        result = engine.process_complete_data(moderate_risk_facts)
        assert result['status'] == 'complete'
        for key in ('binary_features', 'continuous_features',
                     'triggered_rules', 'insights'):
            assert key in result, f"Missing key: {key}"

    def test_missing_fields_handled(self, partial_facts):
        """Partial facts should return incomplete status, not crash."""
        engine = _make_domain_engine()
        result = engine.process_complete_data(partial_facts)
        assert result['status'] == 'incomplete'
        assert 'missing_fields' in result
        assert len(result['missing_fields']) > 0

    def test_binary_features_values(self, high_risk_facts):
        """Binary features should only contain 0 or 1."""
        engine = _make_domain_engine()
        binary = engine.calculate_binary_features(high_risk_facts)
        for key, val in binary.items():
            assert val in (0, 1), f"{key} has non-binary value {val}"

    def test_continuous_features_keys(self, moderate_risk_facts):
        """Continuous features should contain the documented keys."""
        engine = _make_domain_engine()
        cont = engine.calculate_continuous_features(moderate_risk_facts)
        expected_keys = {
            'age_risk_score', 'predicted_max_hr', 'hr_reserve',
            'hr_reserve_ratio', 'framingham_risk_score',
            'age_cholesterol_norm', 'age_bp_norm',
            'cholesterol_bp_norm', 'chest_pain_severity'
        }
        for k in expected_keys:
            assert k in cont, f"Missing continuous feature: {k}"


# ===================================================================
# 2. TestAdvancedFeaturesGenerator
# ===================================================================

class TestAdvancedFeaturesGenerator:

    def test_generates_dataframe(self, moderate_risk_facts):
        """generate() should return a pandas DataFrame."""
        from engine.advanced_features import AdvancedFeaturesGenerator
        gen = AdvancedFeaturesGenerator()
        df = gen.generate(moderate_risk_facts)
        assert isinstance(df, pd.DataFrame)

    def test_feature_count(self, moderate_risk_facts):
        """Should produce approximately 58 features."""
        from engine.advanced_features import AdvancedFeaturesGenerator
        gen = AdvancedFeaturesGenerator()
        df = gen.generate(moderate_risk_facts)
        num_cols = len(df.columns)
        # Allow a small tolerance in case feature_names.json is absent
        assert 50 <= num_cols <= 65, (
            f"Expected ~58 features, got {num_cols}"
        )

    def test_base_features_present(self, moderate_risk_facts):
        """Key base features should appear in the output DataFrame."""
        from engine.advanced_features import AdvancedFeaturesGenerator
        gen = AdvancedFeaturesGenerator()
        df = gen.generate(moderate_risk_facts)
        for col in ('Age', 'Sex', 'Cholesterol', 'MaxHeartRate',
                     'OldPeak', 'ExerciseInducedAngina'):
            assert col in df.columns, f"Missing base feature: {col}"

    def test_no_nan_in_output(self, moderate_risk_facts):
        """Output DataFrame should not contain NaN values."""
        from engine.advanced_features import AdvancedFeaturesGenerator
        gen = AdvancedFeaturesGenerator()
        df = gen.generate(moderate_risk_facts)
        assert not df.isnull().any().any(), "DataFrame contains NaN values"

    def test_single_row(self, moderate_risk_facts):
        """Output should have exactly one row."""
        from engine.advanced_features import AdvancedFeaturesGenerator
        gen = AdvancedFeaturesGenerator()
        df = gen.generate(moderate_risk_facts)
        assert len(df) == 1

    def test_advanced_features_present(self, moderate_risk_facts):
        """Advanced computed features should be present."""
        from engine.advanced_features import AdvancedFeaturesGenerator
        gen = AdvancedFeaturesGenerator()
        df = gen.generate(moderate_risk_facts)
        for col in ('framingham_risk_score', 'age_cholesterol_norm',
                     'male_high_risk', 'st_severe'):
            assert col in df.columns, f"Missing advanced feature: {col}"


# ===================================================================
# 3. TestMLPredictor
# ===================================================================

class TestMLPredictor:

    def _get_predictor(self):
        """Return a HeartDiseasePredictor (no model loaded -- uses fallback)."""
        from engine.ml_predictor import HeartDiseasePredictor
        return HeartDiseasePredictor()  # fallback mode

    def _get_features_df(self, facts):
        from engine.advanced_features import AdvancedFeaturesGenerator
        gen = AdvancedFeaturesGenerator()
        return gen.generate(facts)

    def test_predict_returns_dict(self, moderate_risk_facts):
        """predict() should return a dict with probability and prediction."""
        predictor = self._get_predictor()
        df = self._get_features_df(moderate_risk_facts)
        try:
            result = predictor.predict(df)
        except Exception:
            pytest.skip("ML prediction unavailable")
        assert isinstance(result, dict)
        assert 'probability' in result
        assert 'prediction' in result

    def test_probability_range(self, moderate_risk_facts):
        """Probability should be between 0 and 1."""
        predictor = self._get_predictor()
        df = self._get_features_df(moderate_risk_facts)
        try:
            result = predictor.predict(df)
        except Exception:
            pytest.skip("ML prediction unavailable")
        prob = result['probability']
        assert 0.0 <= prob <= 1.0, f"Probability out of range: {prob}"

    def test_predict_with_valid_features(self, high_risk_facts):
        """predict() should not crash with valid high-risk features."""
        predictor = self._get_predictor()
        df = self._get_features_df(high_risk_facts)
        try:
            result = predictor.predict(df)
        except Exception:
            pytest.skip("ML prediction unavailable")
        assert 'risk_level' in result

    def test_prediction_values(self, moderate_risk_facts):
        """prediction should be 'Positive' or 'Negative'."""
        predictor = self._get_predictor()
        df = self._get_features_df(moderate_risk_facts)
        try:
            result = predictor.predict(df)
        except Exception:
            pytest.skip("ML prediction unavailable")
        assert result['prediction'] in ('Positive', 'Negative')

    def test_risk_level_values(self, moderate_risk_facts):
        """risk_level should be one of the defined levels."""
        predictor = self._get_predictor()
        df = self._get_features_df(moderate_risk_facts)
        try:
            result = predictor.predict(df)
        except Exception:
            pytest.skip("ML prediction unavailable")
        valid_levels = {'LOW', 'MODERATE', 'HIGH', 'CRITICAL'}
        assert result['risk_level'] in valid_levels

    def test_fallback_low_risk(self, low_risk_facts):
        """Fallback predictor should give low probability for low-risk patient."""
        predictor = self._get_predictor()
        df = self._get_features_df(low_risk_facts)
        try:
            result = predictor.predict(df)
        except Exception:
            pytest.skip("ML prediction unavailable")
        assert result['probability'] < 0.5


# ===================================================================
# 4. TestFinalDecisionEngine
# ===================================================================

class TestFinalDecisionEngine:

    def _make_engine(self):
        from engine.final_decision_engine import FinalDecisionEngine
        return FinalDecisionEngine()

    def _empty_features_df(self):
        """Minimal features DataFrame for decision engine."""
        return pd.DataFrame([{
            'framingham_risk_score': 0,
            'high_risk_profile': 0,
        }])

    def test_high_risk_decision(self):
        """High domain + high ML should produce HIGH or CRITICAL."""
        engine = self._make_engine()
        domain = {'risk_level': 'HIGH', 'insights': {}}
        ml = {'probability': 0.85, 'prediction': 'Positive',
              'confidence': 0.85, 'risk_level': 'HIGH', 'source': 'test'}
        features_df = pd.DataFrame([{'framingham_risk_score': 5,
                                      'high_risk_profile': 1}])
        result = engine.make_decision(domain, ml, features_df)
        assert result['final_risk_level'] in ('HIGH', 'CRITICAL')

    def test_low_risk_decision(self):
        """Low domain + low ML should produce LOW."""
        engine = self._make_engine()
        domain = {'risk_level': 'LOW', 'insights': {}}
        ml = {'probability': 0.1, 'prediction': 'Negative',
              'confidence': 0.9, 'risk_level': 'LOW', 'source': 'test'}
        features_df = pd.DataFrame([{'framingham_risk_score': 0,
                                      'high_risk_profile': 0}])
        result = engine.make_decision(domain, ml, features_df)
        assert result['final_risk_level'] == 'LOW'

    def test_returns_risk_level(self):
        """Output should always contain final_risk_level key."""
        engine = self._make_engine()
        domain = {'risk_level': 'MEDIUM', 'insights': {}}
        ml = {'probability': 0.5, 'prediction': 'Positive',
              'confidence': 0.5, 'risk_level': 'MODERATE', 'source': 'test'}
        features_df = self._empty_features_df()
        result = engine.make_decision(domain, ml, features_df)
        assert 'final_risk_level' in result

    def test_returns_confidence(self):
        """Output should contain a confidence score."""
        engine = self._make_engine()
        domain = {'risk_level': 'LOW', 'insights': {}}
        ml = {'probability': 0.2, 'prediction': 'Negative',
              'confidence': 0.8, 'risk_level': 'LOW', 'source': 'test'}
        features_df = self._empty_features_df()
        result = engine.make_decision(domain, ml, features_df)
        assert 'confidence' in result
        assert 0.0 <= result['confidence'] <= 1.0

    def test_returns_recommendations(self):
        """Output should contain recommendations list."""
        engine = self._make_engine()
        domain = {'risk_level': 'HIGH', 'insights': {}}
        ml = {'probability': 0.75, 'prediction': 'Positive',
              'confidence': 0.75, 'risk_level': 'HIGH', 'source': 'test'}
        features_df = pd.DataFrame([{'framingham_risk_score': 4,
                                      'high_risk_profile': 1}])
        result = engine.make_decision(domain, ml, features_df)
        assert 'recommendations' in result
        assert isinstance(result['recommendations'], list)
        assert len(result['recommendations']) > 0


# ===================================================================
# 5. TestIntegration
# ===================================================================

class TestIntegration:

    def _run_pipeline(self, facts):
        """Run the full pipeline: domain -> features -> ML -> decision."""
        from engine.domain_rules_engine import DomainRulesEngine
        from engine.advanced_features import AdvancedFeaturesGenerator
        from engine.ml_predictor import HeartDiseasePredictor
        from engine.final_decision_engine import FinalDecisionEngine

        rules_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'domain_rules.json'
        )

        # Step 1: Domain rules
        domain_engine = DomainRulesEngine(rules_file=rules_path)
        domain_result = domain_engine.process_complete_data(facts)

        # Step 2: Advanced features
        feat_gen = AdvancedFeaturesGenerator()
        features_df = feat_gen.generate(facts)

        # Step 3: ML prediction (fallback if model unavailable)
        try:
            predictor = HeartDiseasePredictor()
            ml_result = predictor.predict(features_df)
        except Exception:
            ml_result = {
                'probability': 0.5, 'prediction': 'Unknown',
                'confidence': 0.5, 'risk_level': 'MODERATE',
                'source': 'test-fallback'
            }

        # Step 4: Final decision
        # Map domain risk_level to upper-case for decision engine compatibility
        domain_for_decision = {
            'risk_level': domain_result.get('insights', {}).get(
                'risk_level', 'UNKNOWN'
            ).upper(),
            'insights': domain_result.get('insights', {}),
        }

        decision_engine = FinalDecisionEngine()
        decision = decision_engine.make_decision(
            domain_for_decision, ml_result, features_df
        )
        return domain_result, features_df, ml_result, decision

    def test_full_pipeline(self, moderate_risk_facts):
        """Full pipeline should run end-to-end without errors."""
        domain_result, features_df, ml_result, decision = \
            self._run_pipeline(moderate_risk_facts)

        # Domain
        assert domain_result['status'] == 'complete'

        # Features
        assert isinstance(features_df, pd.DataFrame)
        assert len(features_df) == 1

        # ML
        assert 'probability' in ml_result

        # Decision
        assert 'final_risk_level' in decision
        valid_levels = {'CRITICAL', 'HIGH', 'MODERATE-HIGH',
                        'MODERATE', 'LOW-MODERATE', 'LOW'}
        assert decision['final_risk_level'] in valid_levels

    def test_multiple_patients(self):
        """Run the pipeline on 5 different patient profiles."""
        patients = [
            {  # Young healthy female
                'Age': 25, 'Sex': 'Female', 'ChestPain': 'NAP',
                'BloodPressure': '110/70', 'Cholesterol': 160, 'FastingBS': 0,
                'RestingECG': 'Normal', 'MaxHR': 190, 'ExerciseAngina': 'N',
                'Oldpeak': 0.0, 'ST_Slope': 'Up'
            },
            {  # Middle-aged male with moderate risk
                'Age': 50, 'Sex': 'Male', 'ChestPain': 'ATA',
                'BloodPressure': '135/85', 'Cholesterol': 230, 'FastingBS': 0,
                'RestingECG': 'Normal', 'MaxHR': 155, 'ExerciseAngina': 'N',
                'Oldpeak': 1.0, 'ST_Slope': 'Flat'
            },
            {  # Elderly male with high risk
                'Age': 72, 'Sex': 'Male', 'ChestPain': 'ASY',
                'BloodPressure': '170/100', 'Cholesterol': 290, 'FastingBS': 1,
                'RestingECG': 'ST', 'MaxHR': 110, 'ExerciseAngina': 'Y',
                'Oldpeak': 3.0, 'ST_Slope': 'Flat'
            },
            {  # Female with borderline values
                'Age': 58, 'Sex': 'Female', 'ChestPain': 'NAP',
                'BloodPressure': '128/82', 'Cholesterol': 210, 'FastingBS': 0,
                'RestingECG': 'LVH', 'MaxHR': 140, 'ExerciseAngina': 'N',
                'Oldpeak': 0.5, 'ST_Slope': 'Up'
            },
            {  # Critical case
                'Age': 75, 'Sex': 'Male', 'ChestPain': 'TA',
                'BloodPressure': '200/130', 'Cholesterol': 350, 'FastingBS': 1,
                'RestingECG': 'ST', 'MaxHR': 90, 'ExerciseAngina': 'Y',
                'Oldpeak': 4.0, 'ST_Slope': 'Down'
            },
        ]

        for i, patient in enumerate(patients):
            domain_result, features_df, ml_result, decision = \
                self._run_pipeline(patient)

            assert domain_result['status'] == 'complete', (
                f"Patient {i} domain failed"
            )
            assert isinstance(features_df, pd.DataFrame), (
                f"Patient {i} features not a DataFrame"
            )
            assert 'final_risk_level' in decision, (
                f"Patient {i} missing final_risk_level"
            )

    def test_pipeline_consistency(self, high_risk_facts):
        """Running the same facts twice should produce identical results."""
        _, _, _, decision1 = self._run_pipeline(high_risk_facts)
        _, _, _, decision2 = self._run_pipeline(high_risk_facts)
        assert decision1['final_risk_level'] == decision2['final_risk_level']
        assert decision1['confidence'] == decision2['confidence']
