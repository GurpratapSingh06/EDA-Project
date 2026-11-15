# Chicago Crime Incident & Public Safety Analytics Data Warehouse

**Design and Implementation of a Batch Data Warehouse with OLAP, Dashboard Analytics, and Predictive Data Mining**  
**Course:** TY B.Tech Integrated Data Warehouse, OLAP and Data Mining Project  
**Author:** Public Safety Data Engineering and Crime Analytics Team  
**Dataset:** Chicago "Crimes – 2001 to Present" (City of Chicago Data Portal: `ijzp-q8t2`)  
**Study Scope:** January 1, 2024 to December 31, 2025 Reported Incidents (**497,919 records**)  

---

## 1. Project Overview & Scope Justification

This project implements an enterprise-grade, single-lifecycle Batch Data Warehouse on **PostgreSQL 16** with conformed dimensional structures, full OLAP cube operations, Power BI semantic models, and predictive data mining pipelines (Regression, Association Rule Mining, and Decision Tree Classification).

### Changed Scope Justification (Single Warehouse Selection):
As authorized by project guidelines, **only the Batch Data Warehouse is physically implemented**, with Distributed (Citus) and Real-Time (Kafka/ClickHouse) paradigms analytically evaluated in `docs/architecture_evaluation.md`:
1. **Right-Sized Single-Node Architecture:** The study dataset (~500,000 rows, 103 MB raw CSV) comfortably fits into a single node's RAM and page cache. Sharding across distributed nodes incurs unnecessary network serialization penalties without analytical gain.
2. **Historical Reporting & Dimensional Fidelity:** The Chicago dataset is inherently historical; streaming would merely simulate live data. A relational batch DW provides full ACID compliance, strict foreign-key integrity, multi-table joins, and certified analytical mart views required for scientific inquiry.
3. **Fact Constellation Acceleration:** A dual-grain constellation schema (`FactCrimeIncident` at incident grain + `FactAreaDailyPublicSafety` at Community Area x Date grain) provides sub-5ms area-level query responses, accelerating regression model training by >70x.

---

## 2. Repository Structure

```
chicago-crime-dw/
├── docker-compose.yml              # PostgreSQL 16 Alpine container definition
├── requirements.txt                # Python package dependencies
├── README.md                       # Complete reproduction and execution guide
├── data/
│   ├── raw/
│   │   └── crimes_2024_2025.csv    # 497,919 raw extracted records (103.17 MB)
│   └── curated/
│       └── crimes_curated.csv      # 497,919 curated records with derived features (203.07 MB)
├── etl/
│   ├── extract.py                  # Multi-threaded Socrata API extraction
│   ├── profile_data.py             # Pre-cleaning profiling script
│   ├── curate.py                   # Data quality treatments and feature engineering
│   ├── generate_eda.py             # Statistical metric computation and figure generation
│   ├── generate_erds.py            # Programmatic ERD diagram generation
│   ├── load_initial.py             # Bulk warehouse load (Jan 2024–Nov 2025: 480k rows)
│   ├── load_incremental.py         # Delta micro-batch load (Dec 2025: 17.6k rows)
│   ├── validate.py                 # Reconciliation, orphan FKs, and measure checks
│   ├── benchmark_indexes.py        # EXPLAIN ANALYZE index performance benchmark
│   ├── run_olap_and_dashboard.py   # OLAP cube operations and Power BI exports
│   └── run_ml_models.py            # Regression, Association Mining, Decision Tree
├── sql/
│   ├── 00_schemas.sql              # Staging, DW, Mart schemas
│   ├── 01_staging.sql              # Staging table DDL
│   ├── 02_dims.sql                 # Conformed dimension tables with -1 Unknowns
│   ├── 03_facts.sql                # FactCrimeIncident and FactAreaDailyPublicSafety
│   ├── 04_indexes.sql              # B-Tree analytical and foreign-key indexes
│   ├── 05_olap_queries.sql         # Documented queries for Roll-up, Drill-down, Slice, Dice, Pivot, CUBE
│   ├── 06_mart_view.sql            # mart.PublicSafetyAnalyticsMart SQL view definition
│   └── 07_validation.sql           # Integrity verification and reconciliation queries
├── notebooks/
│   ├── 01_profiling.ipynb          # Interactive pre-cleaning dataset profiling
│   ├── 02_curation.ipynb           # Attribute-specific curation and feature derivation
│   ├── 03_eda.ipynb                # Comprehensive exploratory data analysis
│   ├── 04_regression.ipynb         # Time-lagged incident count forecasting
│   ├── 05_association.ipynb        # Apriori and FP-Growth rule mining
│   └── 06_decision_tree.ipynb      # Balanced decision tree arrest classification
├── outputs/
│   ├── figures/                    # 14 publication-grade visualization PNGs (fig01 to fig14)
│   ├── tables/                     # Summary CSV statistics and Markdown interpretations
│   ├── results/                    # Execution logs, query timings, model metrics
│   └── powerbi_exports/            # Dimension and aggregated fact CSVs for Power BI
└── docs/
    ├── source_log.md               # Socrata extraction metadata log
    ├── data_dictionary.md          # Source vs. derived attribute catalog
    ├── dq_report.md                # Attribute-specific data quality audit report
    ├── schema_comparison.md        # Star vs. Snowflake vs. Constellation evaluation
    ├── olap_documentation.md       # 6 OLAP operations + 10 mandatory questions documentation
    ├── powerbi_build_guide.md      # Canvas design, DAX measures, and connection guide
    ├── findings.md                 # 10 formal empirical findings and recommendations
    ├── architecture_evaluation.md  # Batch (measured) vs. Distributed vs. Real-Time analysis
    ├── technical_report.md         # Comprehensive end-to-end technical report
    ├── technical_report.docx       # Compiled Microsoft Word deliverable
    └── erd/                        # Visual schema diagrams (Star, Snowflake, Constellation)
```

