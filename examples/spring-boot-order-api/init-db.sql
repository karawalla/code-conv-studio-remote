-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS orderdb_dev;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE orderdb TO orderuser;
GRANT ALL PRIVILEGES ON DATABASE orderdb_dev TO orderuser;
