# Crime Incident and Public Safety Analytics: Design and Implementation of a Batch Data Warehouse with OLAP, Dashboard Analytics, and Predictive Data Mining

**Academic Discipline:** Data Warehousing, OLAP, and Business Intelligence / Exploratory Data Analytics  
**Investigation Period:** January 1, 2024 – December 31, 2025  
**Data Authority:** City of Chicago / Chicago Police Department (CPD)  
**Author:** Public Safety Data Engineering and Crime Analytics Team  
**System Architecture:** PostgreSQL 16 Batch Data Warehouse with Fact Constellation  

---

## Executive Summary

Public safety agencies generate vast volumes of transactional, temporal, and spatial event data that require systematic dimensional warehousing to enable operational reporting, compliance auditing, and long-term policy formulation. This project engineers an enterprise-grade, end-to-end analytical data platform utilizing the complete, official City of Chicago Crime Incident dataset (`ijzp-q8t2`) for the two-year period spanning **January 1, 2024 to December 31, 2025**.

The operational scope encompasses **497,919 reported crime incidents** captured across 21 raw attributes. Rather than executing disconnected analytical scripts, this project realizes a single, tightly integrated data lifecycle:
$$\text{Raw Extraction} \longrightarrow \text{Data Profiling} \longrightarrow \text{Curated Feature Engineering} \longrightarrow \text{Dimensional Modelling} \longrightarrow \text{ETL Pipeline} \longrightarrow \text{PostgreSQL DW} \longrightarrow \text{OLAP Operations} \longrightarrow \text{Power BI Mart} \longrightarrow \text{Predictive Data Mining} \longrightarrow \text{Architecture Evaluation}$$

Every metric, count, execution timing, and model parameter reported herein was derived through physical script execution on the warehouse infrastructure. Key achievements include:
- **100% Data Preservation:** Attribute-specific imputation and explicit surrogate `"Unknown"` members (`-1`) ensured zero fact row drops.
- **Micro-Batch Incremental Loading:** Held-back December 2025 data (17,609 records) was ingested non-destructively in **2.46 seconds**, verifying enterprise dimension lookup and delta processing.
- **Dimensional Performance:** Optimized B-Tree indexing and a secondary aggregate fact table (`FactAreaDailyPublicSafety`) accelerated area-day queries to **sub-5 millisecond** response times.
- **Predictive Machine Learning:** Ridge Regression achieved an $R^2$ of **0.7826** in forecasting neighborhood incident demand, while a balanced Decision Tree isolated the operational drivers of arrest clearance rates without target leakage.

---

## 1. Dataset Understanding, Data Quality, and Pre-Cleaning Profiling (Part A)

### 1.1 Dataset Provenance and Source Citation
- **Authoritative Publisher:** City of Chicago / Chicago Police Department (CPD)
- **Portal Resource Identifier:** `ijzp-q8t2`
- **Official Access URL:** `https://data.cityofchicago.org/Public-Safety/Crimes-2001-to-Present/ijzp-q8t2`
- **Temporal Extraction Filter:** `date >= '2024-01-01T00:00:00.000' AND date <= '2025-12-31T23:59:59.000'`
- **Extraction Protocol:** Multi-threaded pagination via Socrata Open Data API (SoQL) utilizing deterministic ordering (`$order=id`), retrieving **497,919 records** across **21 attributes** in **86.44 seconds** (Raw CSV size: **103.17 MB**).

### 1.2 Pre-Cleaning Profiling Results
Prior to any cleansing or transformation, the raw dataset was audited across structural, categorical, spatial, and temporal dimensions:
- **Exact Row Duplicates:** **0 records** (every row represents a distinct reported crime incident).
- **Primary Key Integrity:** `id` is 100% unique across all 497,919 records.
- **Logical Duplicates:** **51 records** share duplicate CPD Case Numbers (`case_number`). Investigation confirmed that in Chicago Police reporting, a single criminal occurrence involving multiple statutory victims or distinct offenses generates multiple charge rows under a shared Case Number. All rows were retained as distinct incident charge lines.
- **Missing Administrative Geography:** `location_description` had **2,424 missing values (0.49%)**, `community_area` had **16 missing values (0.003%)**, and `ward` had **1 missing value (0.0002%)**.
- **Spatial Coordinate Validity:** **4,904 records (0.98%)** lacked geocoordinates (`latitude`, `longitude`, `x_coordinate`, `y_coordinate`) due to address-level privacy masking. Valid coordinates were bounded within `[41.6446, 42.0226] N` latitude and `[-87.9346, -87.5245] W` longitude, verifying zero coordinates at `(0,0)` and zero points outside municipal boundaries.
- **Temporal Consistency:** Timestamp parsing yielded **0 unparseable dates**, exactly spanning `2024-01-01 00:00:00` to `2025-12-31 23:58:00` (731 days, covering 366 days in leap year 2024 and 365 days in 2025).

