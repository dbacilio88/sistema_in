#!/usr/bin/env python
"""
Script simple para inicializar la base de datos
Ejecutar desde backend-django: python init_database.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.db import connection

User = get_user_model()

def check_database():
    """Verificar conexión a base de datos"""
    print("🔍 Verificando conexión a base de datos...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Conexión a PostgreSQL exitosa")
        return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def run_migrations():
    """Ejecutar migraciones"""
    print("\n📦 Ejecutando migraciones...")
    try:
        call_command('migrate', '--noinput')
        print("✅ Migraciones completadas")
        return True
    except Exception as e:
        print(f"❌ Error en migraciones: {e}")
        return False

def create_superuser():
    """Crear superusuario si no existe"""
    print("\n👤 Verificando superusuario...")
    try:
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@traffic.pe',
                password='admin123',
                first_name='Admin',
                last_name='System'
            )
            print("✅ Superusuario creado: admin / admin123")
        else:
            print("ℹ️  Superusuario 'admin' ya existe")
        return True
    except Exception as e:
        print(f"❌ Error creando superusuario: {e}")
        return False

def load_seed_data():
    """Cargar datos semilla básicos"""
    print("\n🌱 Cargando datos semilla...")
    
    try:
        from devices.models import Zone, Device
        from vehicles.models import Vehicle
        from infractions.models import Infraction
        
        # Crear zona de prueba
        zone, created = Zone.objects.get_or_create(
            code='ZONE-001',
            defaults={
                'name': 'Centro de Lima',
                'description': 'Zona central de monitoreo',
                'speed_limit': 60,  # Corregido: es speed_limit, no max_speed_limit
                'is_active': True
            }
        )
        if created:
            print(f"  ✅ Zona creada: {zone.name}")
        else:
            print(f"  ℹ️  Zona ya existe: {zone.name}")
        
        # Crear dispositivo de prueba
        device, created = Device.objects.get_or_create(
            code='CAM-001',  # Corregido: es code, no device_code
            defaults={
                'name': 'Cámara Principal',  # Corregido: es name, no device_name
                'device_type': 'camera',
                'zone': zone,
                'ip_address': '192.168.1.100',  # Campo requerido
                'rtsp_url': 'rtsp://localhost:8554/stream',  # Campo requerido
                'is_active': True,
                'location_lat': -12.0464,  # Corregido: es location_lat, no latitude
                'location_lon': -77.0428,  # Corregido: es location_lon, no longitude
                'address': 'Av. Arequipa 1234, Lima'
            }
        )
        if created:
            print(f"  ✅ Dispositivo creado: {device.name}")
        else:
            print(f"  ℹ️  Dispositivo ya existe: {device.name}")
        
        # Mostrar estadísticas
        print(f"\n📊 Estadísticas:")
        print(f"  👥 Usuarios: {User.objects.count()}")
        print(f"  📍 Zonas: {Zone.objects.count()}")
        print(f"  📹 Dispositivos: {Device.objects.count()}")
        print(f"  🚗 Vehículos: {Vehicle.objects.count()}")
        print(f"  🚨 Infracciones: {Infraction.objects.count()}")
        
        return True
    except Exception as e:
        print(f"❌ Error cargando datos semilla: {e}")
        import traceback
        traceback.print_exc()
        print("\n⚠️  Advertencia: Algunos datos no se pudieron cargar")
        return False

def show_infraction_types():
    """Mostrar tipos de infracciones disponibles"""
    print("\n📋 Tipos de infracción disponibles:")
    
    infraction_types = [
        ('speed', 'Exceso de velocidad'),
        ('red_light', 'Cruce de semáforo en rojo'),
        ('wrong_lane', 'Invasión de carril'),
        ('no_helmet', 'Sin casco (motocicletas)'),
        ('parking', 'Estacionamiento indebido'),
        ('phone_use', 'Uso de teléfono al conducir'),
        ('seatbelt', 'Sin cinturón de seguridad'),
        ('other', 'Otras infracciones')
    ]
    
    for code, description in infraction_types:
        print(f"  • {code:12} - {description}")

def main():
    """Función principal"""
    print("=" * 60)
    print("🗄️  INICIALIZACIÓN DE BASE DE DATOS")
    print("=" * 60)
    
    # Verificar conexión
    if not check_database():
        print("\n❌ No se pudo conectar a la base de datos")
        print("   Asegúrate de que PostgreSQL esté corriendo:")
        print("   docker-compose up -d postgres")
        sys.exit(1)
    
    # Ejecutar migraciones
    if not run_migrations():
        print("\n❌ Error en las migraciones")
        sys.exit(1)
    
    # Crear superusuario
    if not create_superuser():
        print("\n⚠️  Advertencia: No se pudo crear el superusuario")
    
    # Cargar datos semilla
    if not load_seed_data():
        print("\n⚠️  Advertencia: Algunos datos no se pudieron cargar")
    
    # Mostrar tipos de infracciones
    show_infraction_types()
    
    print("\n" + "=" * 60)
    print("✅ INICIALIZACIÓN COMPLETA")
    print("=" * 60)
    
    print("\n📊 Credenciales de acceso:")
    print("   Username: admin")
    print("   Password: admin123")
    
    print("\n🌐 URLs:")
    print("   Backend API:  http://localhost:8000/api/")
    print("   Admin Panel:  http://localhost:8000/admin/")
    
    print("\n✨ La base de datos está lista para usar")
    print("   Ahora puedes iniciar la detección de infracciones\n")

if __name__ == '__main__':
    main()
