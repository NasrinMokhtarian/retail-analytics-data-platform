from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.trigger_rule import TriggerRule


PROJECT_DIR = "/opt/airflow/project"
DBT_DIR = f"{PROJECT_DIR}/dbt_retail_analytics"

RUN_DATE = "{{ dag_run.conf.get('run_date', params.run_date) }}"
LOG_LEVEL = "{{ dag_run.conf.get('log_level', params.log_level) }}"

QUALITY_REPORT_PATH = (
    f"{PROJECT_DIR}/reports/br_holidays_quality/"
    f"run_date={RUN_DATE}/br_holidays_quality_checks.csv"
)

VALIDATION_REPORT_PATH = (
    f"{PROJECT_DIR}/reports/br_holidays_cleaning_validation/"
    f"run_date={RUN_DATE}/br_holidays_cleaning_validation_report.csv"
)


default_args = {
    "retries": 0,
}


with DAG(
    dag_id="br_holidays_api_refresh",
    description=(
        "Refresh Brazil public holidays API source and rebuild "
        "holiday-aware dbt models."
    ),
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["retail-analytics", "api", "br-holidays", "local"],
    params={
        "run_date": "2026-06-16",
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
            --pipeline-name br_holidays_api_refresh_airflow \
            --run-date {RUN_DATE} \
            --selected-source br_holidays
        """,
        do_xcom_push=True,
    )

    extract_br_holidays = BashOperator(
        task_id="extract_br_holidays",
        bash_command=f"""
        set -e
        cd {PROJECT_DIR}
        python -m retail_analytics.cli.br_holidays_extract \
            --run-date {RUN_DATE} \
            --log-level {LOG_LEVEL}
        """,
    )

    clean_br_holidays = BashOperator(
        task_id="clean_br_holidays",
        bash_command=f"""
        set -e
        cd {PROJECT_DIR}
        python -m retail_analytics.cli.br_holidays_cleaning \
            --run-date {RUN_DATE} \
            --log-level {LOG_LEVEL}
        """,
    )

    run_br_holidays_quality_checks = BashOperator(
        task_id="run_br_holidays_quality_checks",
        bash_command=f"""
        set -e
        cd {PROJECT_DIR}
        python -m retail_analytics.cli.br_holidays_quality \
            --run-date {RUN_DATE} \
            --log-level {LOG_LEVEL}
        """,
    )

    quality_gate = BashOperator(
        task_id="quality_gate",
        bash_command=f"""
        set -e
        cd {PROJECT_DIR}
        python -m retail_analytics.cli.check_report_gates \
            --report-path {QUALITY_REPORT_PATH} \
            --log-level {LOG_LEVEL}
        """,
    )

    validate_br_holidays_cleaning = BashOperator(
        task_id="validate_br_holidays_cleaning",
        bash_command=f"""
        set -e
        cd {PROJECT_DIR}
        python -m retail_analytics.cli.br_holidays_cleaning_validation \
            --run-date {RUN_DATE} \
            --log-level {LOG_LEVEL}
        """,
    )

    validation_gate = BashOperator(
        task_id="validation_gate",
        bash_command=f"""
        set -e
        cd {PROJECT_DIR}
        python -m retail_analytics.cli.check_report_gates \
            --report-path {VALIDATION_REPORT_PATH} \
            --log-level {LOG_LEVEL}
        """,
    )

    load_br_holidays_to_postgres = BashOperator(
        task_id="load_br_holidays_to_postgres",
        bash_command=f"""
        set -e
        cd {PROJECT_DIR}
        python -m retail_analytics.cli.load_cleaned_to_postgres \
            --br-holidays-run-date {RUN_DATE} \
            --only br_holidays \
            --log-level {LOG_LEVEL}
        """,
    )

    dbt_build_holiday_models = BashOperator(
        task_id="dbt_build_holiday_models",
        bash_command=f"""
        set -e
        cd {DBT_DIR}
        dbt build --select +fct_orders_holiday_context --profiles-dir .
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
        >> extract_br_holidays
        >> clean_br_holidays
        >> run_br_holidays_quality_checks
        >> quality_gate
        >> validate_br_holidays_cleaning
        >> validation_gate
        >> load_br_holidays_to_postgres
        >> dbt_build_holiday_models
        >> mark_pipeline_run_success
    )

    [
        extract_br_holidays,
        clean_br_holidays,
        run_br_holidays_quality_checks,
        quality_gate,
        validate_br_holidays_cleaning,
        validation_gate,
        load_br_holidays_to_postgres,
        dbt_build_holiday_models,
    ] >> mark_pipeline_run_failed