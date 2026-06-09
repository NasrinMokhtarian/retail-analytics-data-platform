# Business Analysis Findings

## Purpose

This document summarizes the first business analysis findings from the validated mart layer of the Retail Analytics Data Platform project.

The goal is to show that the data platform can support practical business questions after going through the full workflow:

```text
raw files
→ cleaning
→ validation
→ PostgreSQL loading
→ staging views
→ mart views
→ business analysis
```

The analysis is based on:

`sql/business_analysis/01_mart_business_analysis.sql`

---

## Current Analytical Context

The business analysis uses the PostgreSQL `mart` schema.

Main mart objects used:

| mart object                       | purpose                                             |
| --------------------------------- | --------------------------------------------------- |
| mart.fct_orders                   | Order lifecycle and delivery metrics                |
| mart.fct_order_items              | Item-level revenue and seller/product relationships |
| mart.fct_payments                 | Payment behavior                                    |
| mart.fct_reviews                  | Review scores and sentiment grouping                |
| mart.dim_customers                | Customer geography                                  |
| mart.dim_products                 | Product category and product attributes             |
| mart.dim_sellers                  | Seller geography                                    |
| mart.fct_supplier_product_updates | Supplier update records and quality flags           |

This means the analysis is not querying raw files directly. It uses validated analytical views.

---

## Finding 1 — Highest Revenue Months

The top revenue months based on item revenue were:

| order_month | item_revenue |
| ----------- | -----------: |
| 2017-11-01  | 1,010,271.37 |
| 2018-04-01  |   996,647.75 |
| 2018-05-01  |   996,517.68 |
| 2018-03-01  |   983,213.44 |
| 2018-01-01  |   950,030.36 |

### Interpretation

November 2017 had the highest item revenue among the reviewed months.

Several months in early 2018 also showed strong revenue, especially March, April, and May 2018.

### Business meaning

This suggests that sales activity was strong across late 2017 and early/mid 2018. A business stakeholder may want to investigate whether this was caused by seasonality, promotions, marketplace growth, or category-specific performance.

### Follow-up questions

* Was November 2017 driven by a specific product category?
* Were there promotional events or seasonal campaigns?
* Did order volume and revenue grow together, or was revenue driven by higher-value products?

---

## Finding 2 — Top Product Categories by Revenue

The top product categories by item revenue were:

| product_category      | item_revenue |
| --------------------- | -----------: |
| health_beauty         | 1,258,681.34 |
| watches_gifts         | 1,205,005.68 |
| bed_bath_table        | 1,036,988.68 |
| sports_leisure        |   988,048.97 |
| computers_accessories |   911,954.32 |

### Interpretation

`health_beauty` generated the highest item revenue, followed closely by `watches_gifts`.

The top five categories represent important revenue drivers for the business.

### Business meaning

These categories may deserve priority in commercial reporting, inventory analysis, seller performance monitoring, and marketing campaigns.

### Follow-up questions

* Are these categories also high in order volume, or mainly high in average item value?
* Which sellers dominate these categories?
* Do high-revenue categories also have strong review scores?
* Are delivery delays more common in any of these categories?

---

## Finding 3 — Top Customer States by Revenue

The top customer states by item revenue were:

| customer_state | item_revenue | order_count |
| -------------- | -----------: | ----------: |
| SP             | 5,202,955.05 |      41,375 |
| RJ             | 1,824,092.67 |      12,762 |
| MG             | 1,585,308.03 |      11,544 |
| RS             |   750,304.02 |       5,432 |
| PR             |   683,083.76 |       4,998 |

### Interpretation

SP is by far the largest customer state by both revenue and order count.

RJ and MG are also major markets but significantly smaller than SP.

### Business meaning

Customer demand is geographically concentrated. This can affect logistics, seller strategy, marketing focus, and delivery performance analysis.

### Follow-up questions

* Does SP also have better delivery performance than other states?
* Are top categories different by state?
* Do review scores vary by customer state?
* Are shipping costs higher for some states?

---

## Finding 4 — Delivery Delay and Review Score

Review scores were compared between late and not-late delivered orders:

