# Offline cleanup checkpoint

## Verified state

- The repository already contains two Airflow DAGs:
  - `retail_local_full_refresh`
  - `br_holidays_api_refresh`
- Those DAGs orchestrate the legacy/local PostgreSQL workflow.
- The current cloud dbt project is `dbt/` and targets Redshift.
- CI should validate `dbt/`, not only `dbt_retail_analytics/`.
- CI parsing must not require AWS credentials or execute Redshift queries.
- The Airflow image can include both dbt adapters so the existing local DAG remains usable while Redshift tooling is also available.

## Cost behavior

The CI workflow runs `dbt parse` only. It does not run `dbt build` and therefore does not consume Redshift Serverless RPUs.

## Orchestration boundary

Keep the two existing Airflow DAGs as local orchestration examples for now. Do not schedule Redshift `dbt build` automatically while the warehouse is protected by a usage limit. A manual/on-demand cloud dbt DAG can be added only after final Redshift execution validation is green.
