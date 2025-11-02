#!/usr/bin/env python3
"""
Database connection verification script
Tests connections from both Django ORM and FastAPI asyncpg
"""
import os
import sys
import asyncio
import asyncpg
from datetime import datetime

# Django setup
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.db import connection
from django.contrib.auth import get_user_model
from devices.models import Zone, Device
from vehicles.models import Vehicle
from infractions.models import Infraction

User = get_user_model()

def test_django_connection():
    """Test Django ORM connection"""
    print("🔍 Testing Django ORM connection...")
    
    try:
        # Test basic connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"✅ PostgreSQL version: {version}")
        
        # Test Django queries
        user_count = User.objects.count()
        zone_count = Zone.objects.count()
        device_count = Device.objects.count()
        vehicle_count = Vehicle.objects.count()
        infraction_count = Infraction.objects.count()
        
        print(f"✅ Django ORM queries successful:")
        print(f"   👥 Users: {user_count}")
        print(f"   🗺️ Zones: {zone_count}")
        print(f"   📹 Devices: {device_count}")
        print(f"   🚗 Vehicles: {vehicle_count}")
        print(f"   🚨 Infractions: {infraction_count}")
        
        # Test PostGIS functionality
        if zone_count > 0:
            zone = Zone.objects.first()
            print(f"✅ PostGIS test - Zone center: {zone.center_point}")
        
        # Test foreign key relationships
        if infraction_count > 0:
            infraction = Infraction.objects.select_related('device', 'zone').first()
            print(f"✅ Relationship test - Infraction {infraction.infraction_code} from device {infraction.device.code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Django connection failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_fastapi_connection():
    """Test FastAPI asyncpg connection"""
    print("\n🔍 Testing FastAPI asyncpg connection...")
    
    try:
        # Database URL from Django settings
        from django.conf import settings
        db_config = settings.DATABASES['default']
        
        # Build asyncpg connection string
        db_url = f"postgresql://{db_config['USER']}:{db_config['PASSWORD']}@{db_config['HOST']}:{db_config['PORT']}/{db_config['NAME']}"
        
        # Test connection
        conn = await asyncpg.connect(db_url)
        
        # Test basic query
        version = await conn.fetchval("SELECT version();")
        print(f"✅ AsyncPG connection successful")
        print(f"✅ PostgreSQL version: {version}")
        
        # Test table queries
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        
        print(f"✅ Found {len(tables)} tables:")
        for table in tables[:10]:  # Show first 10 tables
            print(f"   📄 {table['table_name']}")
        if len(tables) > 10:
            print(f"   ... and {len(tables) - 10} more")
        
        # Test extensions
        extensions = await conn.fetch("""
            SELECT extname, extversion 
            FROM pg_extension 
            WHERE extname IN ('postgis', 'timescaledb', 'uuid-ossp')
            ORDER BY extname;
        """)
        
        print(f"✅ Extensions installed:")
        for ext in extensions:
            print(f"   🔧 {ext['extname']} v{ext['extversion']}")
        
        # Test TimescaleDB hypertables
        hypertables = await conn.fetch("""
            SELECT hypertable_name, num_dimensions 
            FROM timescaledb_information.hypertables;
        """)
        
        if hypertables:
            print(f"✅ TimescaleDB hypertables:")
            for ht in hypertables:
                print(f"   ⏰ {ht['hypertable_name']} ({ht['num_dimensions']} dimensions)")
        else:
            print("ℹ️ No TimescaleDB hypertables found (will be created later)")
        
        # Test data queries
        user_count = await conn.fetchval("SELECT COUNT(*) FROM authentication_customuser;")
        print(f"✅ AsyncPG data query - Users: {user_count}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ FastAPI asyncpg connection failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_redis_connection():
    """Test Redis connection"""
    print("\n🔍 Testing Redis connection...")
    
    try:
        import redis
        from django.conf import settings
        
        # Get Redis URL from settings
        redis_url = getattr(settings, 'REDIS_URL', 'redis://redis:6379/0')
        
        # Test connection
        r = redis.from_url(redis_url)
        r.ping()
        
        # Test basic operations
        test_key = f"test_connection_{datetime.now().timestamp()}"
        r.set(test_key, "test_value", ex=10)  # Expire in 10 seconds
        value = r.get(test_key)
        
        print(f"✅ Redis connection successful")
        print(f"✅ Redis test key/value operation successful")
        
        # Get Redis info
        info = r.info()
        print(f"✅ Redis version: {info.get('redis_version', 'unknown')}")
        print(f"✅ Connected clients: {info.get('connected_clients', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis connection failed: {str(e)}")
        return False

async def main():
    """Run all connection tests"""
    print("🔍 Database Connection Verification")
    print("=" * 50)
    print(f"🕐 Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Test Django connection
    django_ok = test_django_connection()
    
    # Test FastAPI connection
    fastapi_ok = await test_fastapi_connection()
    
    # Test Redis connection
    redis_ok = test_redis_connection()
    
    print("\n" + "=" * 50)
    print("📊 Connection Test Summary:")
    print(f"   🐍 Django ORM: {'✅ OK' if django_ok else '❌ FAILED'}")
    print(f"   ⚡ FastAPI AsyncPG: {'✅ OK' if fastapi_ok else '❌ FAILED'}")
    print(f"   🔴 Redis: {'✅ OK' if redis_ok else '❌ FAILED'}")
    
    all_ok = django_ok and fastapi_ok and redis_ok
    print(f"\n🎯 Overall Status: {'✅ ALL CONNECTIONS OK' if all_ok else '❌ SOME CONNECTIONS FAILED'}")
    
    if not all_ok:
        print("\n💡 Troubleshooting tips:")
        if not django_ok:
            print("   - Check Django database settings in settings.py")
            print("   - Ensure PostgreSQL is running and accessible")
        if not fastapi_ok:
            print("   - Check asyncpg connection string format")
            print("   - Ensure PostgreSQL allows connections from FastAPI service")
        if not redis_ok:
            print("   - Check Redis URL configuration")
            print("   - Ensure Redis service is running")
        
        sys.exit(1)
    else:
        print("\n🎉 All database connections are working correctly!")

if __name__ == '__main__':
    asyncio.run(main())