
# SQL Exploration Findings

## Purpose

This document summarizes the first SQL exploration of the PostgreSQL raw layer.

The goal is to understand the loaded data before designing staging tables, marts, or dbt models.

---

## Database Context

| Item | Value |
|---|---|
| Database | retail_analytics |
| Schema explored | raw |
| Main source | Olist e-commerce data |
| Additional source | Handmade supplier product updates |
| Exploration SQL | `sql/exploration/02_business_overview_queries.sql` |

---

## Key Findings

### Orders

- Most orders are expected to be in delivered status.
- Order status should be preserved as a categorical field.
- Order purchase timestamp will be important for monthly reporting.

### Revenue

- Item revenue is based on `raw.olist_order_items.price`.
- Freight value is stored separately and may be analyzed later.
- Revenue should be calculated carefully because one order can contain multiple items.

### Customers

- Customer state is useful for geographic analysis.
- Customer city/state should likely become part of a customer dimension later.

### Products

- Product category translation is useful for English reporting.
- Some product categories may be missing or untranslated and should be handled in staging.

### Payments

- Payment type can support payment behavior analysis.
- Payment value may not always equal item price because orders can include freight, installments, or multiple payment records.

### Reviews

- Review score can be joined to orders through `order_id`.
- Review analysis can later be connected to delivery delays and order status.

### Supplier Source

- Supplier quality flags are visible in PostgreSQL.
- Problematic supplier rows are preserved and flagged.
- Supplier data can later be joined to products through `product_id`, but missing product IDs must be handled.

---

## Important Modeling Observations

- `orders` is a central table.
- `order_items` is likely a fact-like table because it contains item-level price and seller/product relationships.
- `customers`, `products`, and `sellers` are likely dimension-like tables.
- `payments` may require aggregation at order level later.
- `reviews` may require careful handling because reviews are linked by order.
- Supplier updates should probably remain a separate source table first and later be integrated through product-level logic.

---

## Questions for Deeper Analysis

1. Which product categories generate the most revenue?
2. Which customer states have the highest order volume?
3. Which sellers have the highest revenue or delayed delivery risk?
4. How does delivery delay affect review score?
5. Which supplier update rows need business review before use?

---

## Next Data Engineering Decisions

The next step is to design the staging layer.

The staging layer should:

- cast date/time columns to timestamps
- cast numeric columns to numeric types
- standardize text fields where needed
- keep one staging model per main raw table
- preserve useful metadata columns
- prepare clean inputs for mart/fact/dimension models later

---

## Next Step

Proceed to staging design:

`Step 2.9 — Design PostgreSQL staging layer`