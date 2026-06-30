from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.trigger_rule import TriggerRule

PROJECT_DIR = "/opt/airflow/project"
DBT_DIR = f"{PROJECT_DIR}/dbt_retail_analytics"

OLIST_RUN_DATE = "{{ dag_run.conf.get('olist_run_date', params.olist_run_date) }}"
SUPPLIER_RUN_DATE = "{{ dag_run.conf.get('supplier_run_date', params.supplier_run_date) }}"
BR_HOLIDAYS_RUN_DATE = "{{ dag_run.conf.get('br_holidays_run_date', params.br_holidays_run_date) }}"
VALIDATION_RUN_DATE = "{{ dag_run.conf.get('validation_run_date', params.validation_run_date) }}"
LOG_LEVEL = "{{ dag_run.conf.get('log_level', params.log_level) }}"

POSTGRES_VALIDATION_REPORT_PATH = (
    f"{PROJECT_DIR}/reports/postgres_validation/"
    f"run_date={VALIDATION_RUN_DATE}/postgres_load_validation_report.csv"
)

default_args = {
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
    "execution_timeout": timedelta(minutes=45),
}

with DAG(
    dag_id="retail_local_full_refresh",
    description=(
        "Full local refresh for the Retail Analytics Data Platform. "
        "Creates schemas, validates cleaned-file mappings, loads raw tables, "
        "validates PostgreSQL loads, applies report gates, and runs dbt build."
    ),
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    dagrun_timeout=timedelta(hours=2),
    tags=["retail-analytics", "local", "full-refresh"],
    params={
        "olist_run_date": "2026-05-26",
        "supplier_run_date": "2026-06-01",
        "br_holidays_run_date": "2026-06-16",
        "validation_run_date": "2026-06-16",
        "log_level": "INFO",
    },
) as dag:

    create_postgres_schemas = BashOperator(
        task_id="create_postgres_schemas",
        bash_command=f"""
        set -e
        cd {PROJECT_DIR}
        python -m retail_analytics.cli.create_postgres_schemas \
            --log-level {LOG_LEVEL}
        """,
    )

    create_load_audit_table = BashOperator(
        task_id="create_load_audit_table",
        bash_command=f"""
        set -e
        cd {PROJECT_DIR}
        python -m retail_analytics.cli.create_audit_table \
            --log-level {LOG_LEVEL}
        """,
    )

    start_pipeline_run = BashOperator(
        task_id="start_pipeline_run",
        bash_command=f"""
        set -e
        cd {PROJECT_DIR}
        python -m retail_analytics.cli.pipeline_audit start \
            --pipeline-name retail_local_full_refresh_airflow \
            --run-date {VALIDATION_RUN_DATE} \
            --selected-source olist supplier br_holidays
        """,
        do_xcom_push=True,
    )

    validate_cleaned_file_mappings = BashOperator(
        task_id="validate_cleaned_file_mappings",
        bash_command=f"""
        set -e
        cd {PROJECT_DIR}
        python -m retail_analytics.cli.validate_postgres_load_config \
            --olist-run-date {OLIST_RUN_DATE} \
            --supplier-run-date {SUPPLIER_RUN_DATE} \
            --br-holidays-run-date {BR_HOLIDAYS_RUN_DATE} \
            --only olist supplier br_holidays \
            --log-level {LOG_LEVEL}
        """,
    )

    load_raw_tables = BashOperator(
        task_id="load_raw_tables",
        bash_command=f"""
        set -e
        cd {PROJECT_DIR}
        python -m retail_analytics.cli.load_cleaned_to_postgres \
            --olist-run-date {OLIST_RUN_DATE} \
            --supplier-run-date {SUPPLIER_RUN_DATE} \
            --br-holidays-run-date {BR_HOLIDAYS_RUN_DATE} \
            --only olist supplier br_holidays \
            --log-level {LOG_LEVEL}
        """,
    )

    validate_raw_loads = BashOperator(
        task_id="validate_raw_loads",
        bash_command=f"""
        set -e
        cd {PROJECT_DIR}
        python -m retail_analytics.cli.validate_postgres_loads \
            --olist-run-date {OLIST_RUN_DATE} \
            --supplier-run-date {SUPPLIER_RUN_DATE} \
            --br-holidays-run-date {BR_HOLIDAYS_RUN_DATE} \
            --validation-run-date {VALIDATION_RUN_DATE} \
            --only olist supplier br_holidays \
            --log-level {LOG_LEVEL}
        """,
    )

    postgres_validation_gate = BashOperator(
        task_id="postgres_validation_gate",
        bash_command=f"""
        set -e
        cd {PROJECT_DIR}
        python -m retail_analytics.cli.check_report_gates \
            --report-path {POSTGRES_VALIDATION_REPORT_PATH} \
            --log-level {LOG_LEVEL}
        """,
    )

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=f"""
        set -e
        cd {DBT_DIR}
        dbt build --profiles-dir .
        """,
    )

    mark_pipeline_run_success = BashOperator(
        task_id="mark_pipeline_run_success",
        bash_command=f"""
        set -e
        cd {PROJECT_DIR}
        python -m retail_analytics.cli.pipeline_audit finish \
            --pipeline-run-id "{{{{ ti.xcom_pull(task_ids='start_pipeline_run') | trim }}}}" \
            --status SUCCESS
        """,
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    mark_pipeline_run_failed = BashOperator(
        task_id="mark_pipeline_run_failed",
        bash_command=f"""
        set -e
        cd {PROJECT_DIR}
        python -m retail_analytics.cli.pipeline_audit finish \
            --pipeline-run-id "{{{{ ti.xcom_pull(task_ids='start_pipeline_run') | trim }}}}" \
            --status FAILED \
            --error-message "Airflow DAG failed. Check task logs for details."
        """,
        trigger_rule=TriggerRule.ONE_FAILED,
    )

    (
        create_postgres_schemas
        >> create_load_audit_table
        >> start_pipeline_run
        >> validate_cleaned_file_mappings
        >> load_raw_tables
        >> validate_raw_loads
        >> postgres_validation_gate
        >> dbt_build
        >> mark_pipeline_run_success
    )

    [
        validate_cleaned_file_mappings,
        load_raw_tables,
        validate_raw_loads,
        postgres_validation_gate,
        dbt_build,
    ] >> mark_pipeline_run_failed