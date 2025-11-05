#!/usr/bin/env python3
"""
Script rápido para verificar si hay datos en la base de datos
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from devices.models import Zone, Device
from vehicles.models import Vehicle
from infractions.models import Infraction
from django.contrib.auth.models import User

print("\n" + "="*50)
print("📊 CONTEO DE REGISTROS")
print("="*50)

users = User.objects.count()
zones = Zone.objects.count()
devices = Device.objects.count()
vehicles = Vehicle.objects.count()
infractions = Infraction.objects.count()

print(f"👥 Usuarios:     {users}")
print(f"📍 Zonas:        {zones}")
print(f"📹 Dispositivos: {devices}")
print(f"🚗 Vehículos:    {vehicles}")
print(f"🚨 Infracciones: {infractions}")
print("="*50)

if zones == 0 and devices == 0 and users == 0:
    print("\n❌ Base de datos VACÍA")
    print("\n▶️  Ejecuta: python3 init_database.py")
else:
    print("\n✅ Hay datos en la base de datos")
    if zones > 0:
        print(f"\n📍 Zonas registradas:")
        for z in Zone.objects.all():
            print(f"   • {z.code} - {z.name} (límite: {z.speed_limit} km/h)")
    if devices > 0:
        print(f"\n📹 Dispositivos registrados:")
        for d in Device.objects.all():
            print(f"   • {d.code} - {d.name} (zona: {d.zone.name})")
    if users > 0:
        print(f"\n👥 Usuarios registrados:")
        for u in User.objects.all():
            print(f"   • {u.username} (superuser: {u.is_superuser})")

print()
