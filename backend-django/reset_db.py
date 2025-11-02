#!/usr/bin/env python3
"""
Script para limpiar la base de datos completamente
"""
import psycopg2
import os
import sys

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Leer variables de entorno desde .env
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR.parent, '.env'))

# Configuración de la base de datos
DB_CONFIG = {
    'dbname': env('POSTGRES_DB', default='traffic_infractions'),
    'user': env('POSTGRES_USER', default='admin'),
    'password': env('POSTGRES_PASSWORD', default='admin123'),
    'host': env('POSTGRES_HOST', default='localhost'),
    'port': env('POSTGRES_PORT', default='5432'),
}

def reset_database():
    """Elimina y recrea el esquema public"""
    try:
        print(f"Conectando a la base de datos {DB_CONFIG['dbname']}...")
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("Eliminando esquema public...")
        cursor.execute("DROP SCHEMA IF EXISTS public CASCADE;")
        
        print("Recreando esquema public...")
        cursor.execute("CREATE SCHEMA public;")
        
        print("Otorgando permisos...")
        cursor.execute(f"GRANT ALL ON SCHEMA public TO {DB_CONFIG['user']};")
        cursor.execute("GRANT ALL ON SCHEMA public TO public;")
        
        cursor.close()
        conn.close()
        
        print("✅ Base de datos limpiada exitosamente!")
        print("\nAhora ejecuta:")
        print("  make makemigrations")
        print("  make migrate")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    import sys
    
    response = input("⚠️  Esto eliminará TODOS los datos. ¿Continuar? (yes/no): ")
    if response.lower() == 'yes':
        success = reset_database()
        sys.exit(0 if success else 1)
    else:
        print("Operación cancelada.")
        sys.exit(0)