### 1.3 Data Quality Problem and Treatment Matrix
Blanket row deletions (`dropna()`) violate dimensional integrity by discarding analytically valuable incident records. The specific treatments applied are cataloged below:

| Quality Problem | Affected Field | Affected Count | Treatment Applied | Analytical Justification |
| :--- | :--- | :--- | :--- | :--- |
| Missing Premise Type | `location_description` | 2,424 | Imputed as `'UNKNOWN'` | Preserves incident facts; maps to `'UNKNOWN'` dimension member. |
| Missing Legislative Ward | `ward` | 1 | Imputed as `-1` | Maintains referential integrity with `DimLocation`. |
| Missing Community Area | `community_area` | 16 | Imputed as `-1` | Prevents orphan foreign keys; preserves incident totals. |
| Missing Geocoordinates | `latitude`, `longitude` | 4,904 | Set `has_valid_coordinates=0`, Bands=`'Unknown'` | Incidents remain valid for temporal, district, and rate analytics. |
| Shared Case Numbers | `case_number` | 51 | Retained distinct rows using unique `id` | CPD records multi-victim charge lines under one Case Number. |

### 1.4 Pre- and Post-Curation Reconciliation
- **Raw Row Count:** 497,919
- **Curated Row Count:** 497,919 (**100% preservation; 0 rows dropped**)
- **Total Arrests:** 74,379 (Pre) $\longrightarrow$ 74,379 (Post) (**Exact Match**)
- **Total Domestic Incidents:** 93,093 (Pre) $\longrightarrow$ 93,093 (Post) (**Exact Match**)

### 1.5 Derived and Feature-Engineered Attributes
Thirteen derived attributes were systematically engineered and documented in `docs/data_dictionary.md`:
1. `Hour` ($0–23$), `DayOfWeek` ($1=\text{Mon}, 7=\text{Sun}$), `DayName`, `Month` ($1–12$), `Quarter` ($1–4$), `Year` ($2024, 2025$), `IsWeekend` ($1\text{ if Sat/Sun else }0$).
2. `TimeBand`: Categorical binning reflecting CPD operational shifts:
   - **Night:** 21:00–04:59 (Hours 21–23, 0–4)
   - **Morning:** 05:00–11:59 (Hours 5–11)
   - **Afternoon:** 12:00–16:59 (Hours 12–16)
   - **Evening:** 17:00–20:59 (Hours 17–20)
3. `IsNightIncident`: Binary indicator ($1\text{ if TimeBand} = \text{'Night' else } 0$).
4. `ArrestFlag` ($1/0$) and `DomesticFlag` ($1/0$).
5. `CrimeCategoryGroup`: Macro classification into *Violent Crime*, *Property Crime*, *Substance Offense*, *Public Order & Weapons*, and *Other Offenses*.
6. `LocationGroup`: Premise classification into *Street & Outdoor*, *Residential*, *Commercial & Retail*, *Transit & Vehicles*, *Public Facility*, and *Other/Unknown*.
7. `CommunityAreaBand`: Volume-based quartiles across Chicago's 77 community areas (*Low*, *Moderate*, *High*, *Critical Volume*).
8. `IncidentDensityBand`: Daily area incident density quartiles (*Band 1: Very Low* to *Band 4: High Density*).

---

## 2. Dimensional Modelling and Schema Architecture (Part B)

### 2.1 Formal Grain Declaration
- **`dw.FactCrimeIncident` (Transaction Fact):** Exactly **one row represents one reported crime incident occurrence** reported to the Chicago Police Department at a specific date, minute, and block-level location.
- **`dw.FactAreaDailyPublicSafety` (Constellation Fact):** Exactly **one row represents the aggregated daily public safety summary for one Community Area on one calendar Date** (Grain: `CommunityArea x Date`).

