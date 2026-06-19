

import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging
import pickle
import joblib
import os

logger = logging.getLogger(__name__)


class HeartDiseasePredictor:

    
    def __init__(self, model_path: Optional[str] = None):
        """
        تهيئة المتنبئ
        
        Args:
            model_path: مسار الموديل (اختياري)
        """
        self.model = None
        self.model_type = None
        self.feature_names = []
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            logger.warning("No model provided. Using fallback prediction.")
    
    def load_model(self, model_path: str):
        """
        تحميل الموديل
        
        Args:
            model_path: مسار الموديل
        """
        try:
            # تحديد نوع الموديل من الامتداد
            ext = os.path.splitext(model_path)[1].lower()
            
            if ext in ['.pkl', '.pickle']:
                # scikit-learn pickle
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                self.model_type = 'sklearn'
                logger.info(f"Loaded scikit-learn model from {model_path}")
                
            elif ext == '.joblib':
                # scikit-learn joblib
                self.model = joblib.load(model_path)
                self.model_type = 'sklearn'
                logger.info(f"Loaded scikit-learn model (joblib) from {model_path}")
                
            elif ext in ['.h5', '.keras']:
                # Keras/TensorFlow
                try:
                    from tensorflow import keras
                    # Load with safe_mode=False to allow Lambda layers
                    self.model = keras.models.load_model(model_path, safe_mode=False)
                    self.model_type = 'keras'
                    logger.info(f"Loaded Keras model from {model_path}")
                except ImportError:
                    logger.error("TensorFlow/Keras not installed. Cannot load .h5/.keras model")
                except Exception as e:
                    logger.error(f"Failed to load Keras model (CPU may lack AVX support): {e}")
                    
            elif ext in ['.pt', '.pth']:
                # PyTorch
                try:
                    import torch
                    self.model = torch.load(model_path)
                    self.model_type = 'pytorch'
                    logger.info(f"Loaded PyTorch model from {model_path}")
                except ImportError:
                    logger.error("PyTorch not installed. Cannot load .pt/.pth model")
            
            else:
                logger.error(f"Unsupported model format: {ext}")
                
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None
    
    def predict(self, features: pd.DataFrame) -> Dict:
        """
        التنبؤ بحالة القلب
        
        Args:
            features: DataFrame الـ features المتقدمة
            
        Returns:
            Dictionary يحتوي على:
            - probability: احتمالية المرض (0-1)
            - prediction: التنبؤ ('Positive' أو 'Negative')
            - confidence: الثقة (0-1)
            - risk_level: مستوى الخطر ('LOW', 'MODERATE', 'HIGH', 'CRITICAL')
        """
        if self.model is None:
            # Fallback: استخدام قاعدة بسيطة
            return self._fallback_prediction(features)
        
        try:
            # التنبؤ بناءً على نوع الموديل
            if self.model_type == 'sklearn':
                return self._predict_sklearn(features)
            elif self.model_type == 'keras':
                return self._predict_keras(features)
            elif self.model_type == 'pytorch':
                return self._predict_pytorch(features)
            else:
                return self._fallback_prediction(features)
                
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return self._fallback_prediction(features)
    
    def _predict_sklearn(self, features: pd.DataFrame) -> Dict:
        """التنبؤ باستخدام scikit-learn model"""
        # التنبؤ
        if hasattr(self.model, 'predict_proba'):
            # موديل يدعم predict_proba (مثل Random Forest, Logistic Regression)
            proba = self.model.predict_proba(features)
            probability = float(proba[0][1])  # احتمالية الصنف الإيجابي
        else:
            # موديل بدون predict_proba (مثل SVM بدون probability=True)
            pred = self.model.predict(features)
            probability = float(pred[0])
        
        # التنبؤ النهائي
        prediction = 'Positive' if probability > 0.5 else 'Negative'
        
        # الثقة
        confidence = max(probability, 1 - probability)
        
        # مستوى الخطر
        risk_level = self._get_risk_level(probability)
        
        return {
            'probability': probability,
            'prediction': prediction,
            'confidence': confidence,
            'risk_level': risk_level,
            'source': 'ML Model (scikit-learn)'
        }
    
    def _predict_keras(self, features: pd.DataFrame) -> Dict:
        """التنبؤ باستخدام Keras model"""
        # تحويل لـ numpy array
        X = features.values
        
        # التنبؤ
        prediction = self.model.predict(X, verbose=0)
        probability = float(prediction[0][0])
        
        # التنبؤ النهائي
        pred_class = 'Positive' if probability > 0.5 else 'Negative'
        
        # الثقة
        confidence = max(probability, 1 - probability)
        
        # مستوى الخطر
        risk_level = self._get_risk_level(probability)
        
        return {
            'probability': probability,
            'prediction': pred_class,
            'confidence': confidence,
            'risk_level': risk_level,
            'source': 'ML Model (Keras/TensorFlow)'
        }
    
    def _predict_pytorch(self, features: pd.DataFrame) -> Dict:
        """التنبؤ باستخدام PyTorch model"""
        import torch
        
        # تحويل لـ tensor
        X = torch.tensor(features.values, dtype=torch.float32)
        
        # التنبؤ
        self.model.eval()
        with torch.no_grad():
            output = self.model(X)
            probability = float(torch.sigmoid(output)[0])
        
        # التنبؤ النهائي
        prediction = 'Positive' if probability > 0.5 else 'Negative'
        
        # الثقة
        confidence = max(probability, 1 - probability)
        
        # مستوى الخطر
        risk_level = self._get_risk_level(probability)
        
        return {
            'probability': probability,
            'prediction': prediction,
            'confidence': confidence,
            'risk_level': risk_level,
            'source': 'ML Model (PyTorch)'
        }
    
    def _fallback_prediction(self, features: pd.DataFrame) -> Dict:
        """
        Fallback prediction باستخدام قاعدة بسيطة
        (في حالة عدم وجود موديل)
        """
        # حساب نقاط الخطر من الـ features
        risk_score = 0
        
        # Age risk
        if 'age_senior' in features.columns and features['age_senior'].iloc[0] == 1:
            risk_score += 2
        elif 'age_elderly' in features.columns and features['age_elderly'].iloc[0] == 1:
            risk_score += 3
        
        # Cholesterol
        if 'cholesterol_high' in features.columns and features['cholesterol_high'].iloc[0] == 1:
            risk_score += 2
        elif 'cholesterol_very_high' in features.columns and features['cholesterol_very_high'].iloc[0] == 1:
            risk_score += 3
        
        # BP
        if 'bp_stage2' in features.columns and features['bp_stage2'].iloc[0] == 1:
            risk_score += 2
        elif 'bp_crisis' in features.columns and features['bp_crisis'].iloc[0] == 1:
            risk_score += 3
        
        # Framingham
        if 'high_risk_profile' in features.columns and features['high_risk_profile'].iloc[0] == 1:
            risk_score += 2
        
        # ST depression
        if 'st_severe' in features.columns and features['st_severe'].iloc[0] == 1:
            risk_score += 2
        
        # تحويل النقاط لاحتمالية (0-1)
        probability = min(risk_score / 10.0, 0.99)
        
        # التنبؤ
        prediction = 'Positive' if probability > 0.5 else 'Negative'
        
        # الثقة
        confidence = max(probability, 1 - probability)
        
        # مستوى الخطر
        risk_level = self._get_risk_level(probability)
        
        logger.warning("Using FALLBACK prediction — ML model not available!")
        return {
            'probability': probability,
            'prediction': prediction,
            'confidence': confidence,
            'risk_level': risk_level,
            'source': 'Fallback Rule-Based',
            'warning': 'ML model unavailable. This prediction uses simplified rules and may be unreliable.'
        }
    
    def _get_risk_level(self, probability: float) -> str:
        """
        تحديد مستوى الخطر من الاحتمالية
        
        Args:
            probability: احتمالية المرض (0-1)
            
        Returns:
            مستوى الخطر
        """
        if probability >= 0.8:
            return 'CRITICAL'
        elif probability >= 0.6:
            return 'HIGH'
        elif probability >= 0.4:
            return 'MODERATE'
        else:
            return 'LOW'


# Create singleton instance with model
import os as _os

def _create_predictor():
    """Safely create the predictor, catching TensorFlow DLL crashes."""
    _model_path = _os.path.join(_os.path.dirname(__file__), '..', 'models', 'heart_disease_model.keras')
    try:
        if _os.path.exists(_model_path):
            predictor = HeartDiseasePredictor(model_path=_model_path)
            if predictor.model is None:
                logger.warning(
                    f"Model file exists at {_model_path} but failed to load. "
                    "Using fallback prediction."
                )
            else:
                logger.info(f"DL Predictor initialized with model: {_model_path}")
            return predictor
        else:
            logger.warning(
                f"Model file not found at {_model_path}. "
                "Using fallback prediction."
            )
            return HeartDiseasePredictor()
    except Exception as e:
        logger.error(f"Error creating predictor: {e}. Using fallback.")
        return HeartDiseasePredictor()

ml_predictor = _create_predictor()
