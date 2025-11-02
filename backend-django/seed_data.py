"""
Seed data script for Traffic Violation Detection System
Creates initial data for development and testing
"""
import os
import sys
import django
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django environment
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from devices.models import Zone, Device, DeviceEvent
from vehicles.models import Vehicle, Driver, VehicleOwnership
from infractions.models import Infraction, InfractionEvent

User = get_user_model()

def create_users():
    """Create test users with different roles"""
    print("👥 Creating users...")
    
    # Admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@traffic.pe',
            'first_name': 'System',
            'last_name': 'Administrator',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True,
            'phone': '+51-999-888-777'
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"✅ Created admin user: {admin_user.username}")
    
    # Supervisor user
    supervisor_user, created = User.objects.get_or_create(
        username='supervisor',
        defaults={
            'email': 'supervisor@traffic.pe',
            'first_name': 'Juan Carlos',
            'last_name': 'Pérez Supervisor',
            'role': 'supervisor',
            'is_staff': True,
            'phone': '+51-999-777-666'
        }
    )
    if created:
        supervisor_user.set_password('supervisor123')
        supervisor_user.save()
        print(f"✅ Created supervisor user: {supervisor_user.username}")
    
    # Operator user
    operator_user, created = User.objects.get_or_create(
        username='operator',
        defaults={
            'email': 'operator@traffic.pe',
            'first_name': 'María Elena',
            'last_name': 'García Operador',
            'role': 'operator',
            'is_staff': True,
            'phone': '+51-999-666-555'
        }
    )
    if created:
        operator_user.set_password('operator123')
        operator_user.save()
        print(f"✅ Created operator user: {operator_user.username}")
    
    # Auditor user
    auditor_user, created = User.objects.get_or_create(
        username='auditor',
        defaults={
            'email': 'auditor@traffic.pe',
            'first_name': 'Carlos Alberto',
            'last_name': 'Silva Auditor',
            'role': 'auditor',
            'is_staff': True,
            'phone': '+51-999-555-444'
        }
    )
    if created:
        auditor_user.set_password('auditor123')
        auditor_user.save()
        print(f"✅ Created auditor user: {auditor_user.username}")
    
    return {
        'admin': admin_user,
        'supervisor': supervisor_user,
        'operator': operator_user,
        'auditor': auditor_user
    }

def create_zones():
    """Create traffic zones"""
    print("🗺️ Creating traffic zones...")
    
    zones_data = [
        {
            'name': 'Centro de Lima',
            'code': 'ZN001',
            'description': 'Zona céntrica de la ciudad con alto tráfico comercial',
            'speed_limit': 40,
            'boundary': {
                "type": "Polygon",
                "coordinates": [[
                    [-77.0350, -12.0450],
                    [-77.0250, -12.0450],
                    [-77.0250, -12.0350],
                    [-77.0350, -12.0350],
                    [-77.0350, -12.0450]
                ]]
            },
            'center_point_lat': Decimal('-12.0400'),
            'center_point_lon': Decimal('-77.0300')
        },
        {
            'name': 'Av. Javier Prado',
            'code': 'ZN002',
            'description': 'Avenida principal con tráfico intenso',
            'speed_limit': 60,
            'boundary': {
                "type": "Polygon",
                "coordinates": [[
                    [-77.0100, -12.1000],
                    [-76.9800, -12.1000],
                    [-76.9800, -12.0900],
                    [-77.0100, -12.0900],
                    [-77.0100, -12.1000]
                ]]
            },
            'center_point_lat': Decimal('-12.0950'),
            'center_point_lon': Decimal('-76.9950')
        },
        {
            'name': 'Zona Escolar San Isidro',
            'code': 'ZN003',
            'description': 'Zona escolar con límite de velocidad reducido',
            'speed_limit': 30,
            'boundary': {
                "type": "Polygon",
                "coordinates": [[
                    [-77.0500, -12.1100],
                    [-77.0400, -12.1100],
                    [-77.0400, -12.1000],
                    [-77.0500, -12.1000],
                    [-77.0500, -12.1100]
                ]]
            },
            'center_point_lat': Decimal('-12.1050'),
            'center_point_lon': Decimal('-77.0450')
        }
    ]
    
    zones = {}
    for zone_data in zones_data:
        zone, created = Zone.objects.get_or_create(
            code=zone_data['code'],
            defaults=zone_data
        )
        zones[zone_data['code']] = zone
        if created:
            print(f"✅ Created zone: {zone.code} - {zone.name}")
    
    return zones