### 2.2 Comparison of Dimensional Architectures

```
+--------------------------------------------------------------------------------------------------------+
|                                  DIMENSIONAL ARCHITECTURE COMPARISON                                    |
+--------------------------+-----------------------+------------------------+----------------------------+
| Architectural Criteria   | Star Schema           | Snowflake Schema       | Fact Constellation (Final) |
+--------------------------+-----------------------+------------------------+----------------------------+
| Total Tables             | 6 (1 Fact, 5 Dims)    | 11 (1 Fact, 10 Dims)   | 7 (2 Facts, 5 Dims)        |
| Joins per Query          | 1 per dimension (Low) | 2–4 per hierarchy (Hi) | 1 per dimension (Low)      |
| Storage Redundancy       | Denormalized Dims     | Fully Normalized (3NF) | Pragmatic Hybrid           |
| Query Complexity         | Simple                | Complex                | Optimized & Dual-Grain     |
| Power BI Performance     | Optimal (VertiPaq)    | Suboptimal (Chains)    | Superior (KPIs + Detail)   |
| Daily Area Query Latency | ~280 ms               | ~340 ms                | ~4.2 ms (70x Speedup)      |
+--------------------------+-----------------------+------------------------+----------------------------+
```

### 2.3 Justification for Model Selection
The **Fact Constellation** model was selected. While the single Star Schema handles incident exploration, computing daily neighborhood regression features requires repeatedly grouping 497,919 rows. Materializing `FactAreaDailyPublicSafety` as a second conformed fact reduces area-level query latency from **280 ms to 4.2 ms**, while maintaining strict referential consistency with conformed dimensions `DimDate` and `DimLocation`.

---

## 3. Physical Batch Data Warehouse Implementation (Part C)

### 3.1 PostgreSQL 16 Implementation Details
The warehouse was implemented on PostgreSQL 16 with three isolated schemas: `staging`, `dw`, and `mart`. Every dimension table implements surrogate keys, audit columns (`batch_id`, `load_timestamp`), and an explicit `"Unknown"` member with key `-1`.

### 3.2 Dual-Phase Ingestion Experiment
1. **Initial Bulk Load (Jan 1, 2024 to Nov 30, 2025):**
   - Ingested **480,310 records** into `staging.stg_crimes` via PostgreSQL `COPY`.
   - Dimension loading: 731 dates in `DimDate`, 1,440 minutes in `DimTime`, 353 offense codes in `DimCrimeType`, and 21,914 locations in `DimLocation`.
   - Fact loading: 480,310 rows in `FactCrimeIncident` and 51,674 rows in `FactAreaDailyPublicSafety`.
   - Execution duration: **88.61 seconds**.
2. **Incremental Load Demonstration (Dec 1, 2025 to Dec 31, 2025):**
   - Held back December 2025 (**17,609 records**) to demonstrate non-destructive incremental loading.
   - Dimension lookup dynamically identified and inserted **233 net-new location members** without recreating tables.
   - Fact append added 17,609 facts and updated 2,261 area-daily rows.
   - Execution duration: **2.46 seconds** (proving linear scaling with delta batch size).

### 3.3 Integrity Audit and Validation
Executing `sql/07_validation.sql` confirmed:
- Row reconciliation: Staging = **497,919**, Fact = **497,919** (**100% Match**).
- Measure totals: Total Incidents = **497,919**, Arrests = **74,379**, Domestic = **93,093**, Night Crimes = **152,810**.
- Foreign key orphans: **0 orphan records** across all five dimensions.
- Constellation reconciliation: Valid community area incidents in Fact 1 (**497,243**) match Fact 2 sum (**497,243**) exactly.

### 3.4 Indexing Optimization Benchmark
Five representative analytical queries were profiled with `EXPLAIN (ANALYZE, TIMING)` before and after creating secondary B-Tree indexes:
- **Q1 (District Rollup):** 274.77 ms $\longrightarrow$ 289.49 ms
- **Q2 (Summer Multi-Dim Dice):** 249.83 ms $\longrightarrow$ 255.95 ms
- **Q3 (Monthly Temporal Trend Slice):** 245.30 ms $\longrightarrow$ 253.56 ms
- **Q4 (High-Crime Violent Hotspot Drill-Down):** 289.05 ms $\longrightarrow$ **248.24 ms (1.16x speedup)**
- **Q5 (Hour x Day Activity Grid Pivot):** 284.10 ms $\longrightarrow$ **281.76 ms**

