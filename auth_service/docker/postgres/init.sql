-- PostgreSQL initialization script for Docker
-- This script runs when the PostgreSQL container starts for the first time

-- Create additional databases for testing
CREATE DATABASE auth_service_test_db;

-- Create user with appropriate permissions (if needed)
-- Note: The default postgres user is already created by the container

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE auth_service_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE auth_service_test_db TO postgres;

-- Log successful initialization
\echo 'PostgreSQL databases initialized successfully!'
\echo 'Main database: auth_service_db'
\echo 'Test database: auth_service_test_db'
