# Cloud warehouse validation status

## Final validated state

The cloud warehouse has been execution-tested end to end through the dbt reporting layer.

### Connectivity and source layer
- Redshift Serverless workgroup is available.
- Redshift Data API connectivity succeeded.
- Spectrum external schema successfully queries curated Parquet data through AWS Glue.
- 11 curated source tables are represented in dbt.

### dbt project inventory
- **34 models**
- **39 data tests**
- **11 sources**

### Execution validation
- Staging layer: **passed**
- Intermediate layer: **passed**
- Core warehouse layer: **passed**
- Reporting layer: **all 6 marts passed**
- Final dbt tests across the marts layer: **passed**

Validated reporting marts:
- `mart_sales_performance`
- `mart_customer_behavior`
- `mart_delivery_operations`
- `mart_product_performance`
- `mart_supplier_product_health`
- `mart_data_quality`

### Important modeling corrections validated
- Redshift late-binding views are used where Spectrum dependencies require them.
- Redshift-incompatible `MAX(boolean)` logic was replaced.
- Reporting date aliases were made Redshift-safe.
- Supplier-product data is not joined directly into `fct_order_items`.
- Product sales context is aggregated separately before combining with supplier-product health.
- Supplier-feed quality exceptions such as missing `product_id` are retained intentionally for monitoring.

## Cost controls
- Redshift Serverless capacity is capped at 4 RPUs.
- A usage limit protects against accidental excessive execution.
- CI runs `dbt parse` only and does not execute warehouse queries.
- Development validation was performed layer-by-layer.

## Next consumer
The validated reporting marts are ready for Power BI.

For portfolio use, Power BI **Import mode** is preferred over DirectQuery to avoid repeatedly waking Redshift during report interaction.