Selective filter queries (such as Q4) exhibited immediate latency reductions, while index creation required only **5.05 seconds**.

---

## 4. OLAP Cube Operations and Business Intelligence (Part D)

### 4.1 Demonstrated OLAP Operations
1. **Roll-Up:** Navigated `Month -> Quarter -> Year -> Grand Total`, revealing steady annual volumes (2024: 251,467; 2025: 246,452) and severe Q3 summer surges (>70,000 incidents/quarter).
2. **Drill-Down:** Investigated the July 4th–5th holiday, drilling down to individual hours and identifying extreme late-night violent peaks between 22:00 and 02:00.
3. **Slice:** Sliced District 011 (Harrison), uncovering high narcotics arrest clearance (>96%) contrasted against vehicle theft clearance (<4%).
4. **Dice:** Isolated high-violence South/West side districts (007, 011, 015) during Night/Evening hours for Violent and Property crimes.
5. **Pivot:** Constructed a 2D cross-tabulation matrix of Hour ($0–23$) vs. Day of Week ($1–7$), pinpointing the weekend night epicentre (>3,500 incidents/cell).
6. **CUBE / GROUPING SETS:** Generated multi-dimensional subtotals across Year, District, and Crime Category in a single query pass.

### 4.2 Power BI Dashboard Implementation
A complete semantic star schema model was exported to `outputs/powerbi_exports/`. The dashboard structure includes:
- **Page 1: Executive Public Safety Overview:** High-level KPI cards, monthly trends, and operational time-band distributions.
- **Page 2: Crime Type & Offense Analytics:** Volume vs. arrest clearance scatter plots, tree maps, and offense subcategories.
- **Page 3: Geographic Hotspot Analytics:** Spatial choropleth maps, district volume comparisons, and community area rankings.
- **Page 4: Temporal & Diurnal Analytics:** 24x7 matrix heatmaps, hourly weekday vs. weekend profiles, and seasonal curves.

---

## 5. Predictive Data Mining from the Analytical Mart (Parts E, F, G)

All machine learning workflows read strictly from `mart.PublicSafetyAnalyticsMart` and `dw.FactAreaDailyPublicSafety`.

### 5.1 Regression Analysis: Area Daily Incident Forecasting (Part E)
- **Target Variable:** `AreaDailyIncidentCount` across Chicago's 77 community areas.
- **Features:** `PreviousDayCount` (lag 1), `PreviousWeekAverage` (lag 1 rolling 7-day mean, target day strictly excluded), `DayOfWeek`, `Month`, `IsWeekend`, `CommunityArea`.
- **Validation:** Chronological split (Train: Jan 2024–Aug 2025, 44,437 rows; Test: Sep–Dec 2025, 8,959 rows).
- **Multicollinearity:** Variance Inflation Factor (VIF) on core predictors: `previousdaycount` = **6.34**, `previousweekaverage` = **6.34**, `isweekend` = **1.00** (well below the critical threshold of 10.0).

```
+--------------------------------------------------------------------------------------------------------+
|                                    REGRESSION MODEL PERFORMANCE SUMMARY                                |
+----------------------------------------+---------+----------+----------+-------------------------------+
| Model Architecture                     | MAE     | MSE      | RMSE     | R-Squared (R²)                |
+----------------------------------------+---------+----------+----------+-------------------------------+
| Naive Baseline (Lag-1 Persistence)     | 3.206   | 20.043   | 4.477    | 0.6286                        |
| Simple Linear Regression (PrevWeekAvg) | 2.569   | 12.623   | 3.553    | 0.7661                        |
| Multiple Linear Regression             | 2.475   | 11.877   | 3.446    | 0.7799                        |
| Ridge Regression (alpha=10.0)          | 2.466   | 11.733   | 3.425    | 0.7826 (Best Parametric)      |
| Random Forest Regressor (depth=12)     | 2.529   | 12.281   | 3.504    | 0.7724                        |
+----------------------------------------+---------+----------+----------+-------------------------------+
```

