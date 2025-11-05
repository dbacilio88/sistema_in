#!/usr/bin/env python3
"""
Script para verificar y mostrar datos del sistema
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from devices.models import Zone, Device
from vehicles.models import Vehicle
from infractions.models import Infraction
from django.contrib.auth.models import User
from django.urls import reverse

def main():
    print("\n" + "="*60)
    print("🗄️  ESTADO DE LA BASE DE DATOS")
    print("="*60)
    
    # Contar registros
    users_count = User.objects.count()
    zones_count = Zone.objects.count()
    devices_count = Device.objects.count()
    vehicles_count = Vehicle.objects.count()
    infractions_count = Infraction.objects.count()
    
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"  👥 Usuarios: {users_count}")
    print(f"  📍 Zonas: {zones_count}")
    print(f"  📹 Dispositivos: {devices_count}")
    print(f"  🚗 Vehículos: {vehicles_count}")
    print(f"  🚨 Infracciones: {infractions_count}")
    
    # Mostrar zonas
    if zones_count > 0:
        print(f"\n📍 ZONAS REGISTRADAS:")
        for zone in Zone.objects.all():
            print(f"  • {zone.code} - {zone.name}")
            print(f"    Límite velocidad: {zone.speed_limit} km/h")
            print(f"    Activa: {'✅' if zone.is_active else '❌'}")
    
    # Mostrar dispositivos
    if devices_count > 0:
        print(f"\n📹 DISPOSITIVOS REGISTRADOS:")
        for device in Device.objects.all():
            print(f"  • {device.code} - {device.name}")
            print(f"    Tipo: {device.device_type}")
            print(f"    Zona: {device.zone.name}")
            print(f"    IP: {device.ip_address}")
            print(f"    Estado: {device.status}")
    
    # Mostrar usuarios
    if users_count > 0:
        print(f"\n👥 USUARIOS REGISTRADOS:")
        for user in User.objects.all():
            print(f"  • {user.username} ({user.email})")
            print(f"    Superusuario: {'✅' if user.is_superuser else '❌'}")
            print(f"    Staff: {'✅' if user.is_staff else '❌'}")
    
    # Mostrar infracciones
    if infractions_count > 0:
        print(f"\n🚨 INFRACCIONES REGISTRADAS:")
        for infraction in Infraction.objects.all()[:10]:  # Solo primeras 10
            print(f"  • {infraction.code} - {infraction.infraction_type}")
            print(f"    Vehículo: {infraction.vehicle_plate if infraction.vehicle_plate else 'N/A'}")
            print(f"    Fecha: {infraction.detected_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n" + "="*60)
    print("🌐 URLs PARA ACCEDER A LOS DATOS")
    print("="*60)
    print("\n📋 INTERFACES WEB:")
    print("  • Panel Admin:     http://localhost:8000/admin/")
    print("  • API Root:        http://localhost:8000/api/")
    print("  • API Docs:        http://localhost:8000/api/docs/")
    print("  • ReDoc:           http://localhost:8000/api/redoc/")
    
    print("\n📡 ENDPOINTS API REST:")
    print("  • Zonas:           http://localhost:8000/api/devices/zones/")
    print("  • Dispositivos:    http://localhost:8000/api/devices/")
    print("  • Vehículos:       http://localhost:8000/api/vehicles/")
    print("  • Infracciones:    http://localhost:8000/api/infractions/")
    print("  • Notificaciones:  http://localhost:8000/api/notifications/")
    
    print("\n🔍 EJEMPLOS DE USO:")
    print("  # Ver todas las zonas (navegador o curl)")
    print("  curl http://localhost:8000/api/devices/zones/")
    print()
    print("  # Ver todos los dispositivos")
    print("  curl http://localhost:8000/api/devices/")
    print()
    print("  # Ver estadísticas en API root")
    print("  curl http://localhost:8000/api/")
    
    print("\n💡 TIPS:")
    print("  • El panel admin requiere login: admin / admin123")
    print("  • Las APIs REST devuelven JSON")
    print("  • Usa /api/docs/ para ver documentación interactiva")
    print("  • localhost:8000 redirige automáticamente a /api/")
    
    if zones_count == 0 and devices_count == 0:
        print("\n⚠️  ADVERTENCIA: La base de datos está vacía!")
        print("   Ejecuta: python3 init_database.py")
    else:
        print("\n✅ Base de datos inicializada correctamente")
    
    print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    main()
