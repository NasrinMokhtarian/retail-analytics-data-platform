# New Source Integration Plan

## Purpose

This document defines how new data sources will be added to the Retail Analytics Data Platform.

The goal is to extend the project beyond static CSV files while keeping the architecture controlled, realistic, and production-style.

The project will add two new source types:

1. API enrichment source
2. Marketing campaign business dataset

These sources will be onboarded using the same disciplined pattern already used for Olist and supplier data.

---

## Current Project Context

The platform currently includes:

* Olist e-commerce source
* handmade supplier product update source
* local raw and processed data zones
* Python profiling, quality, cleaning, and validation
* PostgreSQL raw schema
* dbt staging and mart models
* Power BI dashboard built from dbt mart models

Current flow:

```text
source files
→ inventory/profile
→ quality checks
→ cleaning
→ cleaned validation
→ PostgreSQL raw loading
→ dbt staging
→ dbt marts
→ Power BI dashboard
```

The next step is to prove that the platform can evolve by onboarding additional source types.

---

## Source 3 — API Enrichment Source

### Source Type

External API source.

### Recommended Source

Holiday/calendar API.

### Business Purpose

The holiday/calendar source will enrich order analysis with calendar context.

Example business questions:

* Do order volumes change around holidays?
* Do delivery delays increase around holiday periods?
* Are some product categories more active before holidays?
* Should business reporting separate normal days from holiday periods?

### Expected Raw Format

API response in JSON format.

Example logical fields:

| field             | purpose                  |
| ----------------- | ------------------------ |
| holiday_date      | Calendar date            |
| holiday_name      | Holiday name             |
| country_code      | Country                  |
| local_name        | Local holiday name       |
| is_public_holiday | Public holiday flag      |
| source_system     | API source name          |
| extracted_at      | API extraction timestamp |
| run_date          | Pipeline run date        |

### Planned Local Folder Structure

```text
data/raw/api_holidays/run_date=YYYY-MM-DD/
data/processed/api_holidays_clean/run_date=YYYY-MM-DD/
reports/api_holidays_inventory/run_date=YYYY-MM-DD/
reports/api_holidays_profile/run_date=YYYY-MM-DD/
reports/api_holidays_quality/run_date=YYYY-MM-DD/
reports/api_holidays_validation/run_date=YYYY-MM-DD/
```

### Planned PostgreSQL Table

```text
raw.api_holidays
```

### Planned dbt Models

```text
dbt_staging.stg_api_holidays
dbt_mart.dim_calendar
```

The holiday source may later contribute to a calendar/date dimension.

### Planned BI Usage

Possible dashboard additions:

* revenue by holiday/non-holiday
* order count before/after holidays
* delivery delay around holidays
* category performance around holiday periods

---

## Source 4 — Marketing Campaign Dataset

### Source Type

Business dataset.

This will be a controlled handmade or semi-realistic CSV dataset.

### Business Purpose

The marketing campaign source will simulate commercial planning data.

Example business questions:

* Did campaigns increase revenue?
* Which campaigns were linked to higher order volume?
* Which product categories were targeted?
* Which customer states were targeted?
* Which campaign channels had the strongest business impact?

### Expected Fields

Planned columns:

| column          | purpose                               |
| --------------- | ------------------------------------- |
| campaign_id     | Campaign identifier                   |
| campaign_name   | Campaign name                         |
| start_date      | Campaign start date                   |
| end_date        | Campaign end date                     |
| target_category | Target product category               |
| target_state    | Target customer state                 |
| channel         | Marketing channel                     |
| budget          | Campaign budget                       |
| campaign_status | Planned, active, completed, cancelled |
| created_at      | Source creation timestamp             |
| run_date        | Pipeline run date                     |

### Planned Local Folder Structure

```text
data/raw/marketing_campaigns/run_date=YYYY-MM-DD/
data/processed/marketing_campaigns_clean/run_date=YYYY-MM-DD/
reports/marketing_campaigns_inventory/run_date=YYYY-MM-DD/
reports/marketing_campaigns_profile/run_date=YYYY-MM-DD/
reports/marketing_campaigns_quality/run_date=YYYY-MM-DD/
reports/marketing_campaigns_validation/run_date=YYYY-MM-DD/
```

### Planned PostgreSQL Table

```text
raw.marketing_campaigns
```

### Planned dbt Models

```text
dbt_staging.stg_marketing_campaigns
dbt_mart.dim_campaigns
```

Optional later mart:

```text
dbt_mart.fct_campaign_performance
```

### Planned BI Usage

Possible dashboard additions:

* campaign-period revenue
* campaign-period order volume
* revenue by target category
* order volume by target state
* campaign budget vs revenue proxy

---

## Required Onboarding Pattern

Each new source must follow the same onboarding pattern.

```text
1. Raw landing
2. Inventory
3. Profiling
4. Quality checks
5. Cleaning / normalization
6. Cleaned validation
7. PostgreSQL raw loading
8. dbt source definition
9. dbt staging model
10. dbt mart model
11. dbt tests and documentation
12. BI update
13. README and documentation update
```

No new source should bypass this process.

---

## What Not to Do

Do not add many new sources at once.

Do not add a source only because it looks interesting.

Do not connect new sources directly to Power BI before they pass through the pipeline.

Do not skip quality checks.

Do not build BI visuals from raw new-source tables.

The project must stay controlled and explainable.

---

## Recommended Implementation Order

### Step 5.2 — API Source Design

Define the holiday/calendar API fields, folder structure, quality rules, and extraction approach.

### Step 5.3 — API Extraction Script

Create a Python script that extracts API data and lands raw JSON.

### Step 5.4 — API Profiling and Quality Checks

Profile the API output and define quality rules.

### Step 5.5 — API Cleaning and Validation

Normalize the JSON into a clean tabular format and validate the cleaned output.

### Step 5.6 — Load API Source to PostgreSQL

Load the cleaned API source into the PostgreSQL `raw` schema.

### Step 5.7 — Add API Source to dbt

Create dbt source and staging model.

### Step 5.8 — Add Calendar/holiday Mart Logic

Create or enrich a calendar dimension.

### Step 5.9 — Marketing Dataset Design

Design the campaign dataset and quality rules.

### Step 5.10 — Marketing Source Onboarding

Inventory, profile, quality check, clean, validate, and load the marketing source.

### Step 5.11 — Add Marketing Source to dbt

Create dbt source, staging model, and campaign dimension.

### Step 5.12 — Update BI Dashboard

Add campaign and holiday-aware analysis.

---

## Decision

The next source to implement is:

```text
Source 3 — API holiday/calendar enrichment source
```

The marketing campaign dataset will be added after the API source is stable.
