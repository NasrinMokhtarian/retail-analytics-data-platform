# Source Onboarding Pattern

## Purpose

This document defines the standard onboarding pattern for every data source in the Retail Analytics Data Platform project.
The purpose is to avoid creating random one-off scripts for each source. Every source should enter the project through a clear, repeatable, and documented process.
This pattern supports a production-style engineering mindset while keeping the implementation realistic and incremental.

---

## Why This Pattern Exists

In a real company, data does not come from only one clean CSV dataset.
Data may arrive from:

- CSV exports
- Excel files from suppliers or business teams
- JSON APIs
- semi-structured event files
- operational databases
- cloud storage locations

Even when source types are different, the engineering workflow should be consistent.

The standard lifecycle is:

- land raw → inventory → profile → quality check → clean → validate → document → load later

```text
land raw source
→ inspect/inventory
→ profile
→ review findings
→ run quality checks
→ define cleaning rules
→ clean/standardize
→ validate cleaned output
→ document decisions
→ load to database or warehouse later

→ This supplier file intentionally contains issues:

| Issue                   | Example                          |
| ----------------------- | -------------------------------- |
| Extra spaces            | supplier names and product codes |
| Mixed casing            | `EUR`, `eur`, `in stock`         |
| Missing product ID      | one row has empty `product_id`   |
| Price as text           | `not available`                  |
| Comma decimal separator | `120,50`                         |
| Negative price          | `-10.00`                         |
| Invalid timestamp       | `invalid_date`                   |
| Missing currency        | empty `currency`                 |
| Missing valid_from      | empty `valid_from`               |
| Unknown category/status | `unknown` stock status           |
| Duplicate row           | repeated Orion Components row    |
