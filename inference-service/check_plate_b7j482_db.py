#!/usr/bin/env python3
"""
Script para verificar infracciones de la placa B7J-482 en la base de datos
"""
import requests
import json
from datetime import datetime

BACKEND_URL = "http://localhost:8000"

print("=" * 70)
print("🔍 VERIFICANDO INFRACCIONES PARA PLACA B7J-482")
print("=" * 70)
print()

try:
    # Obtener todas las infracciones
    response = requests.get(f"{BACKEND_URL}/api/infractions/")
    
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        
        print(f"📊 Total infracciones en BD: {len(results)}")
        print()
        
        # Filtrar por placa B7J-482 (considerar variaciones)
        target_plates = ['B7J-482', 'B7J482', 'B7J 482']
        b7j482_infractions = []
        
        for infraction in results:
            plate = infraction.get('license_plate_detected', '').upper()
            # Limpiar espacios y guiones
            clean_plate = plate.replace(' ', '').replace('-', '')
            
            if any(clean_plate == tp.replace(' ', '').replace('-', '') for tp in target_plates):
                b7j482_infractions.append(infraction)
        
        print(f"🚗 Infracciones para placa B7J-482: {len(b7j482_infractions)}")
        print()
        
        if b7j482_infractions:
            print("📋 Detalles de las infracciones:")
            print("-" * 70)
            
            for idx, infraction in enumerate(b7j482_infractions, 1):
                print(f"\n{idx}. Infracción ID: {infraction.get('id')}")
                print(f"   Código: {infraction.get('infraction_code')}")
                print(f"   Tipo: {infraction.get('infraction_type')}")
                print(f"   Placa detectada: {infraction.get('license_plate_detected')}")
                print(f"   Confianza placa: {infraction.get('license_plate_confidence', 0):.2f}")
                print(f"   Estado: {infraction.get('status')}")
                print(f"   Severidad: {infraction.get('severity')}")
                print(f"   Velocidad detectada: {infraction.get('detected_speed', 'N/A')} km/h")
                print(f"   Límite velocidad: {infraction.get('speed_limit', 'N/A')} km/h")
                print(f"   Detectado en: {infraction.get('detected_at')}")
                
                # Metadata
                metadata = infraction.get('evidence_metadata', {})
                if metadata:
                    print(f"   Tipo vehículo: {metadata.get('vehicle_type', 'N/A')}")
                    print(f"   Confianza detección: {metadata.get('confidence', 0):.2f}")
                    print(f"   BBox: {metadata.get('bbox', 'N/A')}")
        else:
            print("⚠️  No se encontraron infracciones para la placa B7J-482")
            print()
            print("💡 Placas encontradas en la BD:")
            unique_plates = set()
            for infraction in results:
                plate = infraction.get('license_plate_detected', '').strip()
                if plate:
                    unique_plates.add(plate)
            
            for plate in sorted(unique_plates):
                print(f"   - {plate}")
        
        print()
        print("=" * 70)
        print("✅ Verificación completada")
        print("=" * 70)
        
    else:
        print(f"❌ Error al consultar API: {response.status_code}")
        print(response.text)

except requests.exceptions.ConnectionError:
    print("❌ Error: No se pudo conectar al backend en", BACKEND_URL)
    print("   Verifica que el backend Django esté corriendo")
except Exception as e:
    print(f"❌ Error inesperado: {str(e)}")