def create_devices(zones):
    """Create traffic monitoring devices/cameras"""
    print("📹 Creating devices/cameras...")
    
    devices_data = [
        {
            'code': 'CAM001',
            'name': 'Cámara Plaza de Armas',
            'device_type': 'camera',
            'zone': zones['ZN001'],
            'location_lat': Decimal('-12.0430'),
            'location_lon': Decimal('-77.0330'),
            'address': 'Plaza de Armas, Cercado de Lima',
            'ip_address': '192.168.1.100',
            'rtsp_url': 'rtsp://admin:admin123@192.168.1.100:554/h264/ch1/main/av_stream',
            'rtsp_username': 'admin',
            'rtsp_password': 'admin123',
            'model': 'EZVIZ H6C Pro 2K',
            'manufacturer': 'EZVIZ',
            'firmware_version': '5.7.3',
            'resolution': '2560x1440',
            'fps': 30,
            'status': 'active'
        },
        {
            'code': 'CAM002',
            'name': 'Cámara Javier Prado Este',
            'device_type': 'camera',
            'zone': zones['ZN002'],
            'location_lat': Decimal('-12.0980'),
            'location_lon': Decimal('-76.9980'),
            'address': 'Av. Javier Prado Este 1234, San Isidro',
            'ip_address': '192.168.1.101',
            'rtsp_url': 'rtsp://admin:admin123@192.168.1.101:554/h264/ch1/main/av_stream',
            'rtsp_username': 'admin',
            'rtsp_password': 'admin123',
            'model': 'EZVIZ H6C Pro 2K',
            'manufacturer': 'EZVIZ',
            'firmware_version': '5.7.3',
            'resolution': '2560x1440',
            'fps': 30,
            'status': 'active'
        },
        {
            'code': 'CAM003',
            'name': 'Cámara Zona Escolar',
            'device_type': 'camera',
            'zone': zones['ZN003'],
            'location_lat': Decimal('-12.1080'),
            'location_lon': Decimal('-77.0480'),
            'address': 'Calle Las Flores 456, San Isidro',
            'ip_address': '192.168.1.102',
            'rtsp_url': 'rtsp://admin:admin123@192.168.1.102:554/h264/ch1/main/av_stream',
            'rtsp_username': 'admin',
            'rtsp_password': 'admin123',
            'model': 'EZVIZ H6C Pro 2K',
            'manufacturer': 'EZVIZ',
            'firmware_version': '5.7.3',
            'resolution': '1920x1080',
            'fps': 25,
            'status': 'maintenance'
        }
    ]
    
    devices = {}
    for device_data in devices_data:
        device, created = Device.objects.get_or_create(
            code=device_data['code'],
            defaults=device_data
        )
        devices[device_data['code']] = device
        if created:
            print(f"✅ Created device: {device.code} - {device.name}")
            
            # Create device events
            DeviceEvent.objects.create(
                device=device,
                event_type='online',
                message=f'Device {device.code} came online',
                timestamp=timezone.now() - timedelta(hours=2)
            )
    
    return devices

