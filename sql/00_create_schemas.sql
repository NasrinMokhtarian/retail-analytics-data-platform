CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS mart;
CREATE SCHEMA IF NOT EXISTS audit;

SELECT schema_name
FROM information_schema.schemata
WHERE schema_name IN ('raw', 'staging', 'mart', 'audit')
ORDER BY schema_name;