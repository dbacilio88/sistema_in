#!/usr/bin/env python3
"""
Script para mostrar tipos de infracciones disponibles
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from infractions.models import Infraction

print("\n" + "="*60)
print("📋 TIPOS DE INFRACCIONES DISPONIBLES")
print("="*60)

print("\n🚨 INFRACTION_TYPES:")
for code, name in Infraction.INFRACTION_TYPES:
    print(f"  • {code:15s} → {name}")

print("\n⚠️  SEVERITY_LEVELS:")
for code, name in Infraction.SEVERITY_LEVELS:
    print(f"  • {code:10s} → {name}")

print("\n📊 STATUS_CHOICES:")
for code, name in Infraction.STATUS_CHOICES:
    print(f"  • {code:10s} → {name}")

print("\n" + "="*60)
print("💡 CÓMO USAR:")
print("="*60)
print("""
Cuando creas una infracción, usa estos valores:

Ejemplo con curl:
curl -X POST http://localhost:8000/api/infractions/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "infraction_type": "red_light",
    "severity": "high",
    "status": "pending",
    "device": "<device_uuid>",
    "zone": "<zone_uuid>",
    "detected_at": "2025-11-04T20:00:00Z"
  }'

Ejemplo en Python:
infraction = Infraction.objects.create(
    infraction_type='red_light',
    severity='high',
    status='pending',
    device=device,
    zone=zone,
    detected_at=timezone.now()
)
""")

# Verificar si hay infracciones en la BD
total = Infraction.objects.count()
print(f"\n📊 Infracciones registradas en BD: {total}")

if total > 0:
    print("\n🚨 Últimas 5 infracciones:")
    for inf in Infraction.objects.all()[:5]:
        print(f"  • {inf.infraction_code} - {inf.get_infraction_type_display()}")
        print(f"    Fecha: {inf.detected_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"    Estado: {inf.get_status_display()}")
        print(f"    Severidad: {inf.get_severity_display()}")

print("\n" + "="*60 + "\n")
