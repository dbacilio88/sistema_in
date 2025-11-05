"""
Test script for ML prediction system

This script:
1. Creates a sample driver
2. Creates sample infractions for that driver
3. Tests feature extraction
4. Tests recidivism prediction
5. Displays results
"""
import sys
import os
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from django.utils.timezone import make_aware
from datetime import timedelta
from decimal import Decimal
from vehicles.models import Driver, Vehicle
from infractions.models import Infraction
from devices.models import Zone, Device
from ml_models.services import FeatureEngineeringService, RecidivismPredictionService
from ml_models.models import MLModel, MLPrediction


def create_test_data():
    """Create test data for ML prediction"""
    print("=" * 80)
    print("CREATING TEST DATA")
    print("=" * 80)
    
    # Create test driver
    driver, created = Driver.objects.get_or_create(
        document_number='12345678',
        defaults={
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'email': 'juan.perez@example.com',
            'phone': '+51987654321',
            'birth_date': timezone.now().date() - timedelta(days=365*30),  # 30 years old
            'license_number': 'Q12345678',
            'license_class': 'A-IIIc',
            'license_expiry': timezone.now().date() + timedelta(days=365*2)
        }
    )
    print(f"✓ Driver {'created' if created else 'found'}: {driver.full_name} (DNI: {driver.document_number})")
    
    # Create test vehicle
    vehicle, created = Vehicle.objects.get_or_create(
        license_plate='ABC-123',
        defaults={
            'make': 'Toyota',
            'model': 'Corolla',
            'year': 2020,
            'color': 'silver',
            'vehicle_type': 'car',
            'owner_name': driver.full_name,
            'owner_dni': driver.document_number
        }
    )
    print(f"✓ Vehicle {'created' if created else 'found'}: {vehicle.license_plate} ({vehicle.make} {vehicle.model})")
    
    # Create test zone and device
    zone, _ = Zone.objects.get_or_create(
        name='Test Zone',
        defaults={
            'code': 'ZN-TEST',
            'description': 'Test zone for ML predictions',
            'speed_limit': 60
        }
    )
    
    device, _ = Device.objects.get_or_create(
        name='Test Camera',
        defaults={
            'zone': zone,
            'device_type': 'camera',
            'status': 'active',
            'ip_address': '192.168.1.100'
        }
    )
    
    # Create test infractions with different patterns
    now = timezone.now()
    infractions_data = [
        # Recent infractions (high risk)
        {'days_ago': 2, 'type': 'speed', 'excess': 25},
        {'days_ago': 5, 'type': 'red_light', 'excess': 0},
        {'days_ago': 8, 'type': 'speed', 'excess': 18},
        
        # Medium-term infractions
        {'days_ago': 35, 'type': 'lane_invasion', 'excess': 0},
        {'days_ago': 42, 'type': 'speed', 'excess': 15},
        
        # Older infractions
        {'days_ago': 95, 'type': 'red_light', 'excess': 0},
        {'days_ago': 120, 'type': 'speed', 'excess': 22},
        {'days_ago': 180, 'type': 'no_helmet', 'excess': 0},
        
        # Night infractions  
        {'days_ago': 10, 'type': 'speed', 'excess': 30},
        {'days_ago': 25, 'type': 'red_light', 'excess': 0},
    ]
    
    created_count = 0
    for inf_data in infractions_data:
        # Create timezone-aware datetime
        detected_timestamp = timezone.now() - timedelta(days=inf_data['days_ago'])
        
        # Use create instead of get_or_create to avoid uniqueness issues
        try:
            infraction = Infraction.objects.create(
                vehicle=vehicle,
                driver=driver,
                detected_at=detected_timestamp,
                device=device,
                zone=zone,
                infraction_type=inf_data['type'],
                detected_speed=60 + inf_data['excess'] if inf_data['type'] == 'speed' else None,
                speed_limit=60 if inf_data['type'] == 'speed' else None,
                severity='high' if inf_data['excess'] > 20 else 'medium',
                status='validated',
                license_plate_confidence=Decimal('0.95')
            )
            created_count += 1
        except Exception as e:
            print(f"Warning: Could not create infraction: {e}")
            continue
    
    print(f"✓ Created {created_count} test infractions")
    print(f"  Total infractions for driver: {Infraction.objects.filter(driver=driver).count()}")
    print()
    
    return driver


def test_feature_extraction(driver):
    """Test feature extraction"""
    print("=" * 80)
    print("TESTING FEATURE EXTRACTION")
    print("=" * 80)
    
    features = FeatureEngineeringService.extract_features(driver.document_number)
    
    print(f"\nExtracted {len(features)} features for driver {driver.document_number}:\n")
    
    # Group features by category
    categories = {
        'Historical Counts': ['infraction_count_total', 'infraction_count_7d', 'infraction_count_30d', 
                             'infraction_count_90d', 'infraction_count_365d'],
        'By Type': ['speed_violations', 'red_light_violations', 'lane_invasions', 
                   'no_helmet', 'no_seatbelt'],
        'Severity': ['avg_speed_excess', 'max_speed_excess', 'avg_severity_score'],
        'Recency': ['days_since_last_infraction', 'recency_score'],
        'Patterns': ['infractions_night', 'infractions_weekend', 'infractions_rush_hour'],
        'Rates': ['infraction_rate', 'infraction_trend'],
        'Diversity': ['infraction_type_diversity'],
        'Driver': ['driver_age', 'driver_risk_score', 'driver_is_suspended']
    }
    
    for category, feature_names in categories.items():
        print(f"{category}:")
        for feat_name in feature_names:
            if feat_name in features:
                value = features[feat_name]
                if isinstance(value, float):
                    print(f"  • {feat_name}: {value:.3f}")
                else:
                    print(f"  • {feat_name}: {value}")
        print()
    
    return features


