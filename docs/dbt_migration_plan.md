# dbt Migration Plan

## Purpose

This document defines the plan for migrating the validated PostgreSQL staging and mart SQL logic into dbt.

The goal is not to restart the project. The goal is to formalize the SQL transformation layer using dbt after the logic has already been designed, tested, and validated in PostgreSQL.

---

## Current Context

The project currently has:

- local source onboarding
- data profiling
- data quality checks
- cleaning and validation
- PostgreSQL raw tables
- PostgreSQL staging views
- PostgreSQL mart views
- SQL validation queries
- business analysis queries

Current transformation SQL exists in:

```text
sql/staging/
sql/mart/
```
## Target dbt Project Structure
dbt_retail_analytics/
├── dbt_project.yml
├── profiles.yml.example
├── models/
│   ├── sources.yml
│   ├── staging/
│   │   ├── stg_customers.sql
│   │   ├── stg_orders.sql
│   │   ├── stg_order_items.sql
│   │   ├── stg_order_payments.sql
│   │   ├── stg_order_reviews.sql
│   │   ├── stg_products.sql
│   │   ├── stg_sellers.sql
│   │   ├── stg_product_category_translation.sql
│   │   └── stg_supplier_product_updates.sql
│   └── marts/
│       ├── dim_customers.sql
│       ├── dim_products.sql
│       ├── dim_sellers.sql
│       ├── fct_orders.sql
│       ├── fct_order_items.sql
│       ├── fct_payments.sql
│       ├── fct_reviews.sql
│       └── fct_supplier_product_updates.sql