| is_late_delivery | review_count | avg_review_score |
| ---------------- | -----------: | ---------------: |
| false            |       88,653 |             4.29 |
| true             |        7,700 |             2.57 |

### Interpretation

Late deliveries have a much lower average review score.

Orders that were not late had an average review score of 4.29, while late orders had an average review score of 2.57.

### Business meaning

Delivery performance appears strongly related to customer satisfaction.

This is one of the strongest business insights from the first analysis.

### Follow-up questions

* Which sellers are responsible for the most late deliveries?
* Which customer states have the most late deliveries?
* Are some product categories more likely to be delivered late?
* How many negative reviews are linked to late deliveries?

---

## Finding 5 — Payment Type Distribution

Payment type summary:

| payment_type | payment_record_count | total_payment_value |
| ------------ | -------------------: | ------------------: |
| credit_card  |               76,795 |       12,542,084.19 |
| boleto       |               19,784 |        2,869,361.27 |
| voucher      |                5,775 |          379,436.87 |
| debit_card   |                1,529 |          217,989.79 |
| not_defined  |                    3 |                0.00 |

### Interpretation

Credit card is the dominant payment method by both payment record count and total payment value.

Boleto is the second-largest payment method.

`not_defined` appears only three times and has zero payment value.

### Business meaning

Payment behavior is highly concentrated around credit card payments. This could be useful for payment operations, checkout optimization, and financial reporting.

### Follow-up questions

* Do payment methods vary by customer state?
* Do higher-value orders use different payment methods?
* Are review scores or delivery patterns different by payment type?
* Should `not_defined` payment records be excluded from some financial analysis?

---

## Supplier Data Quality Observation

The supplier source was intentionally created as a messy business file.

Previous supplier quality checks found issues such as:

* missing product_id
* missing currency
* invalid price
* negative price
* unknown stock status
* duplicate business keys

### Business meaning

Supplier data should not be blindly trusted for final analytics.

The mart layer preserves supplier quality flags and includes `needs_business_review`, so problematic records remain visible instead of being silently removed.

### Follow-up action

The supplier issue summary should be reviewed again from:

`mart.fct_supplier_product_updates`

The key question is:

```text
How many supplier rows need business review before they can be trusted?
```

---

## Important Data Modeling Notes

### Revenue grain

Revenue was calculated from `mart.fct_order_items`.

This is important because item-level revenue should be analyzed at item grain.

Incorrectly joining item-level facts with order-level, payment-level, or review-level facts can create double counting.

### Delivery analysis grain

Delivery metrics are order-level metrics from `mart.fct_orders`.

They should be interpreted at order grain.

### Review analysis risk

Review scores are linked to orders. When joining reviews to order items or product categories, one order with multiple items may duplicate the review across items.

This is acceptable for exploration when documented, but future mart models may need more careful review-to-product logic.

### Supplier quality

Supplier data is useful for simulating real business-file ingestion, but flagged supplier rows should remain visible and should not be treated as fully trusted.

---

## Strong Business Insights

The first mart-layer analysis produced several useful insights:

1. November 2017 was the highest revenue month among the reviewed months.
2. `health_beauty` and `watches_gifts` were the top revenue-generating product categories.
3. SP was the dominant customer state by revenue and order count.
4. Late deliveries had a much lower average review score than non-late deliveries.
5. Credit card was the dominant payment method by payment value.
6. Supplier data quality issues must be reviewed before supplier updates are used for trusted analysis.

---

## Recommended Next Business Analysis Questions

The next SQL analysis should investigate:

1. Seller performance by revenue and late delivery rate.
2. Product category performance by revenue and review score.
3. Customer state performance by revenue, order count, and delivery delay.
4. Monthly revenue trend by product category.
5. Relationship between late delivery and negative reviews.
6. Supplier update records that can be matched to product categories.

---

## Portfolio Value

This analysis shows that the platform can support end-to-end analytical work:

```text
source onboarding
→ data quality
→ cleaning
→ PostgreSQL loading
→ staging
→ marts
→ business analysis
```

The project is not only a technical data pipeline. It also demonstrates the ability to connect data engineering work to business questions.
