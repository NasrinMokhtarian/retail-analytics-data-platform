We separate raw loaded data, staging transformations, business-ready marts, and audit metadata so the database stays understandable and maintainable.

raw      → source-like loaded data from cleaned files
staging  → cleaned/standardized SQL transformation layer
mart     → business-ready analytical tables later
audit    → load tracking and pipeline metadata
### Phase 1
 — Design database table loading strategy
### phase 2
 — Design PostgreSQL Load Strategy
This step matters because loading data is not only “insert CSV into database.” This step defines the load plan before implementation. It is about load design.
In a company, you need traceability:
- Which file was loaded?
- When was it loaded?
- How many rows loaded?
- Did the table row count match the file?
- Was the load successful?