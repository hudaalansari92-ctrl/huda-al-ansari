
import pandas as pd
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class FinalDecisionEngine:
    """
    محرك القرار النهائي
    
    يدمج:
    1. Domain Rules Analysis (القواعد الطبية)
    2. ML Model Prediction (التنبؤ بالموديل)
    3. Advanced Features (الخصائص المتقدمة)
    
    باستخدام Rule-Based Decision Tree
    """
    
    def __init__(self):
        """تهيئة المحرك"""
        self.decision_tree_rules = self._initialize_decision_tree()
        logger.info("FinalDecisionEngine initialized")
    
    def _initialize_decision_tree(self) -> List[Dict]:
        """
        تهيئة قواعد Decision Tree
        
        Returns:
            قائمة القواعد مرتبة حسب الأولوية
        """
        return [
            # Rule 1: CRITICAL - ML very high + Domain high
            {
                'condition': lambda domain, ml: (
                    ml['probability'] >= 0.9 and 
                    domain.get('risk_level') in ['HIGH', 'CRITICAL']
                ),
                'decision': 'CRITICAL',
                'confidence': 0.95,
                'reasoning_en': 'Both ML model and domain rules indicate critical risk',
                'reasoning_ar': 'كل من الموديل والقواعد الطبية تشير لخطر حرج'
            },
            
            # Rule 2: CRITICAL - ML critical regardless of domain
            {
                'condition': lambda domain, ml: ml['probability'] >= 0.95,
                'decision': 'CRITICAL',
                'confidence': 0.90,
                'reasoning_en': 'ML model shows critical probability (≥95%)',
                'reasoning_ar': 'الموديل يشير لاحتمالية حرجة (≥95%)'
            },
            
            # Rule 3: HIGH - ML high + Domain high
            {
                'condition': lambda domain, ml: (
                    ml['probability'] >= 0.7 and 
                    domain.get('risk_level') in ['HIGH', 'CRITICAL']
                ),
                'decision': 'HIGH',
                'confidence': 0.85,
                'reasoning_en': 'Both ML and domain analysis show high risk',
                'reasoning_ar': 'كل من الموديل والتحليل الطبي يشيران لخطر عالي'
            },
            
            # Rule 4: HIGH - ML high + Framingham high
            {
                'condition': lambda domain, ml, features: (
                    ml['probability'] >= 0.7 and 
                    features.get('framingham_risk_score', 0) >= 4
                ),
                'decision': 'HIGH',
                'confidence': 0.80,
                'reasoning_en': 'High ML probability with elevated Framingham score',
                'reasoning_ar': 'احتمالية عالية من الموديل مع نقاط فرامنغهام مرتفعة'
            },
            
            # Rule 5: HIGH - Domain critical regardless of ML
            {
                'condition': lambda domain, ml: domain.get('risk_level') == 'CRITICAL',
                'decision': 'HIGH',
                'confidence': 0.75,
                'reasoning_en': 'Domain rules indicate critical risk patterns',
                'reasoning_ar': 'القواعد الطبية تشير لأنماط خطر حرجة'
            },
            
            # Rule 6: MODERATE-HIGH - ML moderate + Domain high
            {
                'condition': lambda domain, ml: (
                    0.5 <= ml['probability'] < 0.7 and 
                    domain.get('risk_level') in ['HIGH', 'CRITICAL']
                ),
                'decision': 'MODERATE-HIGH',
                'confidence': 0.70,
                'reasoning_en': 'Moderate ML risk but high domain risk',
                'reasoning_ar': 'خطر متوسط من الموديل لكن عالي من القواعد'
            },
            
            # Rule 7: MODERATE-HIGH - ML high + Domain moderate
            {
                'condition': lambda domain, ml: (
                    ml['probability'] >= 0.7 and 
                    domain.get('risk_level') == 'MEDIUM'
                ),
                'decision': 'MODERATE-HIGH',
                'confidence': 0.70,
                'reasoning_en': 'High ML probability despite moderate domain risk',
                'reasoning_ar': 'احتمالية عالية من الموديل رغم خطر متوسط من القواعد'
            },
            
            # Rule 8: MODERATE - Both moderate
            {
                'condition': lambda domain, ml: (
                    0.4 <= ml['probability'] < 0.7 and 
                    domain.get('risk_level') in ['MEDIUM', 'MODERATE']
                ),
                'decision': 'MODERATE',
                'confidence': 0.65,
                'reasoning_en': 'Both sources indicate moderate risk',
                'reasoning_ar': 'كلا المصدرين يشيران لخطر متوسط'
            },
            
            # Rule 9: LOW-MODERATE - ML low + Domain moderate
            {
                'condition': lambda domain, ml: (
                    ml['probability'] < 0.4 and 
                    domain.get('risk_level') in ['MEDIUM', 'HIGH']
                ),
                'decision': 'LOW-MODERATE',
                'confidence': 0.60,
                'reasoning_en': 'Domain shows concern but ML probability is low',
                'reasoning_ar': 'القواعد تُظهر قلقاً لكن احتمالية الموديل منخفضة'
            },
            
            # Rule 10: LOW - Both low
            {
                'condition': lambda domain, ml: (
                    ml['probability'] < 0.3 and 
                    domain.get('risk_level') in ['LOW', 'UNKNOWN']
                ),
                'decision': 'LOW',
                'confidence': 0.80,
                'reasoning_en': 'Both ML and domain analysis show low risk',
                'reasoning_ar': 'كل من الموديل والتحليل الطبي يشيران لخطر منخفض'
            },
            
            # Default rule
            {
                'condition': lambda domain, ml: True,
                'decision': 'MODERATE',
                'confidence': 0.50,
                'reasoning_en': 'Default moderate risk assessment',
                'reasoning_ar': 'تقييم خطر متوسط افتراضي'
            }
        ]
    
    def make_decision(self,
                     domain_assessment: Dict,
                     ml_prediction: Dict,
                     advanced_features: pd.DataFrame) -> Dict:
        """
        اتخاذ القرار النهائي باستخدام Decision Tree
        
        Args:
            domain_assessment: نتيجة Domain Rules Analysis
            ml_prediction: نتيجة ML Model Prediction
            advanced_features: الخصائص المتقدمة
            
        Returns:
            القرار النهائي
        """
        logger.info("Making final decision using Rule-Based Decision Tree")
        
        # استخراج معلومات مهمة
        features_dict = advanced_features.iloc[0].to_dict() if not advanced_features.empty else {}
        
        # تطبيق Decision Tree Rules
        for rule in self.decision_tree_rules:
            try:
                # تحقق من الشرط
                condition = rule['condition']
                
                # تمرير المعاملات المناسبة
                import inspect
                sig = inspect.signature(condition)
                params = list(sig.parameters.keys())
                
                if len(params) == 2:
                    # domain, ml فقط
                    if condition(domain_assessment, ml_prediction):
                        return self._build_decision(rule, domain_assessment, ml_prediction, features_dict)
                elif len(params) == 3:
                    # domain, ml, features
                    if condition(domain_assessment, ml_prediction, features_dict):
                        return self._build_decision(rule, domain_assessment, ml_prediction, features_dict)
                        
            except Exception as e:
                logger.warning(f"Error evaluating rule: {e}")
                continue
        
        # لن نصل هنا أبداً (القاعدة الافتراضية موجودة)
        return self._build_default_decision()
    
    def _build_decision(self,
                       rule: Dict,
                       domain_assessment: Dict,
                       ml_prediction: Dict,
                       features_dict: Dict) -> Dict:
        """
        بناء القرار النهائي
        
        Args:
            rule: القاعدة المُطبقة
            domain_assessment: تقييم القواعد
            ml_prediction: تنبؤ الموديل
            features_dict: الخصائص
            
        Returns:
            القرار الكامل
        """
        decision = {
            # القرار النهائي
            'final_risk_level': rule['decision'],
            'final_risk_level_ar': self._translate_risk_level(rule['decision']),
            'confidence': rule['confidence'],
            
            # التفسير
            'reasoning_en': rule['reasoning_en'],
            'reasoning_ar': rule['reasoning_ar'],
            
            # المصادر
            # NOTE: the domain engine puts risk_level inside
            # domain_assessment['insights'], not at the top level — read it
            # from insights first, fall back to the top level for backward
            # compatibility, and normalise to upper-case.
            'sources': {
                'domain_rules': {
                    'risk_level': str(
                        domain_assessment.get('insights', {}).get('risk_level')
                        or domain_assessment.get('risk_level')
                        or 'UNKNOWN'
                    ).upper(),
                    'triggered_rules': domain_assessment.get('insights', {}).get('triggered_rules_count', 0),
                    'framingham_score': features_dict.get('framingham_risk_score', 0)
                },
                'ml_model': {
                    'probability': ml_prediction.get('probability', 0.0),
                    'prediction': ml_prediction.get('prediction', 'Unknown'),
                    'confidence': ml_prediction.get('confidence', 0.0),
                    'source': ml_prediction.get('source', 'Unknown')
                }
            },
            
            # التوصيات المُجمعة
            'recommendations': self._generate_recommendations(
                rule['decision'],
                domain_assessment,
                ml_prediction
            ),
            
            # معلومات إضافية
            'metadata': {
                'decision_rule': rule['reasoning_en'],
                'domain_risk': str(
                    domain_assessment.get('insights', {}).get('risk_level')
                    or domain_assessment.get('risk_level')
                    or 'UNKNOWN'
                ).upper(),
                'ml_risk': ml_prediction.get('risk_level', 'UNKNOWN'),
                'ml_probability': ml_prediction.get('probability', 0.0),
                # Full list of triggered domain rules so the UI can show
                # the complete N/48 breakdown (sorted by weight in the
                # engine), not just the top 5.
                'triggered_rules': domain_assessment.get('triggered_rules', []),
            }
        }
        
        return decision
    
    def _build_default_decision(self) -> Dict:
        """بناء قرار افتراضي في حالة الفشل"""
        return {
            'final_risk_level': 'MODERATE',
            'final_risk_level_ar': 'متوسط',
            'confidence': 0.50,
            'reasoning_en': 'Unable to determine precise risk level',
            'reasoning_ar': 'غير قادر على تحديد مستوى الخطر بدقة',
            'sources': {},
            'recommendations': ['Consult with healthcare professional'],
            'metadata': {}
        }
    
    def _translate_risk_level(self, risk_level: str) -> str:
        """ترجمة مستوى الخطر للعربية"""
        translations = {
            'CRITICAL': 'حرج',
            'HIGH': 'عالي',
            'MODERATE-HIGH': 'متوسط-عالي',
            'MODERATE': 'متوسط',
            'LOW-MODERATE': 'منخفض-متوسط',
            'LOW': 'منخفض',
            'UNKNOWN': 'غير معروف'
        }
        return translations.get(risk_level, risk_level)
    
    def _generate_recommendations(self,
                                 risk_level: str,
                                 domain_assessment: Dict,
                                 ml_prediction: Dict) -> List[str]:
        """
        توليد توصيات بناءً على مستوى الخطر
        
        Args:
            risk_level: مستوى الخطر النهائي
            domain_assessment: تقييم القواعد
            ml_prediction: تنبؤ الموديل
            
        Returns:
            قائمة التوصيات
        """
        recommendations = []
        
        # توصيات حسب مستوى الخطر
        if risk_level == 'CRITICAL':
            recommendations.extend([
                'URGENT: Immediate cardiac evaluation required',
                'Emergency room visit recommended',
                'Contact cardiologist immediately',
                'Medication review may be needed'
            ])
        elif risk_level == 'HIGH':
            recommendations.extend([
                'Schedule cardiac evaluation within 1-2 weeks',
                'Comprehensive cardiac workup recommended',
                'ECG and stress test needed',
                'Discuss medication with physician'
            ])
        elif risk_level in ['MODERATE-HIGH', 'MODERATE']:
            recommendations.extend([
                'Schedule follow-up appointment',
                'Regular monitoring recommended',
                'Lifestyle modifications may help',
                'Review medications with doctor'
            ])
        else:  # LOW, LOW-MODERATE
            recommendations.extend([
                'Continue regular checkups',
                'Maintain healthy lifestyle',
                'Balanced diet recommended',
                'Regular exercise beneficial'
            ])
        
        # إضافة توصيات من Domain Rules إن وجدت
        domain_recs = domain_assessment.get('insights', {}).get('recommendations_ar', [])
        if domain_recs:
            recommendations.extend(domain_recs[:2])  # أول توصيتين
        
        return recommendations[:6]  # أقصى 6 توصيات


# Create singleton instance
final_decision_engine = FinalDecisionEngine()
