"""
Machine Learning Services for predictive analytics
"""
from datetime import timedelta
from typing import Dict, List, Optional
import numpy as np
from django.db import models
from django.db.models import Count, Avg, Q, F
from django.utils import timezone
from infractions.models import Infraction
from vehicles.models import Driver


class FeatureEngineeringService:
    """Extract features from driver history for ML models"""
    
    @staticmethod
    def extract_features(driver_dni: str) -> Dict:
        """
        Extract 20+ features from driver's infraction history
        
        Args:
            driver_dni: Driver's DNI
            
        Returns:
            Dictionary with feature names and values
        """
        # Get driver
        try:
            driver = Driver.objects.get(document_number=driver_dni)
        except Driver.DoesNotExist:
            return FeatureEngineeringService.get_default_features()
        
        # Get infractions
        infractions = Infraction.objects.filter(
            driver=driver
        ).order_by('-detected_at')
        
        if not infractions.exists():
            return FeatureEngineeringService.get_default_features()
        
        now = timezone.now()
        features = {}
        
        # 1. Características históricas (cantidad por período)
        features['infraction_count_total'] = infractions.count()
        features['infraction_count_7d'] = infractions.filter(
            detected_at__gte=now - timedelta(days=7)
        ).count()
        features['infraction_count_30d'] = infractions.filter(
            detected_at__gte=now - timedelta(days=30)
        ).count()
        features['infraction_count_90d'] = infractions.filter(
            detected_at__gte=now - timedelta(days=90)
        ).count()
        features['infraction_count_365d'] = infractions.filter(
            detected_at__gte=now - timedelta(days=365)
        ).count()
        
        # 2. Por tipo de infracción
        features['speed_violations'] = infractions.filter(
            infraction_type='speed'
        ).count()
        features['red_light_violations'] = infractions.filter(
            infraction_type='red_light'
        ).count()
        features['lane_invasions'] = infractions.filter(
            infraction_type='wrong_lane'
        ).count()
        features['no_helmet_violations'] = infractions.filter(
            infraction_type='no_helmet'
        ).count()
        features['no_seatbelt_violations'] = infractions.filter(
            infraction_type='seatbelt'
        ).count()
        
        # 3. Severidad
        speed_infractions = infractions.filter(
            infraction_type='speed',
            detected_speed__isnull=False,
            speed_limit__isnull=False
        )
        if speed_infractions.exists():
            features['avg_speed_excess'] = float(
                speed_infractions.aggregate(
                    avg_excess=Avg(
                        F('detected_speed') - F('speed_limit')
                    )
                )['avg_excess'] or 0
            )
            features['max_speed_excess'] = float(
                max([
                    i.detected_speed - i.speed_limit
                    for i in speed_infractions
                    if i.detected_speed and i.speed_limit
                ] or [0])
            )
        else:
            features['avg_speed_excess'] = 0.0
            features['max_speed_excess'] = 0.0
        
        # 4. Recencia
        last_infraction = infractions.first()
        if last_infraction:
            days_since_last = max(0.01, (now - last_infraction.detected_at).days)  # Evitar división por cero
            features['days_since_last_infraction'] = days_since_last
            features['recency_score'] = 1.0 / (1.0 + days_since_last)  # Más reciente = mayor score
        else:
            features['days_since_last_infraction'] = 999
            features['recency_score'] = 0.0
        
        # 5. Patrones temporales
        features['infractions_night'] = infractions.filter(
            Q(detected_at__hour__gte=22) | Q(detected_at__hour__lte=6)
        ).count()
        features['infractions_weekend'] = infractions.filter(
            detected_at__week_day__in=[1, 7]  # Sunday=1, Saturday=7 in Django
        ).count()
        features['infractions_rush_hour'] = infractions.filter(
            Q(detected_at__hour__gte=7, detected_at__hour__lte=9) |
            Q(detected_at__hour__gte=17, detected_at__hour__lte=19)
        ).count()
        
        # 6. Tasa de reincidencia histórica
        if features['infraction_count_total'] > 1:
            first_infraction = infractions.last()
            time_span_days = (now - first_infraction.detected_at).days
            features['infraction_rate'] = features['infraction_count_total'] / max(time_span_days, 1)
        else:
            features['infraction_rate'] = 0.0
        
        # 7. Características del conductor
        if driver.birth_date:
            age = (now.date() - driver.birth_date).days // 365
            features['driver_age'] = age
        else:
            features['driver_age'] = 0
        
        features['driver_risk_score'] = float(driver.risk_score)
        features['driver_is_suspended'] = 1 if driver.is_suspended else 0
        
        # 8. Diversidad de infracciones
        infraction_types = infractions.values('infraction_type').distinct().count()
        features['infraction_type_diversity'] = infraction_types
        
        # 9. Tendencia (infracciones recientes vs antiguas)
        recent_count = features['infraction_count_30d']
        old_count = infractions.filter(
            detected_at__lt=now - timedelta(days=30),
            detected_at__gte=now - timedelta(days=90)
        ).count()
        if old_count > 0:
            features['infraction_trend'] = recent_count / old_count
        else:
            features['infraction_trend'] = float(recent_count) if recent_count > 0 else 0.0
        
        # 10. Severidad promedio
        severity_map = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        severity_scores = [
            severity_map.get(i.severity, 2)
            for i in infractions
            if i.severity
        ]
        features['avg_severity_score'] = np.mean(severity_scores) if severity_scores else 2.0
        
        return features
    
    @staticmethod
    def get_default_features() -> Dict:
        """Return default feature values for drivers with no history"""
        return {
            # Históricas
            'infraction_count_total': 0,
            'infraction_count_7d': 0,
            'infraction_count_30d': 0,
            'infraction_count_90d': 0,
            'infraction_count_365d': 0,
            # Por tipo
            'speed_violations': 0,
            'red_light_violations': 0,
            'lane_invasions': 0,
            'no_helmet_violations': 0,
            'no_seatbelt_violations': 0,
            # Severidad
            'avg_speed_excess': 0.0,
            'max_speed_excess': 0.0,
            # Recencia
            'days_since_last_infraction': 999,
            'recency_score': 0.0,
            # Patrones
            'infractions_night': 0,
            'infractions_weekend': 0,
            'infractions_rush_hour': 0,
            # Tasa
            'infraction_rate': 0.0,
            # Conductor
            'driver_age': 0,
            'driver_risk_score': 0.0,
            'driver_is_suspended': 0,
            # Otros
            'infraction_type_diversity': 0,
            'infraction_trend': 0.0,
            'avg_severity_score': 2.0,
        }


