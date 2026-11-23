"""
Section 9: Master Concept-to-Implementation Mapping Catalog.
Connects all 38 core concepts to their exact physical files, SQL scripts,
Python functions, and notebook implementations.
"""

from reportlab.platypus import Paragraph, Spacer, PageBreak, KeepTogether, Table, TableStyle
from reportlab.lib import colors
from .config import (
    USABLE_WIDTH, PRIMARY, SECONDARY, ACCENT, DARK_TEXT, LIGHT_BG,
    BORDER_COLOR, make_callout, make_table, PageTracker
)

def build_section_9(styles, tracker):
    elements = []
    elements.append(PageTracker('sec9', tracker))
    
    elements.append(Paragraph("<b>Section 9: Master Concept-to-Implementation Mapping Catalog</b>", styles['SectionH1']))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(
        "This master reference table connects every theoretical concept, algorithm, and methodology directly to its exact "
        "executable implementation in the repository. Use this catalog for rapid code navigation during practical exams and viva voce examinations:",
        styles['Body']
    ))
    elements.append(Spacer(1, 6))
    
    mapping_rows = [
        ["Major Technical Concept", "How the Chicago Crime DW Uses It", "Exact File / Code Location"],
        ["1. Batch Warehouse Architecture", "Centralized single-node PostgreSQL 16 container storing 497,919 records.", "docker-compose.yml; sql/00_schemas.sql"],
        ["2. Data Staging Layer", "Unindexed landing table (staging.stg_crimes) populated via bulk COPY protocol.", "sql/01_staging.sql; etl/load_initial.py (L127-145)"],
        ["3. Multi-Threaded Extraction", "ThreadPoolExecutor (6 workers) chunking SoQL API queries by 50,000 rows.", "etl/extract.py (L20-75); docs/source_log.md"],
        ["4. Pre-Cleaning Profiling", "Audits nulls, duplicate keys, coordinates bounding boxes, and timestamp validity.", "etl/profile_data.py; outputs/tables/missing_profile.csv"],
        ["5. Zero-Loss Curation Policy", "Retains 100% of incident records (0 dropped); maps missing spatial tags to -1/UNKNOWN.", "etl/curate.py (L80-140); docs/dq_report.md"],
        ["6. Temporal Feature Decomposition", "Decomposes ISO timestamp into Hour, DayOfWeek, DayName, Month, Quarter, Year, TimeBand.", "etl/curate.py (L190-215); docs/data_dictionary.md"],
        ["7. Domain Categorical Binning", "Maps 31 primary types -> 5 Crime Categories; maps 134 premises -> 6 Location Groups.", "etl/curate.py (L23-78); dashboard/app.py (L199-209)"],
        ["8. Spatial Discretization", "Calculates CommunityAreaBand quartiles and daily IncidentDensityBand quantiles.", "etl/curate.py (L220-285); DimLocation schema"],
        ["9. Fact Constellation Schema", "Dual-grain schema: FactCrimeIncident (atomic) + FactAreaDailyPublicSafety (aggregate).", "sql/03_facts.sql; docs/erd/constellation_schema_erd.png"],
        ["10. Transaction Fact Table", "Stores 497,919 individual crime events with additive measures (IncidentCount, ArrestCount).", "sql/03_facts.sql (L7-30); etl/load_initial.py (L240-260)"],
        ["11. Periodic Snapshot Fact", "Stores 53,935 area-daily aggregated status rows; accelerates area queries by 70x.", "sql/03_facts.sql (L31-52); etl/load_initial.py (L261-290)"],
        ["12. Conformed Dimensions", "Shared dimensions (DimDate, DimTime, DimCrimeType, DimLocation) across both facts.", "sql/02_dims.sql; etl/load_initial.py (L43-100)"],
        ["13. Surrogate Keys", "Integer primary keys (DateKey YYYYMMDD, CrimeTypeKey, LocationKey) isolating source schema.", "sql/02_dims.sql; etl/load_initial.py (L150-205)"],
        ["14. Degenerate Dimensions", "IncidentID (BIGINT) and CaseNumber (VARCHAR(20)) stored directly in fact table.", "sql/03_facts.sql (L19-20); docs/data_dictionary.md"],
        ["15. Junk Dimension", "DimIncidentContext consolidating ArrestFlag, DomesticFlag, NightFlag (8 rows).", "sql/02_dims.sql (L100-125); sql/03_facts.sql (L17)"],
        ["16. Unknown Member (-1)", "Dummy row with PK=-1 pre-inserted in all dimensions to eliminate NULL foreign keys.", "sql/02_dims.sql (L25-29, 43-46, 63-67, 94-98)"],
        ["17. Analytical Mart SQL View", "mart.PublicSafetyAnalyticsMart joining facts and dimensions for BI and ML.", "sql/06_mart_view.sql; dashboard/app.py (L54-69)"],
        ["18. B-Tree Secondary Indexing", "17 analytical B-Tree indexes on foreign keys and composite slices built in 5.05 s.", "sql/04_indexes.sql; etl/benchmark_indexes.py"],
        ["19. Bulk COPY Ingestion", "Streams 480,310 rows via io.StringIO into PostgreSQL in 88.61 s (~34k rows/sec).", "etl/load_initial.py (L135-145); psycopg2 cur.copy_from"],
        ["20. Incremental Micro-Batch", "Ingests held-back Dec 2025 records (17,609 rows) non-destructively in 2.46 s.", "etl/load_incremental.py; outputs/results/incremental_load.md"],
        ["21. Reconciliation Auditing", "Verifies 497,919 / 497,919 row match, 0 orphan keys, exact measure equality.", "etl/validate.py; sql/07_validation.sql; validation_report.md"],
        ["22. EXPLAIN ANALYZE Benchmark", "Profiles execution times pre- and post-indexing across 5 multi-dimensional queries.", "etl/benchmark_indexes.py; outputs/results/query_timings.csv"],
        ["23. Conceptual OLAP Cube", "Multidimensional hypercube spanned by Time, Location, and Crime Category axes.", "docs/olap_documentation.md; pdf_assets/olap_cube_concept.png"],
        ["24. OLAP Roll-Up", "Aggregates temporal hierarchy: Month -> Quarter -> Year -> Grand Total.", "sql/05_olap_queries.sql (L8-18); etl/run_olap_and_dashboard.py"],
        ["25. OLAP Drill-Down", "Navigates down to hourly grain during July 4th peak summer holiday window.", "sql/05_olap_queries.sql (L20-34); etl/run_olap_and_dashboard.py"],
        ["26. OLAP Slice", "Filters on single dimension: District = '011' Harrison crime breakdown.", "sql/05_olap_queries.sql (L36-48); etl/run_olap_and_dashboard.py"],
        ["27. OLAP Dice", "Multi-dimensional sub-cube: Districts (007,011,015) x Night/Evening x Violent/Property.", "sql/05_olap_queries.sql (L50-66); etl/run_olap_and_dashboard.py"],
        ["28. OLAP Pivot", "Rotates axes to produce 2D cross-tabular matrix: Hour of Day x Day of Week.", "sql/05_olap_queries.sql (L68-83); dashboard/app.py (L336-350)"],
        ["29. CUBE / GROUPING SETS", "Computes simultaneous multi-grain aggregations across Year, District, and Category.", "sql/05_olap_queries.sql (L85-104); etl/run_olap_and_dashboard.py"],
        ["30. Time-Lag Feature Engineering", "Engineers lag_1_day and lag_7_day_avg without temporal data leakage.", "etl/run_ml_models.py (L65-95); notebooks/04_regression.ipynb"],
        ["31. Multiple Linear Regression", "Parametric OLS regression modeling area-daily demand (R² = 0.7799).", "etl/run_ml_models.py (L100-115); notebooks/04_regression.ipynb"],
        ["32. Ridge Regression (L2)", "Regularized champion model (alpha=10.0) shrinking collinear weights (R² = 0.7826).", "etl/run_ml_models.py (L115-135); fig09, fig10"],
        ["33. VIF Multicollinearity Check", "Computes VIF for all regression predictors, confirming all VIF < 5.0 (no collinearity).", "etl/run_ml_models.py (L145-165); outputs/tables/regression_vif.csv"],
        ["34. Apriori Rule Mining", "Level-wise candidate generation mining 1,123 frequent itemsets in 3.97 s.", "etl/run_ml_models.py (L180-220); notebooks/05_association.ipynb"],
        ["35. FP-Growth Rule Mining", "FP-Tree divide-and-conquer mining 1,123 itemsets in 2.35 s (1.7x faster than Apriori).", "etl/run_ml_models.py (L220-270); outputs/tables/association_rules.csv"],
        ["36. Balanced CART Decision Tree", "Class-balanced decision tree (depth=5) classifying arrest clearance (ROC-AUC = 0.7392).", "etl/run_ml_models.py (L280-450); fig12, fig13, fig14"],
        ["37. Reactive Streamlit BI App", "4-page browser BI dashboard with live PostgreSQL connection and resilient CSV fallback.", "dashboard/app.py (L1-360)"],
        ["38. Power BI Developer Project", "Ready-to-open PBIP project with Tabular Model (.bim) and 8 certified DAX measures.", "powerbi/ChicagoCrimeAnalytics.pbip; model.bim"]
    ]
    elements.append(make_table(mapping_rows, col_widths=[120, 235, USABLE_WIDTH - 355], headers=True, styles=styles))
    
    elements.append(PageBreak())
    return elements