def test_prediction(driver):
    """Test recidivism prediction"""
    print("=" * 80)
    print("TESTING RECIDIVISM PREDICTION")
    print("=" * 80)
    
    result = RecidivismPredictionService.predict_recidivism_risk(driver.document_number)
    
    print(f"\nPrediction Results for driver {driver.document_number}:\n")
    print(f"Recidivism Probability: {result['recidivism_probability']:.1%}")
    print(f"Risk Category: {result['risk_category'].upper()}")
    print(f"Confidence: {result['confidence']:.1%}")
    print(f"Model Version: {result['model_version']}")
    print(f"Prediction Time: {result['prediction_timestamp']}")
    print(f"\nTop Risk Factors:")
    
    for i, factor in enumerate(result['risk_factors'], 1):
        print(f"  {i}. {factor['factor']}")
        print(f"     Description: {factor['description']}")
        print(f"     Importance: {factor['importance']:.1%}")
        print()
    
    return result


def test_api_simulation():
    """Simulate API call"""
    print("=" * 80)
    print("SIMULATING API CALL")
    print("=" * 80)
    
    # This would be: POST /api/ml/predictions/recidivism/
    # Body: {"driver_dni": "12345678"}
    
    driver = Driver.objects.get(document_number='12345678')
    
    # Get or create model
    model, _ = MLModel.objects.get_or_create(
        model_name='recidivism_heuristic',
        version='v1.0.0',
        defaults={
            'model_type': 'classification',
            'framework': 'sklearn',
            'model_path': 'heuristic://recidivism_v1.0.0',
            'metrics': {
                'accuracy': 0.75,
                'note': 'Heuristic model - placeholder for XGBoost'
            },
            'is_active': True,
            'deployment_environment': 'development'
        }
    )
    
    # Make prediction
    start_time = timezone.now()
    prediction_result = RecidivismPredictionService.predict_recidivism_risk('12345678')
    end_time = timezone.now()
    prediction_time_ms = (end_time - start_time).total_seconds() * 1000
    
    # Save prediction
    ml_prediction = MLPrediction.objects.create(
        model=model,
        driver=driver,
        prediction_type='recidivism',
        prediction_value=prediction_result['recidivism_probability'],
        prediction_class=prediction_result['risk_category'],
        prediction_confidence=prediction_result['confidence'],
        features=prediction_result['features'],
        prediction_time_ms=prediction_time_ms
    )
    
    # Update driver risk
    driver.risk_score = prediction_result['recidivism_probability']
    driver.risk_category = prediction_result['risk_category']
    driver.risk_updated_at = timezone.now()
    driver.save()
    
    print(f"\n✓ Prediction saved to database")
    print(f"  Prediction ID: {ml_prediction.id}")
    print(f"  Prediction Time: {prediction_time_ms:.2f}ms")
    print(f"  Driver Risk Updated: {driver.risk_score:.1%} ({driver.risk_category})")
    print()
    
    return ml_prediction


def display_summary():
    """Display summary statistics"""
    print("=" * 80)
    print("SYSTEM SUMMARY")
    print("=" * 80)
    
    print(f"\nDatabase Statistics:")
    print(f"  • Drivers: {Driver.objects.count()}")
    print(f"  • Infractions: {Infraction.objects.count()}")
    print(f"  • ML Models: {MLModel.objects.count()}")
    print(f"  • ML Predictions: {MLPrediction.objects.count()}")
    
    # High risk drivers
    high_risk = Driver.objects.filter(risk_category__in=['high', 'critical'])
    print(f"\nHigh Risk Drivers: {high_risk.count()}")
    for driver in high_risk[:5]:
        print(f"  • {driver.full_name} (DNI: {driver.document_number})")
        print(f"    Risk Score: {driver.risk_score:.1%} ({driver.risk_category})")
        print(f"    Last Updated: {driver.risk_updated_at}")
    
    print()


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("ML PREDICTION SYSTEM - COMPREHENSIVE TEST")
    print("=" * 80 + "\n")
    
    try:
        # 1. Create test data
        driver = create_test_data()
        
        # 2. Test feature extraction
        features = test_feature_extraction(driver)
        
        # 3. Test prediction
        prediction = test_prediction(driver)
        
        # 4. Test API simulation
        ml_prediction = test_api_simulation()
        
        # 5. Display summary
        display_summary()
        
        print("=" * 80)
        print("✓ ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print("\nNext Steps:")
        print("1. Test API endpoint: curl -X POST http://localhost:8000/api/ml/predictions/recidivism/")
        print("   -H 'Content-Type: application/json' -d '{\"driver_dni\": \"12345678\"}'")
        print("2. Check admin panel: http://localhost:8000/admin/ml_models/")
        print("3. Train actual XGBoost model with real data")
        print()
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
