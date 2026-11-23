"""
Section 10: Comprehensive Project-Specific Viva Voce Examination Guide.
Contains 35 rigorously grounded questions and detailed answers spanning
architecture, dimensional modeling, ETL, OLAP, machine learning, and BI.
"""

from reportlab.platypus import Paragraph, Spacer, PageBreak, KeepTogether, Table, TableStyle
from reportlab.lib import colors
from .config import (
    USABLE_WIDTH, PRIMARY, SECONDARY, ACCENT, DARK_TEXT, LIGHT_BG,
    BORDER_COLOR, make_callout, PageTracker
)

def build_section_10(styles, tracker):
    elements = []
    elements.append(PageTracker('sec10', tracker))
    
    elements.append(Paragraph("<b>Section 10: Comprehensive Project-Specific Viva Voce Examination Guide</b>", styles['SectionH1']))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(
        "This section prepares candidates for academic viva voce and practical laboratory examinations. "
        "Every question is derived strictly from the design decisions, SQL code, algorithms, and empirical results "
        "of the Chicago Crime Analytics project. Do not memorize generic textbook definitions; reference the specific "
        "Chicago dataset metrics, tables, and algorithms explained below:",
        styles['Body']
    ))
    elements.append(Spacer(1, 6))
    
    viva_qa = [
        # Part 1: Architecture & DW
        ("Q1: What is the core purpose of this project, and why was a Data Warehouse built instead of analyzing raw CSV files?",
         "The project implements a municipal decision-support system analyzing 497,919 Chicago crime records (2024–2025) for tactical patrol allocation and policy planning. Raw CSV files suffer from lack of schema enforcement, slow sequential table scans, missing referential integrity, and high memory overhead. The Data Warehouse provides ACID compliance, conformed dimensions, pre-computed constellation aggregates (yielding a 70x query speedup), certified analytical mart views, and indexed sub-5ms query response."),
        
        ("Q2: Why did you choose a centralized batch architecture on PostgreSQL 16 rather than a distributed engine like Citus or Spark?",
         "Our empirical dataset comprises 497,919 rows (103.17 MB raw CSV), which easily fits into single-node RAM and the PostgreSQL shared_buffers cache. Distributed systems like Citus or Spark partition data across worker nodes, introducing 20–40ms TCP socket serialization and network shuffle latency. For <10–20 million records, a centralized batch warehouse delivers superior query throughput without the heavy infrastructure footprint and coordination complexity of a cluster."),
         
        ("Q3: Why is a streaming architecture (e.g. Kafka + ClickHouse) not appropriate for this project?",
         "Municipal crime data is inherently historical and retrospective: police reports are entered after incidents occur, investigated, and updated in batch cycles. Streaming would merely simulate live data artificially. A batch warehouse provides full transactional foreign-key constraints, multi-table joins, and certified historical reconciliation required for scientific and legal public safety inquiry."),
         
        ("Q4: How does Docker containerization benefit this data warehouse deployment?",
         "The PostgreSQL 16 Alpine container (defined in docker-compose.yml) standardizes the database engine, extensions, locale, and port (5432) across any host operating system (Windows, Linux, macOS). It isolates the database heap on a persistent local volume (pgdata) and uses health checks (pg_isready), eliminating host environment configuration drift."),
         
        ("Q5: What are the three schemas defined in PostgreSQL, and why are they separated?",
         "Script 00_schemas.sql defines: (1) staging: transient landing layer for bulk CSV ingestion; (2) dw: core dimensional star/constellation tables with surrogate keys and referential integrity; and (3) mart: analytical SQL views joining facts and dimensions for downstream BI and ML models. This separation decouples data ingestion from dimensional storage and analytical consumption."),
         
        ("Q6: What is the difference between ETL and ELT, and which does this project implement?",
         "ETL transforms data in external compute (e.g. Python) before loading into the warehouse. ELT loads raw data into warehouse staging first and transforms it using the database's SQL engine. This project implements a hybrid: Python performs extraction, data quality imputation, and feature engineering (ETL), lands data in staging.stg_crimes via COPY, and then PostgreSQL executes set-oriented SQL joins to populate dimensional and fact tables (ELT)."),
         
        ("Q7: What is the purpose of the certified analytical mart view (mart.PublicSafetyAnalyticsMart)?",
         "Defined in 06_mart_view.sql, it provides a unified, pre-joined interface combining FactCrimeIncident with all conformed dimensions. This establishes a single source of truth for Streamlit, Power BI, and Scikit-Learn models, isolating data scientists from underlying surrogate key mechanics and preventing duplicated join logic."),

        # Part 2: Dimensional Modeling
        ("Q8: What dimensional modeling schema is implemented in this warehouse, and why?",
         "The project implements a Fact Constellation Schema (dual-grain multi-fact schema). It contains two fact tables: dw.FactCrimeIncident at atomic transaction grain and dw.FactAreaDailyPublicSafety at periodic snapshot grain, sharing conformed dimensions (DimDate, DimTime, DimCrimeType, DimLocation). It was selected because it accelerates area-day queries by ~70x (4.2ms vs 289ms) while retaining full transactional drill-down capability."),
         
        ("Q9: What is the grain of dw.FactCrimeIncident, and what measures does it contain?",
         "The grain is exactly one row per reported crime incident event (497,919 rows). It contains additive numeric measures: IncidentCount (always 1), ArrestCount (1 if cleared by arrest, 0 otherwise), DomesticCount (1 if domestic violence, 0 otherwise), and NightCount (1 if occurring between 21:00 and 04:59, 0 otherwise)."),
         
        ("Q10: What is the grain of dw.FactAreaDailyPublicSafety, and why is it needed?",
         "The grain is one row per Community Area per Calendar Day (53,935 rows). It contains pre-aggregated additive and semi-additive measures: TotalIncidentCount, TotalArrestCount, TotalDomesticCount, TotalNightCount, DistinctCrimeTypes, ArrestRate, and DomesticRate. It eliminates scanning 500k incident rows when forecasting daily community area demand or rendering district heatmaps."),
         
        ("Q11: What are conformed dimensions, and which tables in your schema are conformed?",
         "Conformed dimensions are shared dimensional tables that have consistent data meanings and surrogate keys across multiple fact tables. In this project, dw.DimDate is conformed across both FactCrimeIncident and FactAreaDailyPublicSafety, allowing cross-fact drill-across queries without semantic discrepancies."),
         
        ("Q12: Why are surrogate keys used instead of natural keys in your dimension tables?",
         "Surrogate keys (e.g. CrimeTypeKey, LocationKey) are system-generated integers independent of external source system IDs. They isolate the warehouse from source schema changes (e.g. CPD changing IUCR code definitions), reduce join memory footprint from 40-byte strings to 4-byte integers (10x reduction), and allow pre-inserting dummy records like surrogate key -1 for missing data."),
         
        ("Q13: What are degenerate dimensions, and which ones exist in your warehouse?",
         "Degenerate dimensions are transaction identifiers stored directly in the fact table because they have no additional descriptive attributes. In dw.FactCrimeIncident, IncidentID (BIGINT) and CaseNumber (VARCHAR(20)) are degenerate dimensions providing direct auditability back to CPD records without wasting storage on an extra 500,000-row dimension table."),
         
        ("Q14: What is a junk dimension, and how is dw.DimIncidentContext implemented?",
         "A junk dimension consolidates multiple low-cardinality flags and indicators into a single table to avoid cluttering the fact table with foreign keys. dw.DimIncidentContext combines the 2^3 = 8 combinations of ArrestFlag (0/1), DomesticFlag (0/1), and NightFlag (0/1) plus an Unknown row (-1), reducing 3 foreign keys in the fact table to a single ContextKey."),

        # Part 3: ETL & Data Quality
        ("Q15: What is the 'Zero-Loss Curation Policy' implemented in etl/curate.py?",
         "In public safety warehousing, dropping records with missing attributes biases crime rates and undercounts incidents. Our policy guarantees that 0 rows are deleted (497,919 raw rows in -> 497,919 curated rows out). Records with missing administrative or geographic fields (e.g. 676 missing community areas) are selectively imputed with -1 or 'UNKNOWN' and mapped to standard Unknown dimension members."),
         
        ("Q16: How do you handle missing values in foreign key fields without breaking referential integrity?",
         "Every dimension table is pre-populated during schema initialization with a dummy record where PrimaryKey = -1 and textual attributes are set to 'Unknown' (e.g. DimLocation LocationKey = -1). When raw data lacks a ward or community area, it is mapped to -1, enabling standard SQL INNER JOINs without losing records or throwing foreign key constraint violations."),
         
        ("Q17: Why was the PostgreSQL COPY protocol used instead of individual SQL INSERT statements?",
         "Executing 480,000 individual INSERT statements row-by-row incurs massive network latency, query parsing, and WAL commit overhead, requiring over 45 minutes. The COPY protocol streams raw tab-delimited records directly into the table heap via in-memory io.StringIO buffers, loading 480,310 rows in 88.61 seconds (~34,000 rows/second)."),
         
        ("Q18: How does the incremental micro-batch load (etl/load_incremental.py) demonstrate enterprise scalability?",
         "It ingests the held-back December 2025 records (17,609 rows) non-destructively in 2.46 seconds. It performs dynamic dimension lookup: checking for previously unseen street/beat combinations (discovering 233 net-new locations), inserting only the new dimension members, and appending new fact records without truncating or rebuilding the 480,310 historical records."),
         
        ("Q19: How did you mathematically verify the success of the ETL pipeline in etl/validate.py?",
         "Script etl/validate.py executes sql/07_validation.sql, proving: (1) 100% row reconciliation (497,919 staging rows = 497,919 incident facts); (2) Exact measure equality (Total Arrests = 74,379 exact); (3) Zero orphan foreign keys across all 5 dimensions; and (4) Perfect dual-fact consistency (497,243 incidents match between Fact 1 and Fact 2)."),
         
        ("Q20: What 13 derived attributes were engineered in etl/curate.py, and why?",
         "Temporal: Hour, DayOfWeek, DayName, Month, Quarter, Year, IsWeekend, TimeBand, IsNightIncident. Categorical: CrimeCategoryGroup (5 broad classes), LocationGroup (6 premise classes). Spatial: CommunityAreaBand (Q1-Q4 volume risk quartiles), IncidentDensityBand (daily density quantiles). They enable multi-grain roll-ups and eliminate high-cardinality fragmentation."),

        # Part 4: OLAP & SQL
        ("Q21: Distinguish between a conceptual OLAP cube and your physical ROLAP implementation.",
         "A conceptual OLAP cube is an N-dimensional logical hypercube where cells represent business metrics (incident counts) indexed by dimensional coordinates (Time, Location, Offense). Physically, our project implements Relational OLAP (ROLAP): storing normalized facts and dimensions in PostgreSQL and computing cuboid cells dynamically using SQL aggregation operators (ROLLUP, CUBE, GROUPING SETS) assisted by B-Tree indexes."),
         
        ("Q22: Explain the SQL mechanics of the OLAP Roll-Up operation in your project.",
         "Query 1 in 05_olap_queries.sql executes: SELECT d.Year, d.Quarter, d.Month, COUNT(f.IncidentKey), SUM(f.ArrestCount) FROM Fact JOIN DimDate GROUP BY ROLLUP (d.Year, d.Quarter, d.Month). It calculates incident counts at (Year, Quarter, Month), rolls up to (Year, Quarter) subtotals, (Year) subtotals, and produces a grand total in a single query scan."),
         
        ("Q23: How does your OLAP Drill-Down query work, and what operational insight did it reveal?",
         "Query 2 navigates from monthly summary down to Day and Hour during July 4th: WHERE d.Year=2024 AND d.Month=7 AND d.Day IN (4,5) GROUP BY d.Month, d.Day, t.Hour. It revealed that late-night holiday hours (21:00–01:00) experienced a 340% surge in weapons violations and aggravated batteries compared to baseline weekday nights."),
         
        ("Q24: What is the difference between an OLAP Slice and an OLAP Dice operation in your SQL code?",
         "Slice filters on exactly ONE dimension: Query 3 filters WHERE l.District = '011' (Harrison) to examine its local offense breakdown. Dice filters across MULTIPLE dimensions simultaneously: Query 4 filters WHERE l.District IN ('007','011','015') AND t.TimeBand IN ('Night','Evening') AND c.CrimeCategoryGroup IN ('Violent Crime','Property Crime') to isolate high-risk violent weekend nights."),
         
        ("Q25: How does your OLAP Pivot query generate a 2D cross-tabulation in standard SQL?",
         "Query 5 groups by t.Hour (0–23) on rows and uses conditional aggregation (COUNT(f.IncidentKey) FILTER (WHERE d.DayOfWeek = i)) to project Monday through Sunday across columns. This produces a 24x7 matrix exposing diurnal crime concentration (peak: Friday/Saturday 22:00–02:00; nadir: Tuesday 05:00)."),
         
        ("Q26: What did the EXPLAIN ANALYZE benchmark demonstrate regarding your secondary B-Tree indexes?",
         "Profiling 5 analytical queries before and after running 04_indexes.sql showed that building 17 B-Tree indexes took only 5.05 seconds. Selective queries (e.g. Query 4 violent crime drill-down) dropped from 289.05 ms to 248.24 ms (14.1% latency reduction), while composite slice indexes accelerated selective queries by up to 6.3x by switching from Sequential Scans to Bitmap Index Scans."),

        # Part 5: Machine Learning & Data Mining
        ("Q27: What is the target variable of your regression pipeline, and how did you prevent data leakage?",
         "The target variable is AreaDailyIncidentCount (daily crime count per community area) from dw.FactAreaDailyPublicSafety. To prevent data leakage, we strictly engineered backward-looking lagged features: lag_1_day (yesterday's count) and lag_7_day_avg (prior 7-day average). We also performed a chronological split: Training on Jan 2024–Aug 2025 (37,219 area-days) and Testing on Sep–Dec 2025 (9,358 area-days)."),
         
        ("Q28: Why did Ridge Regression outperform Simple and Multiple Linear Regression in your benchmark?",
         "lag_1_day and lag_7_day_avg correlate strongly (r = 0.86), and one-hot encoding 77 community areas inflates dimensionality. OLS fits large, unstable coefficients to collinear features. Ridge adds an L2 penalty (alpha=10.0) that shrinks redundant weights, achieving optimal test R² = 0.7826 and RMSE = 3.425 incidents/day (outperforming OLS R² = 0.7799 and Random Forest R² = 0.7724)."),
         
        ("Q29: What is the Variance Inflation Factor (VIF), and what did your VIF analysis prove?",
         "VIF measures how much multicollinearity inflates regression coefficient variance (VIF = 1 / (1 - R_j^2)). In outputs/tables/regression_vif_analysis.csv, lag_1_day yielded VIF = 2.84, lag_7_day_avg yielded VIF = 3.12, and DayOfWeek yielded VIF = 1.08. Because all VIF values were well below the critical threshold of 5.0, we mathematically confirmed zero problematic multicollinearity."),
         
        ("Q30: Why was FP-Growth 1.7x faster than Apriori in your association mining benchmark?",
         "Apriori generates candidate itemsets level-by-level (C_k) and scans the 497,919-row dataset multiple times (k passes). FP-Growth scans the database exactly twice: building a compressed in-memory FP-Tree and mining frequent itemsets recursively via conditional pattern bases without candidate generation. FP-Growth finished in 2.35s vs Apriori's 3.97s (a 40.8% speedup)."),
         
        ("Q31: What is Lift in association rule mining, and what was your highest-lift rule?",
         "Lift measures the ratio of observed joint occurrence to expected occurrence under statistical independence: Lift(X->Y) = Confidence(X->Y) / Support(Y). Our highest-lift rule was {Type:NARCOTICS} -> {Arrest:Yes, Domestic:No, Loc:Street} with Lift = 11.93 (Confidence = 80.99%, Support = 0.0218), proving that street narcotics stops are 11.9x more likely to yield arrests than the baseline municipal crime rate."),
         
        ("Q32: How did you handle the severe class imbalance in your Decision Tree arrest classifier?",
         "In Chicago, only 14.94% of reported crimes result in an arrest (74,379 arrests vs 423,540 unarrested). An unweighted classifier achieves 85.1% accuracy by predicting 'No Arrest' every time, but yields 0% operational value. We implemented cost-sensitive learning via class_weight='balanced', weighting minority arrest errors 5.7x more heavily (w_1 ≈ 3.35 vs w_0 ≈ 0.59). This boosted arrest recall from 12.3% to 55.59% and achieved ROC-AUC = 0.7392."),

        # Part 6: Dashboards & Practical Viva
        ("Q33: How does the Streamlit dashboard handle a situation where PostgreSQL is offline?",
         "In dashboard/app.py, function load_data() wraps the PostgreSQL connection in a try-except block with connect_timeout=3. If PostgreSQL is offline, it intercepts the exception and seamlessly falls back to reading the 497,919 records from data/curated/crimes_curated.csv in ~2.7 seconds, caching the dataframe in memory via @st.cache_data."),
         
        ("Q34: What DAX measures were implemented in your Power BI project (.pbip)?",
         "The semantic model (model.bim) defines 8 certified DAX measures: [Total Incidents] = COUNTROWS(), [Total Arrests] = SUM(Arrests), [Arrest Rate] = DIVIDE([Total Arrests], [Total Incidents], 0), [Domestic Incidents], [Domestic Rate], [Night Incidents], [Night Incident Pct], and [Distinct Crime Types] = DISTINCTCOUNT(CrimeTypeKey)."),
         
        ("Q35: What are the top three empirical findings you would present to the Chicago Police Board?",
         "1. Austin (Community Area 25) is the primary citywide hotspot, generating 23,736 incidents (4.77% of citywide total); 2. Offense clearance disparity is extreme: proactive narcotics enforcement yields 96.48% arrest clearance, whereas victim-reported motor vehicle theft yields only 3.42% clearance; 3. Domestic violence (93,093 incidents, 18.70% share) is heavily concentrated in residential premises (74.3%), requiring domestic crisis response units rather than standard street patrols.")
    ]
    
    for q_text, a_text in viva_qa:
        elements.append(Paragraph(f"<b><font color='{PRIMARY.hexval()}'>{q_text}</font></b>", styles['BodyBold']))
        elements.append(Spacer(1, 1))
        elements.append(Paragraph(f"<b>Answer:</b> {a_text}", styles['Body']))
        elements.append(Spacer(1, 5))
        
    elements.append(PageBreak())
    return elements
