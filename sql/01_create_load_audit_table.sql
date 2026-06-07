CREATE TABLE IF NOT EXISTS audit.load_audit (
    load_id BIGSERIAL PRIMARY KEY,
    run_date DATE NOT NULL,
    source_name TEXT NOT NULL,
    source_file TEXT NOT NULL,
    target_schema TEXT NOT NULL,
    target_table TEXT NOT NULL,
    source_row_count INTEGER,
    loaded_row_count INTEGER,
    load_started_at TIMESTAMPTZ NOT NULL,
    load_finished_at TIMESTAMPTZ,
    status TEXT NOT NULL,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema = 'raw'
ORDER BY table_name;

SELECT
    run_date,
    source_name,
    source_file,
    target_schema,
    target_table,
    source_row_count,
    loaded_row_count,
    status,
    load_started_at,
    load_finished_at
FROM audit.load_audit
ORDER BY load_id DESC;


SELECT *
FROM audit.load_audit
WHERE status <> 'SUCCESS'
ORDER BY load_id DESC;