---

## 3. Environment Setup & Prerequisites

### Prerequisites:
- Python 3.10+ (Tested on Python 3.13)
- PostgreSQL 16 (via Docker Compose or local PostgreSQL service on `localhost:5432`)
- Pandoc 3.0+ (for Word report compilation)

### Quick Start:
```bash
# 1. Clone repository and navigate to folder
cd chicago-crime-dw

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Start PostgreSQL container via Docker Compose
docker compose up -d
```

*Note on Database Credentials:* The system connects by default to:
- **Host:** `localhost`
- **Port:** `5432`
- **User:** `postgres`
- **Password:** `root`
- **Database:** `chicago_crime_dw`

---

## 4. End-to-End Reproduction Run Order

Every step of the lifecycle is automated via clean Python and SQL scripts. Execute them sequentially:

### Step 1: Data Extraction
```bash
python etl/extract.py
```
*Retrieves 497,919 records from the City of Chicago Socrata API (`ijzp-q8t2`) and logs metadata to `docs/source_log.md`.*

### Step 2: Data Profiling (Pre-Cleaning)
```bash
python etl/profile_data.py
```
*Audits missing fields, exact duplicates, logical duplicates, coordinate validity, and saves profiling summaries to `outputs/tables/`.*

### Step 3: Data Curation & Feature Engineering
```bash
python etl/curate.py
```
*Applies attribute-specific treatments (imputing `-1` for unknown spatial fields; 0 rows dropped), engineers 13 derived features, saves `data/curated/crimes_curated.csv`, and generates `docs/dq_report.md` and `docs/data_dictionary.md`.*

### Step 4: Exploratory Data Analysis & Chart Generation
```bash
python etl/generate_eda.py
```
*Calculates numerical statistics (mean, std, IQR, skewness, kurtosis), analyzes categorical frequencies, diurnal hourly trends, volume vs. arrest rate distinctions, and generates figures `fig01` to `fig08`.*

### Step 5: Dimensional Modelling & ERD Generation
```bash
python etl/generate_erds.py
```
*Generates publication-quality ERD diagrams for Star, Snowflake, and Fact Constellation models in `docs/erd/`.*

### Step 6: Initial Warehouse Bulk Load (Jan 2024 to Nov 2025)
```bash
python etl/load_initial.py
```
*Executes DDLs (`00_schemas.sql` to `03_facts.sql`), populates conformed dimensions (`DimDate`, `DimTime`, `DimCrimeType`, `DimLocation`, `DimIncidentContext`), and bulk loads 480,310 facts into `dw.FactCrimeIncident` and `dw.FactAreaDailyPublicSafety` in **88.61 seconds**.*

### Step 7: Incremental Warehouse Load Demonstration (Dec 2025)
```bash
python etl/load_incremental.py
```
*Ingests the held-back December 2025 records (17,609 rows) non-destructively through staging, dimension lookup, and fact append in **2.46 seconds**, logging audit results to `outputs/results/incremental_load.md`.*

### Step 8: Warehouse Reconciliation & Referential Integrity Audit
```bash
python etl/validate.py
```
*Executes `07_validation.sql` against PostgreSQL, confirming 100% row reconciliation (497,919 / 497,919), zero orphan foreign keys, exact measure totals, and outputs `outputs/results/validation_report.md`.*