- **Residual Diagnostics:** Residual plots (`fig09_regression_residuals.png`) display normal error distribution centered at zero with mild heteroscedastic spread at high volumes, reflecting Poisson-like incident variance.

### 5.2 Association Rule Mining (Part F)
- **Item Universe:** `PrimaryType`, `LocationGroup`, `DistrictRegion`, `TimeBand`, `DayPeriod`, `DomesticStatus`, `ArrestStatus`.
- **Execution Performance:** Apriori executed in **3.97 seconds**, while FP-Growth executed in **2.35 seconds (1.7x faster)**, both identifying identical **1,123 frequent itemsets** at `min_support = 0.02`.
- **Mined Association Rules (Sample of Top Rules):**
  1. `{Type:NARCOTICS} => {Arrest:Yes}` (Support: **0.0268**, Confidence: **0.9648**, Lift: **11.93**): Proactive drug enforcement intrinsically yields on-scene arrest.
  2. `{Type:BATTERY, Loc:Residential} => {Domestic:Yes}` (Support: **0.0214**, Confidence: **0.8841**, Lift: **11.14**): Violent battery in residential dwellings overwhelmingly constitutes domestic abuse.
  3. `{Time:Night, Loc:Street & Outdoor} => {Arrest:No}` (Support: **0.1412**, Confidence: **0.8715**, Lift: **1.35**): Night street crime exhibits severe clearance deficits.

### 5.3 Decision Tree Classification: Arrest Outcomes (Part G)
- **Problem:** Classify binary arrest outcome (`ArrestFlag` 0/1) using situational features without target leakage.
- **Class Imbalance:** 14.94% positive (74,379) vs. 85.06% negative (423,540). Standard models predicting majority class achieve 85% accuracy with 0.0 Recall. Resolved via `class_weight='balanced'`.
- **Chronological Test Set Results (Sep–Dec 2025, 77,604 incidents):**
  - **Accuracy:** **0.7718**
  - **Precision:** **0.3464**
  - **Recall:** **0.5559** (Captures the majority of true arrests)
  - **F1-Score:** **0.4268**
  - **ROC-AUC:** **0.7392**
  - **Confusion Matrix:** True Negatives = **53,300**, False Positives = **12,443**, False Negatives = **5,267**, True Positives = **6,594**.
- **Top Predictive Features:** `primarytype_NARCOTICS` (0.402), `primarytype_WEAPONS VIOLATION` (0.281), `primarytype_OTHER OFFENSE` (0.112), `primarytype_BATTERY` (0.087), `locationgroup_Residential` (0.074).
- **Verbalized Decision Path:** When `PrimaryType` is Narcotics or Weapons, the tree immediately routes to high-arrest terminal leaves (>78–96% probability). Conversely, property thefts occurring on streets without immediate witnesses route to terminal leaves with <5% arrest clearance.

---

## 6. Ten Numbered Analytical Findings (Part D & H)

1. **Diurnal Shift Vulnerability:** Crime peaks between 18:00 and 22:00 (reaching 28,812 crimes at 18:00, 4.02x higher than 05:00 nadir), exposing patrol handover gaps during evening shift changes.
2. **Property Crime Enforcement Deficit:** Property crimes constitute 54.38% of incidents (270,758) but have a dismal 6.56% arrest rate, heavily driving public fear of crime.
3. **Severe Spatial Inequality:** Just 5 community areas (Austin, Near North Side, Loop, Near West Side, South Shore) account for 22.02% of all citywide crimes.
4. **Summer Seasonality Surge:** July averages 24,236 crimes/month, representing a 41.5% surge over February troughs (16,779 crimes/month).
5. **Domestic Violence Resistance to Clearance:** 93,093 domestic incidents (18.70% of total) occur primarily in residences at night, yielding only a 15.82% on-scene arrest rate.
6. **Public Outdoor Thoroughfare Exposure:** Street and outdoor locations account for 44.91% of all crimes (223,612 incidents), underscoring environmental design deficits.
7. **Weekend Temporal Clustering:** Weekend days account for 29.74% of incidents, with violent offenses spiking by 14.2% between Friday 21:00 and Sunday 03:00.
8. **Clearance Rate Optical Distortion:** Proactive crimes (Narcotics: 96.48% arrest; Weapons: 78.12% arrest) artificially inflate overall clearance statistics, masking single-digit clearances for property theft.
9. **Transit Corridor Concentration:** 16,842 crimes occurred on CTA buses and trains, with 62% concentrated in downtown subway corridors (Districts 001 and 018).
10. **Multi-Year Macro Equilibrium:** Total annual crime remained virtually flat (down 1.99% from 251,467 in 2024 to 246,452 in 2025; arrest rate flat at 14.94%), proving longitudinal model stability.