def create_drivers():
    """Create test drivers"""
    print("👤 Creating drivers...")
    
    drivers_data = [
        {
            'document_number': '12345678',
            'first_name': 'Carlos Alberto',
            'last_name': 'Mendoza Silva',
            'birth_date': datetime(1985, 5, 15).date(),
            'phone': '+51-999-123-456',
            'email': 'carlos.mendoza@email.com',
            'license_number': 'Q12345678',
            'license_class': 'AIII',
            'license_expiry': datetime(2026, 8, 20).date()
        },
        {
            'document_number': '87654321',
            'first_name': 'Ana María',
            'last_name': 'González Pérez',
            'birth_date': datetime(1990, 12, 3).date(),
            'phone': '+51-999-654-321',
            'email': 'ana.gonzalez@email.com',
            'license_number': 'Q87654321',
            'license_class': 'AII',
            'license_expiry': datetime(2025, 11, 15).date()
        },
        {
            'document_number': '11223344',
            'first_name': 'Roberto',
            'last_name': 'Vargas Torres',
            'birth_date': datetime(1978, 8, 22).date(),
            'phone': '+51-999-112-233',
            'license_number': 'Q11223344',
            'license_class': 'AIII',
            'license_expiry': datetime(2024, 12, 10).date(),
            'is_suspended': True,
            'suspension_reason': 'Exceso de infracciones acumuladas'
        }
    ]
    
    drivers = {}
    for driver_data in drivers_data:
        driver, created = Driver.objects.get_or_create(
            document_number=driver_data['document_number'],
            defaults=driver_data
        )
        drivers[driver_data['document_number']] = driver
        if created:
            print(f"✅ Created driver: {driver.full_name} ({driver.document_number})")
    
    return drivers

def create_vehicles(drivers):
    """Create test vehicles"""
    print("🚗 Creating vehicles...")
    
    vehicles_data = [
        {
            'license_plate': 'ABC-123',
            'make': 'Toyota',
            'model': 'Corolla',
            'year': 2020,
            'color': 'Blanco',
            'vehicle_type': 'car',
            'owner_name': 'Carlos Alberto Mendoza Silva',
            'owner_dni': '12345678',
            'registration_date': datetime(2020, 3, 15).date()
        },
        {
            'license_plate': 'XYZ-789',
            'make': 'Nissan',
            'model': 'Sentra',
            'year': 2019,
            'color': 'Gris',
            'vehicle_type': 'car',
            'owner_name': 'Ana María González Pérez',
            'owner_dni': '87654321',
            'registration_date': datetime(2019, 7, 22).date()
        },
        {
            'license_plate': 'DEF-456',
            'make': 'Chevrolet',
            'model': 'Spark',
            'year': 2018,
            'color': 'Rojo',
            'vehicle_type': 'car',
            'owner_name': 'Roberto Vargas Torres',
            'owner_dni': '11223344',
            'registration_date': datetime(2018, 11, 5).date(),
            'is_wanted': True,
            'notes': 'Vehículo reportado en investigación por infracciones reiteradas'
        }
    ]
    
    vehicles = {}
    for vehicle_data in vehicles_data:
        vehicle, created = Vehicle.objects.get_or_create(
            license_plate=vehicle_data['license_plate'],
            defaults=vehicle_data
        )
        vehicles[vehicle_data['license_plate']] = vehicle
        if created:
            print(f"✅ Created vehicle: {vehicle.license_plate} - {vehicle.make} {vehicle.model}")
            
            # Create ownership relationship
            driver_dni = vehicle_data.get('owner_dni')
            if driver_dni in drivers:
                VehicleOwnership.objects.get_or_create(
                    vehicle=vehicle,
                    driver=drivers[driver_dni],
                    defaults={
                        'start_date': vehicle_data.get('registration_date', datetime.now().date()),
                        'is_primary_owner': True,
                        'ownership_percentage': Decimal('100.00')
                    }
                )
    
    return vehicles

