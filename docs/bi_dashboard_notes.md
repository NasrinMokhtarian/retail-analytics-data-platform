# BI Dashboard Notes

## Purpose

This document describes the Power BI dashboard created for the Retail Analytics Data Platform project.

The dashboard is built on top of the validated dbt mart layer, not on raw tables.

The goal is to show how the data platform supports business-facing analysis after the full workflow:

```text
source onboarding
→ profiling
→ quality checks
→ cleaning
→ PostgreSQL loading
→ dbt staging models
→ dbt mart models
→ Power BI dashboard
```

## BI Tool
The dashboard was built using:

* Power BI Desktop
* Local PostgreSQL connection
 Import mode

Power BI connects to the local PostgreSQL database and imports the dbt mart views from the dbt_mart schema.

## Data Source Used by Power BI
Power BI uses only the dbt_mart schema.

Loaded views:

| dbt mart view                           | purpose                              |
| --------------------------------------- | ------------------------------------ |
| `dbt_mart.dim_customers`                | Customer geography                   |
| `dbt_mart.dim_products`                 | Product attributes and categories    |
| `dbt_mart.dim_sellers`                  | Seller geography                     |
| `dbt_mart.fct_orders`                   | Order lifecycle and delivery metrics |
| `dbt_mart.fct_order_items`              | Item-level revenue                   |
| `dbt_mart.fct_payments`                 | Payment behavior                     |
| `dbt_mart.fct_reviews`                  | Review scores and sentiment          |
| `dbt_mart.fct_supplier_product_updates` | Supplier data-quality review         |

## Why Power BI Uses dbt Mart Models

Power BI does not connect directly to raw tables.

Reason:

* raw tables are source-like and not business-ready
* staging models handle typing and standardization
* mart models define business-friendly facts and dimensions
* dbt tests validate important assumptions
* BI should focus on reporting and analysis, not cleaning raw data

The intended flow is:
PostgreSQL raw
→ dbt staging
→ dbt mart
→ Power BI

## Data Model Relationships

The Power BI model uses these relationships:
| from                                      | to                          | cardinality | filter direction |
| ----------------------------------------- | --------------------------- | ----------- | ---------------- |
| `fct_orders.customer_id`                  | `dim_customers.customer_id` | many-to-one | single           |
| `fct_order_items.order_id`                | `fct_orders.order_id`       | many-to-one | single           |
| `fct_order_items.product_id`              | `dim_products.product_id`   | many-to-one | single           |
| `fct_order_items.seller_id`               | `dim_sellers.seller_id`     | many-to-one | single           |
| `fct_payments.order_id`                   | `fct_orders.order_id`       | many-to-one | single           |
| `fct_reviews.order_id`                    | `fct_orders.order_id`       | many-to-one | single           |
| `fct_supplier_product_updates.product_id` | `dim_products.product_id`   | many-to-one | single           |

Supplier data is treated as a separate supplier-quality fact and is not directly connected to orders, payments, or reviews.

## Dashboard Pages
1. Executive Overview

Purpose:

Provide a high-level business summary.

Main visuals:

* Total item revenue
* Order count
* Revenue per order
* Average review score
* Late delivery rate
* Rows needing supplier review
* Monthly revenue trend
* Top product categories by revenue
* Customer states by order count
* Payment type distribution

2. Revenue & Orders

Purpose:

Analyze order and revenue trends.

Main visuals:

* Monthly revenue trend
* Monthly order count trend
* Top product categories by revenue
* Customer states by revenue
* Revenue and order summary cards
* Date and state slicers

3. Product & Seller Performance

Purpose:

Analyze which products and sellers drive business performance.

Main visuals:

* Top product categories by revenue
* Top sellers by revenue
* Seller states by revenue
* Product categories by item count
* Product/seller summary cards

4. Delivery & Reviews

Purpose:

Analyze the relationship between delivery performance and customer satisfaction.

Main visuals:

* Late delivery vs average review score
* Late delivery rate
* Average review score
* Review sentiment distribution
* Delivery delay/order count analysis
* Review score by product category

Important observation:

Late deliveries are associated with lower review scores.

Earlier SQL analysis showed:
| delivery status | average review score |
| --------------- | -------------------: |
| not late        |                 4.29 |
| late            |                 2.57 |

5. Supplier Data Quality

