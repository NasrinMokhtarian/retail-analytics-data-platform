# Architecture

```mermaid
flowchart LR
    A[Olist CSV sources] --> B[Python ingestion / quality / cleaning]
    S[Supplier update file] --> B
    H[Nager.Date holidays API] --> B

    B --> C[Validated Parquet]
    C --> D[S3 data lake]
    D --> E[AWS Glue Data Catalog]
    E --> F[Redshift Spectrum external schema]

    F --> G[dbt staging<br/>late-binding views]
    G --> I[dbt intermediate<br/>late-binding views]
    I --> J[Core warehouse<br/>dimensions + facts]
    J --> K[Reporting marts]
    K --> L[Power BI]

    T[Terraform] -. provisions .-> D
    T -. provisions .-> F

    Q[Quality gates + pytest] -. validates .-> B
    CI[GitHub Actions<br/>pytest + dbt parse] -. validates code .-> G
    AF[Airflow<br/>local orchestration] -. orchestrates tested CLI tasks .-> B
```

## Warehouse layers

- **Sources:** 11 curated Parquet datasets registered in Glue.
- **Staging:** type casting, naming normalization, source cleanup; late-binding Redshift views because the models reference Spectrum.
- **Intermediate:** one-to-many aggregation and grain protection for payments, reviews, geolocation, products, orders and supplier/product data.
- **Core:** durable analytical dimensions and facts stored in Redshift.
- **Reporting:** business-facing marts for sales, customers, delivery, products, suppliers and data quality.

## Grain rules

- `fct_orders`: one row per `order_id`.
- `fct_order_items`: one row per `order_id + order_item_id`.
- customer analytics use `customer_unique_id`.
- geolocation is reduced to one analytical row per ZIP before joining.
- payment and review sources are aggregated before joining to orders.
- supplier/product updates remain at supplier-product grain and are not joined directly to order items, avoiding false supplier attribution and duplicated revenue.

## Cost controls

- Redshift Serverless workgroup is capped at 4 RPUs.
- A usage limit protects against accidental excessive execution.
- CI performs `dbt parse` only and does not execute warehouse queries.
- Cloud dbt builds are run deliberately and layer-by-layer during development.