def create_sample_infractions(users, devices, zones, vehicles):
    """Create sample infractions for testing"""
    print("🚨 Creating sample infractions...")
    
    infractions_data = [
        {
            'infraction_type': 'speed',
            'device': devices['CAM001'],
            'zone': zones['ZN001'],
            'location_lat': Decimal('-12.0430'),
            'location_lon': Decimal('-77.0330'),
            'vehicle': vehicles['ABC-123'],
            'license_plate_detected': 'ABC-123',
            'license_plate_confidence': 0.95,
            'detected_speed': 65.5,
            'speed_limit': 40,
            'severity': 'high',
            'detected_at': timezone.now() - timedelta(hours=5),
            'snapshot_url': 'https://storage.traffic.pe/snapshots/infraction_001.jpg',
            'video_url': 'https://storage.traffic.pe/videos/infraction_001.mp4',
            'status': 'pending',
            'fine_amount': Decimal('400.00')
        },
        {
            'infraction_type': 'speed',
            'device': devices['CAM002'],
            'zone': zones['ZN002'],
            'location_lat': Decimal('-12.0980'),
            'location_lon': Decimal('-76.9980'),
            'vehicle': vehicles['XYZ-789'],
            'license_plate_detected': 'XYZ-789',
            'license_plate_confidence': 0.88,
            'detected_speed': 78.2,
            'speed_limit': 60,
            'severity': 'medium',
            'detected_at': timezone.now() - timedelta(hours=2),
            'snapshot_url': 'https://storage.traffic.pe/snapshots/infraction_002.jpg',
            'video_url': 'https://storage.traffic.pe/videos/infraction_002.mp4',
            'status': 'validated',
            'reviewed_by': users['supervisor'],
            'reviewed_at': timezone.now() - timedelta(hours=1),
            'review_notes': 'Infracción validada. Evidencia clara de exceso de velocidad.',
            'fine_amount': Decimal('200.00')
        },
        {
            'infraction_type': 'speed',
            'device': devices['CAM003'],
            'zone': zones['ZN003'],
            'location_lat': Decimal('-12.1080'),
            'location_lon': Decimal('-77.0480'),
            'license_plate_detected': 'DEF-456',
            'license_plate_confidence': 0.92,
            'detected_speed': 45.0,
            'speed_limit': 30,
            'severity': 'high',
            'detected_at': timezone.now() - timedelta(minutes=30),
            'snapshot_url': 'https://storage.traffic.pe/snapshots/infraction_003.jpg',
            'status': 'pending',
            'fine_amount': Decimal('600.00')
        }
    ]
    
    for infraction_data in infractions_data:
        infraction, created = Infraction.objects.get_or_create(
            device=infraction_data['device'],
            detected_at=infraction_data['detected_at'],
            license_plate_detected=infraction_data['license_plate_detected'],
            defaults=infraction_data
        )
        if created:
            print(f"✅ Created infraction: {infraction.infraction_code} - {infraction.get_infraction_type_display()}")
            
            # Create infraction events
            InfractionEvent.objects.create(
                infraction=infraction,
                event_type='detected',
                notes=f'Infraction detected by device {infraction.device.code}',
                timestamp=infraction.detected_at
            )
            
            if infraction.status == 'validated':
                InfractionEvent.objects.create(
                    infraction=infraction,
                    event_type='validated',
                    user=infraction.reviewed_by,
                    notes=infraction.review_notes,
                    timestamp=infraction.reviewed_at
                )

def main():
    """Run all seed data creation"""
    print("🌱 Starting seed data creation...")
    print("=" * 50)
    
    try:
        users = create_users()
        zones = create_zones()
        devices = create_devices(zones)
        drivers = create_drivers()
        vehicles = create_vehicles(drivers)
        create_sample_infractions(users, devices, zones, vehicles)
        
        print("=" * 50)
        print("✅ Seed data creation completed successfully!")
        print("\n📊 Summary:")
        print(f"   👥 Users: {User.objects.count()}")
        print(f"   🗺️ Zones: {Zone.objects.count()}")
        print(f"   📹 Devices: {Device.objects.count()}")
        print(f"   👤 Drivers: {Driver.objects.count()}")
        print(f"   🚗 Vehicles: {Vehicle.objects.count()}")
        print(f"   🚨 Infractions: {Infraction.objects.count()}")
        print("\n🔐 Test login credentials:")
        print("   Admin: admin / admin123")
        print("   Supervisor: supervisor / supervisor123")
        print("   Operator: operator / operator123")
        print("   Auditor: auditor / auditor123")
        
    except Exception as e:
        print(f"❌ Error creating seed data: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()