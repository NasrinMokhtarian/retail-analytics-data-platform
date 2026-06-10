# dbt Migration Summary

## Purpose

This document summarizes the dbt migration work completed for the Retail Analytics Data Platform project.

The goal of this phase was to move the validated PostgreSQL staging and mart SQL logic into dbt, making the transformation layer more maintainable, testable, documented, and explainable.

---

## Why dbt Was Added

The project first used manually written PostgreSQL SQL views for staging and mart layers.

This was intentional.

The manual SQL phase helped validate:

- raw-to-staging transformation logic
- data type casting
- business keys
- table grain
- joins
- fact and dimension design
- delivery metrics
- revenue metrics
- supplier quality flags
- business analysis outputs

After the SQL logic was stable, it was migrated into dbt.

This reflects a realistic analytics engineering workflow:

```text
manual SQL prototype
→ validation
→ dbt migration
→ tests
→ documentation
→ lineage