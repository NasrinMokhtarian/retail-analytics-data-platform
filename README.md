# Retail Analytics Data Platform

A production-style, incremental data engineering project built around realistic retail/e-commerce data workflows.

---

## Project Purpose

This project supports my transition into the data job market as a career changer with a technical background but no commercial data engineering experience yet.

This repository is intentionally built incrementally.  
It starts with local data ingestion, profiling, cleaning, and SQL practice before moving into PostgreSQL, dbt, Spark, orchestration, and cloud integration.

---

## Business Context

The project is a retail analytics data platform for an e-commerce business.

The business wants to understand:

- order volume,
- customer behavior,
- product performance,
- seller performance,
- delivery performance,
- payment behavior,
- customer reviews,
- and operational data quality.

The initial dataset is a  E-Commerce dataset, which contains realistic e-commerce data such as customers, orders, products, payments, sellers, reviews, and geolocation.

Additional source types will be introduced gradually to simulate a more realistic data environment.

---

## Data Sources

### Current Source

| Source | Type | Status |
|---|---|---|
| Commerce Dataset | CSV, API, transactional Database | In progress |

### Planned Additional Sources

| Source Type | Purpose |
|---|---|
| JSON API | Practice API extraction, JSON parsing, error handling, and incremental ingestion |
| Messy Excel files | Simulate supplier/business files with inconsistent structure |
| Semi-structured JSON data | Practice nested data handling, flattening, schema drift, and event-style data |

The project starts with CSV files, but it is not intended to remain a CSV-only project.  
The long-term goal is to build a repeatable source onboarding pattern that can support different source types.

---

## Engineering Principles

This project follows production-style thinking from the beginning, without adding unnecessary complexity too early.

### Current Project Structure
retail-analytics-data-platform/
│
├── data/
│   ├── raw/
│   │   └── olist/
│   └── processed/
│
├── docs/
│
├── reports/
│   ├── raw_inventory/
│   └── raw_profile/
│
├── sql/
│
├── src/
│   └── retail_analytics/
│       ├── __init__.py
│       ├── config.py
│       │
│       ├── cli/
│       │   ├── __init__.py
│       │   ├── raw_inventory.py
│       │   └── raw_profile.py
│       │
│       ├── ingestion/
│       │   ├── __init__.py
│       │   └── raw_inventory.py
│       │
│       ├── profiling/
│       │   ├── __init__.py
│       │   └── raw_profile.py
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   ├── raw_inventory.py
│       │   └── raw_profile.py
│       │
│       ├── validations/
│       │   ├── __init__.py
│       │   ├── raw_files.py
│       │   └── run_date.py
│       │
│       └── utils/
│           ├── __init__.py
│           └── logging.py
│
├── tests/
├── pyproject.toml
├── requirements.txt
├── README.md
└── .gitignore

---

## Current Implementation Status

### Completed

- Project structure created
- Python package structure using `src/`
- Configuration module
- Structured JSON logging
- CLI entry point pattern
- Raw file inventory job
- Raw column profiling job

### Current Phase

The project is currently in:

```text
Phase 1 — Local raw data ingestion, inspection, profiling, and onboarding other resources -> Done
Phase 2 - PostgreSQL Loading and SQL Practice
```
### Planned Project Roadmap
- Phase 1 — Local Ingestion, Inspection, and Profiling
- Phase 2 — PostgreSQL Loading and SQL Practice
- Phase 3 — Data Modeling
- Phase 4 — dbt Basics
- Phase 6 — PySpark / Spark Transformations
- Phase 7 — Orchestration, Testing, Logging, Monitoring, and Docker
- Phase 8 — Cloud Integration