Purpose:

Expose data-quality risks in the supplier source.

Main visuals:

* Supplier row count
* Rows needing supplier review
* Supplier review rate
* Invalid supplier price rows
* Negative supplier price rows
* Supplier rows by stock status
* Supplier rows needing review by supplier
* Table of problematic supplier records

This page demonstrates that the platform keeps messy supplier-source problems visible instead of silently removing them.
| measure                              | purpose                                                  |
| ------------------------------------ | -------------------------------------------------------- |
| `Total Item Revenue`                 | Sum of item-level price                                  |
| `Total Item Value Including Freight` | Item price plus freight                                  |
| `Total Freight Value`                | Sum of freight value                                     |
| `Order Count`                        | Distinct count of orders                                 |
| `Item Count`                         | Count of item-level records                              |
| `Average Item Price`                 | Average item price                                       |
| `Revenue per Order`                  | Item revenue divided by order count                      |
| `Average Review Score`               | Average customer review score                            |
| `Review Count`                       | Count of review records                                  |
| `Delivered Order Count`              | Count of delivered orders                                |
| `Late Delivered Order Count`         | Count of late delivered orders                           |
| `Late Delivery Rate`                 | Late delivered orders divided by delivered orders        |
| `Average Delivery Delay Days`        | Average difference between actual and estimated delivery |
| `Total Payment Value`                | Sum of payment values                                    |
| `Payment Record Count`               | Count of payment records                                 |
| `Supplier Row Count`                 | Count of supplier update records                         |
| `Rows Needing Supplier Review`       | Count of supplier records with quality issues            |
| `Supplier Review Rate`               | Supplier review rows divided by total supplier rows      |
| `Invalid Supplier Price Rows`        | Supplier rows with invalid price                         |
| `Negative Supplier Price Rows`       | Supplier rows with negative price                        |


## Important Modeling Notes
1. Revenue

The dashboard uses Total Item Revenue from fct_order_items.
This avoids using payment value as the main revenue metric, because payment records may have different grain and can include multiple payment rows per order.

2. Order Count

Order count uses distinct order IDs from fct_orders. This avoids counting item rows as orders.

3. Reviews

Review analysis is order-level. When reviews are analyzed by product category, review scores can be repeated if an order contains multiple items.This is acceptable for first exploratory dashboarding but should be documented as a modeling limitation.

4. Supplier Data

Supplier data intentionally contains messy records.The dashboard uses needs_business_review and related flags to make supplier data-quality issues visible.

## Known Limitations
* The dashboard is built in Power BI Desktop using local PostgreSQL data.
* It is not yet published to Power BI Service.
* Scheduled refresh is not configured yet.
* Supplier data is handmade for simulation and should be interpreted as a data-quality scenario.
* Review-to-product analysis may duplicate reviews across multi-item orders.
* The dashboard currently uses imported data, not DirectQuery.
* Cloud Redshift/dbt Cloud integration is planned later.

## Portfolio Value

This dashboard demonstrates that the project supports business-facing analysis, not only backend data movement.
It shows:
* dbt mart models can support BI reporting
* Power BI connects to business-ready models
* revenue, order, product, seller, delivery, review, and supplier-quality questions can be answered
* data-quality issues are visible to business users
* the platform connects engineering work to business value

## Next Improvements

Possible next improvements:
* add dashboard screenshots to the repository
* update README with BI dashboard summary
* add a dashboard architecture diagram
* add API and marketing sources later
* publish to Power BI Service if needed
* connect to Redshift/dbt Cloud in the AWS phase

Then commit:

```powershell
cd G:\retail-analytics-data-platform
git add docs/bi_dashboard_notes.md powerbi/retail_analytics_dashboard.pbix
git commit -m "Add Power BI dashboard and documentation"
git push origin master

## Holiday Impact Page

The Holiday Impact page enriches Olist order data with Br public-holiday data from the Nager.Date API.

The page is based on the dbt mart `dbt_mart.fct_orders_holiday_context`, which connects each order to the nearest Br public holiday within a seven-day window.

The dashboard compares:

- order volume by holiday window
- revenue by holiday window
- average review score by holiday window
- late delivery rate by holiday window
- top holidays by revenue

This page demonstrates external API enrichment, dbt business modeling, and Power BI reporting on a holiday-aware retail analytics use case.