### Step 9: Indexing Performance Benchmark
```bash
python etl/benchmark_indexes.py
```
*Profiles 5 analytical queries with `EXPLAIN (ANALYZE, TIMING)` before and after executing `04_indexes.sql`, logging timings to `outputs/results/query_timings.csv` and `outputs/results/indexing_report.md`.*

### Step 10: OLAP Cube Operations & Power BI Data Export
```bash
python etl/run_olap_and_dashboard.py
```
*Executes Roll-up, Drill-down, Slice, Dice, Pivot, CUBE/GROUPING SETS, answers all 10 mandatory questions in `sql/05_olap_queries.sql`, writes `docs/olap_documentation.md`, `docs/powerbi_build_guide.md`, `docs/findings.md`, and exports dashboard-ready CSVs to `outputs/powerbi_exports/`.*

### Step 11: Machine Learning & Data Mining Pipelines
```bash
python etl/run_ml_models.py
```
*Trains and evaluates models directly from the certified analytical mart:*
- **Regression:** Time-lagged area incident forecasting (Ridge $R^2 = 0.7826$, RMSE = 3.425).
- **Association Mining:** Apriori and FP-Growth rule mining (1,123 frequent itemsets, top 12 rules).
- **Decision Tree:** Class-balanced arrest classification (Accuracy = 0.7718, Recall = 0.5559, ROC-AUC = 0.7392).

### Step 12: Generate & Execute All Jupyter Notebooks
```bash
python etl/generate_notebooks_a.py
python etl/generate_notebooks_efg.py
python -c "
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
for nb_name in ['01_profiling.ipynb', '02_curation.ipynb', '03_eda.ipynb', '04_regression.ipynb', '05_association.ipynb', '06_decision_tree.ipynb']:
    nb_path = f'notebooks/{nb_name}'
    with open(nb_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
    ep.preprocess(nb, {'metadata': {'path': 'notebooks'}})
    with open(nb_path, 'w', encoding='utf-8') as f:
        nbformat.write(nb, f)
    print(f'Executed {nb_name} successfully!')
"
```

### Step 13: Compile Technical Report to DOCX
```bash
pandoc docs/technical_report.md -o docs/technical_report.docx
```

---

## 5. Measured Experimental Benchmark Highlights

| System Lifecycle Stage | Metric / Parameter | Empirically Measured Result |
| :--- | :--- | :--- |
| **Data Extraction** | Multi-threaded Socrata SoQL API | **497,919 rows in 86.44 s** (103.17 MB) |
| **Data Curation** | Attribute Treatment & Feature Engineering | **497,919 rows in ~18 s** (0 rows dropped) |
| **Initial Warehouse Load** | PostgreSQL 16 Bulk Ingestion | **480,310 rows in 88.61 s** |
| **Incremental Delta Load** | December 2025 Micro-Batch Append | **17,609 rows in 2.46 s** (233 new locations) |
| **Post-Load Validation** | Source vs. Staging vs. Fact Match | **497,919 / 497,919 (100% Match, 0 Orphans)** |
| **Indexing Build Time** | Secondary B-Tree Indexes | **5.05 s for 17 indexes** |
| **Constellation Query Latency**| Area-Daily Aggregated Fact Query | **~4.2 ms** (vs. ~280 ms scanning incident fact) |
| **Regression Forecasting** | Ridge Regression ($R^2$ on Test Set) | **0.7826** (RMSE: 3.425 incidents/day) |
| **Association Mining** | FP-Growth vs. Apriori Execution Time | **2.35 s vs. 3.97 s (1.7x faster)** |
| **Decision Tree Model** | Class-Balanced Arrest Classifier | **ROC-AUC: 0.7392**, Recall: 0.5559 |

---

## 6. Power BI Dashboard Connectivity

To explore the analytical data model in Microsoft Power BI:
1. Open Power BI Desktop $\longrightarrow$ **Get Data** $\longrightarrow$ **PostgreSQL database**.
2. Set Server = `localhost:5432`, Database = `chicago_crime_dw`.
3. Select tables `dw.dimdate`, `dw.dimtime`, `dw.dimcrimetype`, `dw.dimlocation`, `dw.dimincidentcontext`, and view `mart.publicsafetyanalyticsmart` or `dw.factareadailypublicsafety`.
4. Alternatively, use **Text/CSV** to import files from `outputs/powerbi_exports/`.
5. Follow the visual canvas layouts and DAX formulas provided in `docs/powerbi_build_guide.md`.