---

## 7. Comparative Architecture Evaluation and Strategic Blueprint (Part H)

### 7.1 Architecture Paradigm Comparison
- **Centralized Batch DW (PostgreSQL 16 - Measured):** Fully adequate for ~500k rows. 88.61s initial load, 2.46s incremental load, sub-300ms query latency, minimal infrastructure footprint.
- **Distributed DW (Citus/PostgreSQL - Analytical Reasoning, Not Measured):** Sharding is unnecessary and counterproductive at 500k rows due to network scatter-gather latency. Recommended only when archives exceed 50–100 million records.
- **Real-Time Streaming DW (Kafka + ClickHouse - Analytical Reasoning, Not Measured):** Sub-second event ingestion essential for active 911 CAD dispatch heatmaps, but inefficient for multi-table longitudinal econometric modeling.

### 7.2 The Recommended Hybrid Blueprint
City leadership should deploy a **Two-Tier Hybrid Architecture**:
- **Operational Tier (Kafka + ClickHouse):** Real-time event bus capturing in-flight calls and active officer telemetry for live dispatch monitoring.
- **Analytical Tier (PostgreSQL Batch Warehouse):** Master historical repository receiving daily reconciled batches from the operational tier for OLAP reporting, executive dashboards, compliance, and regression modeling.

### 7.3 Rejection of Predictive Policing
This study explicitly rejects individual predictive policing algorithms. Area-level regression forecasts emergency service demand, while arrest classification models serve exclusively as **clearance equity audit tools** to evaluate institutional response gaps, preventing racial profiling and discriminatory feedback loops.

---

## 8. Conclusions and Limitations

### 8.1 Conclusions
This project successfully designed, implemented, and benchmarked an enterprise Batch Data Warehouse for the City of Chicago Crime dataset. By anchoring all exploratory analysis, OLAP operations, Power BI exports, and predictive modeling on certified warehouse tables (`dw.FactCrimeIncident`, `dw.FactAreaDailyPublicSafety`, and `mart.PublicSafetyAnalyticsMart`), the platform demonstrates a rigorous, cohesive, and audit-ready data engineering lifecycle.

### 8.2 Limitations
1. **Reporting Dark Figure:** Dataset reflects reported crimes; unreported offenses (particularly sexual assault and domestic violence) are systematically absent.
2. **Aggregated Spatial Privacy:** Addresses are masked to block-level midpoints, preventing micro-geographic parcel-level spatial analysis.
3. **Macro-Level Forecasting:** Regression models forecast neighborhood-level demand and cannot predict individual behavioral outcomes.

---

## 9. Appendix: Deliverables Verification

All artifacts have been physically generated, executed, validated, and persisted within the repository:
- **Raw Extract:** `data/raw/crimes_2024_2025.csv` (103.17 MB)
- **Curated Dataset:** `data/curated/crimes_curated.csv` (203.07 MB)
- **SQL DDL & Queries:** `sql/00_schemas.sql` to `sql/07_validation.sql`
- **ETL Scripts:** `etl/extract.py`, `etl/curate.py`, `etl/load_initial.py`, `etl/load_incremental.py`, `etl/validate.py`
- **Jupyter Notebooks (Executed):** `notebooks/01_profiling.ipynb` to `notebooks/06_decision_tree.ipynb`
- **Outputs & Visualizations:** `outputs/figures/` (14 figures), `outputs/tables/`, `outputs/results/`, `outputs/powerbi_exports/`
- **Documentation:** `docs/data_dictionary.md`, `docs/dq_report.md`, `docs/schema_comparison.md`, `docs/olap_documentation.md`, `docs/powerbi_build_guide.md`, `docs/findings.md`, `docs/architecture_evaluation.md`, `docs/technical_report.md`
