#!/usr/bin/env python3
"""
Script simple para cargar SOLO zona y dispositivo
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from devices.models import Zone, Device

print("\n" + "="*60)
print("🌱 CARGANDO ZONA Y DISPOSITIVO")
print("="*60)

# 1. Crear Zona
print("\n📍 Paso 1: Creando zona ZONE-001...")
try:
    zone = Zone.objects.filter(code='ZONE-001').first()
    if zone:
        print(f"  ℹ️  Zona ya existe: {zone.code} - {zone.name}")
    else:
        zone = Zone(
            code='ZONE-001',
            name='Centro de Lima',
            description='Zona central de monitoreo',
            speed_limit=60,
            is_active=True
        )
        zone.save()
        print(f"  ✅ Zona creada exitosamente!")
        print(f"     Código: {zone.code}")
        print(f"     Nombre: {zone.name}")
        print(f"     Límite: {zone.speed_limit} km/h")
except Exception as e:
    print(f"  ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 2. Crear Dispositivo
print("\n📹 Paso 2: Creando dispositivo CAM-001...")
try:
    device = Device.objects.filter(code='CAM-001').first()
    if device:
        print(f"  ℹ️  Dispositivo ya existe: {device.code} - {device.name}")
    else:
        device = Device(
            code='CAM-001',
            name='Cámara Principal',
            device_type='camera',
            zone=zone,
            ip_address='192.168.1.100',
            rtsp_url='rtsp://localhost:8554/stream',
            is_active=True,
            status='active',
            location_lat=-12.0464,
            location_lon=-77.0428,
            address='Av. Arequipa 1234, Lima',
            model='Hikvision DS-2CD2345',
            manufacturer='Hikvision',
            resolution='1920x1080',
            fps=30
        )
        device.save()
        print(f"  ✅ Dispositivo creado exitosamente!")
        print(f"     Código: {device.code}")
        print(f"     Nombre: {device.name}")
        print(f"     Zona: {device.zone.name}")
        print(f"     IP: {device.ip_address}")
        print(f"     Estado: {device.status}")
except Exception as e:
    print(f"  ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 3. Verificar
print("\n" + "="*60)
print("📊 VERIFICACIÓN FINAL")
print("="*60)

total_zones = Zone.objects.count()
total_devices = Device.objects.count()

print(f"\n✅ Zonas en BD: {total_zones}")
for z in Zone.objects.all():
    print(f"   • {z.code} - {z.name} ({z.speed_limit} km/h)")

print(f"\n✅ Dispositivos en BD: {total_devices}")
for d in Device.objects.all():
    print(f"   • {d.code} - {d.name} (zona: {d.zone.code})")

print("\n✅ PROCESO COMPLETADO")
print("="*60 + "\n")
