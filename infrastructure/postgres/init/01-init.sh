#!/bin/bash
set -e

echo "Initializing PostgreSQL database for Traffic System..."

# Create extensions
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Enable core extensions
    CREATE EXTENSION IF NOT EXISTS postgis;
    CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- For text search
    CREATE EXTENSION IF NOT EXISTS btree_gin;  -- For JSONB indexing
    CREATE EXTENSION IF NOT EXISTS pg_stat_statements;  -- For query monitoring
    CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- For additional crypto functions

    -- Create schemas
    CREATE SCHEMA IF NOT EXISTS public;
    CREATE SCHEMA IF NOT EXISTS timeseries;
    CREATE SCHEMA IF NOT EXISTS analytics;

    -- Set default privileges
    GRANT ALL PRIVILEGES ON SCHEMA public TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON SCHEMA timeseries TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON SCHEMA analytics TO $POSTGRES_USER;

    -- Create function for updating updated_at timestamp
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS \$\$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    \$\$ LANGUAGE plpgsql;

    -- Create sequence for infraction codes
    CREATE SEQUENCE IF NOT EXISTS infraction_code_seq START 1;

    -- Grant permissions on existing objects
    GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO $POSTGRES_USER;

    -- Grant permissions on future objects
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $POSTGRES_USER;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $POSTGRES_USER;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO $POSTGRES_USER;
    
    -- Create database for MLflow (if needed)
    CREATE DATABASE IF NOT EXISTS mlflow OWNER $POSTGRES_USER;

    -- Verify extensions are loaded
    SELECT extname, extversion FROM pg_extension WHERE extname IN ('postgis', 'timescaledb', 'uuid-ossp');
EOSQL

echo "PostgreSQL initialization completed successfully!"
echo "Extensions installed:"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -c "SELECT extname, extversion FROM pg_extension ORDER BY extname;"
