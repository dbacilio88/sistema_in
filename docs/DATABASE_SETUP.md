# Database Setup Guide

## PostgreSQL Configuration

### Required Extensions

The system requires the following PostgreSQL extensions:

- **PostGIS**: Geographic data support for device locations and zones
- **TimescaleDB**: Time-series data for events and analytics  
- **uuid-ossp**: UUID generation for primary keys
- **pg_trgm**: Text search functionality
- **btree_gin**: JSONB indexing
- **pg_stat_statements**: Query monitoring
- **pgcrypto**: Additional cryptographic functions

### Database Schema

The system creates the following schemas:

- `public`: Main application tables
- `timeseries`: TimescaleDB hypertables for time-series data
- `analytics`: Analytics and reporting tables

### Main Tables

#### Authentication
- `authentication_customuser`: Custom user model with roles
- `authentication_loginhistory`: Login tracking for security

#### Devices & Zones
- `devices_zone`: Traffic zones with geographic boundaries
- `devices_device`: IoT cameras and sensors
- `devices_deviceevent`: Device status events (TimescaleDB)

#### Vehicles & Drivers
- `vehicles_vehicle`: Vehicle registration data
- `vehicles_driver`: Driver/person information
- `vehicles_vehicleownership`: Vehicle-driver relationships

#### Infractions
- `infractions_infraction`: Main infractions table
- `infractions_infractionevent`: Infraction lifecycle events (TimescaleDB)
- `infractions_appeal`: Appeal submissions

### TimescaleDB Hypertables

The following tables are configured as TimescaleDB hypertables for optimal time-series performance:

- `devices_deviceevent`: Partitioned by `timestamp`
- `infractions_infractionevent`: Partitioned by `timestamp`

### Initial Data

The `seed_data.py` script creates:

#### Users
- **admin** (admin role): Full system access
- **supervisor** (supervisor role): Review and validate infractions
- **operator** (operator role): Monitor devices and basic operations
- **auditor** (auditor role): Read-only access for auditing

#### Zones
- **ZN001 - Centro de Lima**: 40 km/h speed limit
- **ZN002 - Av. Javier Prado**: 60 km/h speed limit  
- **ZN003 - Zona Escolar San Isidro**: 30 km/h speed limit

#### Devices
- **CAM001**: Plaza de Armas camera (EZVIZ H6C Pro 2K)
- **CAM002**: Javier Prado Este camera
- **CAM003**: School zone camera

#### Sample Data
- 3 test drivers with valid licenses
- 3 test vehicles with SUNARP data
- Sample traffic infractions with evidence

## Setup Commands

### 1. Initialize Database

```bash
# Run PostgreSQL initialization script
docker-compose up postgres

# Wait for PostgreSQL to be ready
docker-compose exec postgres pg_isready

# Verify extensions are installed
docker-compose exec postgres psql -U admin -d traffic_system -c "SELECT extname, extversion FROM pg_extension ORDER BY extname;"
```

### 2. Run Django Migrations

```bash
# Create and apply migrations
docker-compose exec django python manage.py makemigrations
docker-compose exec django python manage.py migrate

# Verify tables were created
docker-compose exec postgres psql -U admin -d traffic_system -c "\dt"
```

### 3. Load Seed Data

```bash
# Run seed data script
docker-compose exec django python seed_data.py

# Verify data was loaded
docker-compose exec django python manage.py shell -c "
from django.contrib.auth import get_user_model
from devices.models import Zone, Device
from infractions.models import Infraction
User = get_user_model()
print(f'Users: {User.objects.count()}')
print(f'Zones: {Zone.objects.count()}')
print(f'Devices: {Device.objects.count()}')
print(f'Infractions: {Infraction.objects.count()}')
"
```

### 4. Verify Connections

```bash
# Test all database connections
docker-compose exec django python verify_connections.py

# Test FastAPI connection separately
docker-compose exec inference python -c "
import asyncio
import asyncpg

async def test():
    conn = await asyncpg.connect('postgresql://admin:SecurePassword123!@postgres:5432/traffic_system')
    result = await conn.fetchval('SELECT COUNT(*) FROM authentication_customuser')
    print(f'FastAPI can read {result} users from database')
    await conn.close()

asyncio.run(test())
"
```

## Troubleshooting

### Common Issues

1. **PostGIS not found**
   ```bash
   # Install PostGIS in the container
   docker-compose exec postgres apt-get update
   docker-compose exec postgres apt-get install -y postgis
   ```

2. **TimescaleDB not initialized**
   ```bash
   # Check TimescaleDB is loaded
   docker-compose exec postgres psql -U admin -d traffic_system -c "SELECT * FROM pg_extension WHERE extname='timescaledb';"
   ```

3. **Permission denied errors**
   ```bash
   # Grant permissions
   docker-compose exec postgres psql -U admin -d traffic_system -c "
   GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;
   GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO admin;
   "
   ```

4. **Django migrations fail**
   ```bash
   # Reset migrations (development only)
   docker-compose exec django find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
   docker-compose exec django python manage.py makemigrations
   ```

### Performance Optimization

#### Indexes
Key indexes are automatically created:
- Device location (spatial index)
- Infraction timestamps
- License plate lookups
- User authentication

#### TimescaleDB Compression
Enable compression for older data:
```sql
-- Compress data older than 7 days
SELECT add_compression_policy('devices_deviceevent', INTERVAL '7 days');
SELECT add_compression_policy('infractions_infractionevent', INTERVAL '7 days');
```

#### Connection Pooling
For production, configure connection pooling:
- Django: Use `django-db-pool`
- FastAPI: Use `asyncpg` connection pools

### Security Considerations

1. **Change default passwords** in production
2. **Enable SSL** for database connections
3. **Restrict network access** to database ports
4. **Regular backups** with encryption
5. **Monitor query performance** with `pg_stat_statements`

### Monitoring Queries

```sql
-- Check database size
SELECT pg_database_size('traffic_system')/1024/1024 AS size_mb;

-- Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check active connections
SELECT count(*) FROM pg_stat_activity WHERE state = 'active';

-- Check slow queries
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;
```