class RecidivismPredictionService:
    """Service for recidivism risk prediction"""
    
    @staticmethod
    def predict_recidivism_risk(driver_dni: str) -> Dict:
        """
        Predict recidivism risk for a driver
        
        NOTE: This is a placeholder implementation using heuristics.
        In production, this should use the trained XGBoost model.
        
        Args:
            driver_dni: Driver's DNI
            
        Returns:
            Dictionary with prediction results
        """
        # Extract features
        features = FeatureEngineeringService.extract_features(driver_dni)
        
        # HEURISTIC CALCULATION (placeholder for actual ML model)
        # In production, replace this with: model.predict(features)
        
        # Calculate risk score based on key factors
        risk_score = 0.0
        risk_factors = []
        
        # Factor 1: Recent infractions (35% weight)
        recent_count = features['infraction_count_90d']
        if recent_count >= 5:
            risk_score += 0.35
            risk_factors.append({
                'factor': 'infraction_count_90d',
                'importance': 0.35,
                'value': recent_count,
                'description': f'Alto número de infracciones recientes ({recent_count} en 90 días)'
            })
        elif recent_count >= 3:
            risk_score += 0.25
            risk_factors.append({
                'factor': 'infraction_count_90d',
                'importance': 0.25,
                'value': recent_count,
                'description': f'Múltiples infracciones recientes ({recent_count} en 90 días)'
            })
        elif recent_count >= 1:
            risk_score += 0.15
        
        # Factor 2: Recency (28% weight)
        recency = features['recency_score']
        if recency > 0.5:  # Muy reciente (< 1 día)
            risk_score += 0.28
            risk_factors.append({
                'factor': 'recency',
                'importance': 0.28,
                'value': features['days_since_last_infraction'],
                'description': f'Infracción muy reciente ({features["days_since_last_infraction"]} días)'
            })
        elif recency > 0.2:  # Reciente (< 5 días)
            risk_score += 0.20
        elif recency > 0.1:  # Moderadamente reciente
            risk_score += 0.10
        
        # Factor 3: Severity (22% weight)
        avg_severity = features['avg_severity_score']
        max_speed_excess = features['max_speed_excess']
        if avg_severity >= 3.5 or max_speed_excess > 30:
            risk_score += 0.22
            risk_factors.append({
                'factor': 'severity',
                'importance': 0.22,
                'value': 'high',
                'description': f'Infracciones graves (severidad: {avg_severity:.1f}, exceso máx: {max_speed_excess:.0f} km/h)'
            })
        elif avg_severity >= 2.5 or max_speed_excess > 20:
            risk_score += 0.15
        elif avg_severity >= 2.0:
            risk_score += 0.08
        
        # Factor 4: Type diversity and trend (10% weight)
        diversity = features['infraction_type_diversity']
        trend = features['infraction_trend']
        if diversity >= 3 or trend > 1.5:
            risk_score += 0.10
            if diversity >= 3:
                risk_factors.append({
                    'factor': 'diversity',
                    'importance': 0.10,
                    'value': diversity,
                    'description': f'Múltiples tipos de infracciones ({diversity} tipos diferentes)'
                })
        elif diversity >= 2 or trend > 1.0:
            risk_score += 0.05
        
        # Factor 5: Patterns (5% weight)
        night_count = features['infractions_night']
        if night_count >= 3:
            risk_score += 0.05
        
        # Cap at 1.0
        risk_score = min(risk_score, 1.0)
        
        # Determine risk category
        if risk_score < 0.25:
            risk_category = 'low'
        elif risk_score < 0.50:
            risk_category = 'medium'
        elif risk_score < 0.75:
            risk_category = 'high'
        else:
            risk_category = 'critical'
        
        # Sort risk factors by importance
        risk_factors.sort(key=lambda x: x['importance'], reverse=True)
        
        return {
            'driver_dni': driver_dni,
            'recidivism_probability': round(risk_score, 3),
            'risk_category': risk_category,
            'risk_factors': risk_factors[:3],  # Top 3 factors
            'features': features,
            'model_version': 'heuristic_v1.0.0',  # Placeholder
            'prediction_timestamp': timezone.now().isoformat(),
            'confidence': 0.75  # Placeholder confidence
        }
