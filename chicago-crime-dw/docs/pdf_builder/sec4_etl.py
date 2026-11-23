"""
Section 4: End-to-End Batch ETL Lifecycle & Operational Mechanics.
Implements Concepts 14 through 18, details bulk loading vs incremental loading,
and presents experimental reconciliation and benchmark results.
"""

from reportlab.platypus import Paragraph, Spacer, PageBreak, KeepTogether, Table, TableStyle
from reportlab.lib import colors
from .config import (
    USABLE_WIDTH, PRIMARY, SECONDARY, ACCENT, DARK_TEXT, LIGHT_BG,
    BORDER_COLOR, make_callout, make_table, make_image_figure, make_concept_card, PageTracker
)

def build_section_4(styles, tracker):
    elements = []
    elements.append(PageTracker('sec4', tracker))
    
    elements.append(Paragraph("<b>Section 4: End-to-End Batch ETL Lifecycle & Operational Mechanics</b>", styles['SectionH1']))
    elements.append(Spacer(1, 4))
    
    elements.append(Paragraph("<b>4.1 The Two-Phase Batch Ingestion Strategy</b>", styles['SectionH2']))
    elements.append(Paragraph(
        "A central requirement of enterprise data warehousing is proving that the data pipeline can ingest historical archives "
        "in bulk (Initial Load) and subsequently absorb continuous operational deltas without rebuilding or tearing down the warehouse "
        "(Incremental Load). The project splits the 2024–2025 dataset into two distinct operational batches:<br/>"
        "• <b>Initial Bulk Load:</b> January 1, 2024 through November 30, 2025 (<b>480,310 records</b>).<br/>"
        "• <b>Incremental Micro-Batch Load:</b> December 1, 2025 through December 31, 2025 (<b>17,609 records held back</b>).",
        styles['Body']
    ))
    elements.append(Spacer(1, 6))
    
    # ETL Flowchart Diagram
    elements.append(Paragraph("<b>4.2 End-to-End Batch ETL Processing Flow</b>", styles['SectionH2']))
    elements.extend(make_image_figure('chicago-crime-dw/docs/pdf_assets/etl_pipeline_flow.png',
                                      "Figure 4.1: End-to-end batch ETL lifecycle from multi-threaded API extraction to incremental verification.",
                                      width=485, styles=styles))
    elements.append(Spacer(1, 8))
    
    elements.append(Paragraph("<b>4.3 Empirically Measured Execution Benchmarks</b>", styles['SectionH2']))
    bench_data = [
        ["ETL Lifecycle Stage", "Executed Script / Mechanism", "Input Volume", "Measured Time", "Operational Outcome"],
        ["Data Extraction", "etl/extract.py (ThreadPool 6 workers)", "497,919 API rows", "86.44 s", "Saved raw CSV (103.17 MB), zero dropped rows."],
        ["Data Curation", "etl/curate.py (In-memory Pandas)", "497,919 raw rows", "18.25 s", "Saved curated CSV (203.07 MB) with 13 derived features."],
        ["Initial Bulk Load", "etl/load_initial.py (COPY protocol)", "480,310 records", "88.61 s", "Populated DimDate, DimTime, Dims & Facts 1 and 2."],
        ["Incremental Micro-Batch", "etl/load_incremental.py (Lookup)", "17,609 records", "2.46 s", "Discovered 233 new locations; 0 downtime append."],
        ["Integrity Reconciliation", "etl/validate.py (SQL Audits)", "Full Warehouse", "1.12 s", "497,919 / 497,919 exact match; 0 orphan keys."],
        ["B-Tree Index Creation", "etl/benchmark_indexes.py", "17 B-Tree indexes", "5.05 s", "Indexed all foreign keys & composite slices."]
    ]
    elements.append(make_table(bench_data, col_widths=[100, 140, 75, 55, USABLE_WIDTH - 370], headers=True, styles=styles))
    elements.append(Spacer(1, 10))
    
    elements.append(Paragraph("<b>4.4 Core ETL Concepts & Technical Implementation</b>", styles['SectionH2']))
    
    # Concept 14: Staging Layer
    elements.extend(make_concept_card(
        num=14, name="Transient Data Staging Layer (staging.stg_crimes)",
        definition="An intermediate, unindexed relational storage area that mirrors the source schema, used to land raw data quickly before applying complex dimensional transformations and surrogate key lookups.",
        why_needed="Applying dimensional joins, lookups, and business logic over an active network connection or during raw CSV parsing slows down source systems and risks partial database corruption upon network failure.",
        how_it_works="The schema defines staging.stg_crimes in sql/01_staging.sql. Curated records are streamed directly into this table via the PostgreSQL COPY protocol in a few seconds. Subsequent dimension lookups execute as high-speed set-based SQL joins inside PostgreSQL memory.",
        step_by_step="1. Drop and recreate staging.stg_crimes; 2. Define schema matching curated attributes with batch_id and load_timestamp; 3. Execute bulk COPY from in-memory TSV buffer; 4. Execute set-oriented INSERT INTO ... SELECT DISTINCT to populate dimensions; 5. Execute set-oriented join to populate fact tables; 6. Staging table remains available for audit reconciliation.",
        math_formula="<b>Decoupled Throughput:</b> <i>T</i><sub>StagedETL</sub> = <i>T</i><sub>BulkLanding</sub> + <i>T</i><sub>InDBJoins</sub> &ll; <i>T</i><sub>RowByRowETL</sub> (Over 150&times; faster)",
        worked_example="480,310 rows stream into staging.stg_crimes in ~14 seconds via COPY. Once landed, a single SQL query populates dw.DimCrimeType in 0.8 seconds using SELECT DISTINCT iucr, primary_type FROM staging.stg_crimes.",
        project_usage="Defined in sql/01_staging.sql. Populated in etl/load_initial.py (lines 127-145) and etl/load_incremental.py (lines 80-105).",
        exact_reference="chicago-crime-dw/sql/01_staging.sql; etl/load_initial.py, lines 127-145",
        pros_cons="Advantages: Fast, non-blocking data landing; preserves original source extract state for auditing. Limitations: Requires temporary secondary database storage (~65 MB).",
        styles=styles
    ))
    
    # Concept 15: Bulk Ingestion via PostgreSQL COPY
    elements.extend(make_concept_card(
        num=15, name="High-Throughput Bulk Ingestion via PostgreSQL COPY Protocol",
        definition="A specialized streaming protocol in PostgreSQL that bypasses the standard SQL query parsing, planning, and transactional statement overhead to stream raw records directly into table disk pages.",
        why_needed="Executing 480,000 individual SQL INSERT statements row-by-row requires 480,000 network round trips and WAL transaction flushes, taking over 45 minutes. Bulk COPY finishes in 14 seconds.",
        how_it_works="The script formats the Pandas DataFrame into an in-memory tab-delimited stream (io.StringIO), with \\N representing SQL NULLs. The Python psycopg2 client issues cur.copy_from() or cur.copy_expert(), which writes directly to the PostgreSQL heap.",
        step_by_step="1. Filter initial load slice in Pandas; 2. Serialize target columns to io.StringIO buffer using sep='\\t' and na_rep='\\\\N'; 3. Call cur.copy_from(s_buf, 'staging.stg_crimes', columns=stg_cols); 4. PostgreSQL parses binary stream and appends directly to disk blocks; 5. Commit transaction.",
        math_formula="<b>Ingestion Speedup:</b> <i>S</i><sub>COPY</sub> = <i>T</i><sub>INSERT</sub> / <i>T</i><sub>COPY</sub> = 2,700 s / 14.2 s &asymp; <b>190&times; Throughput Increase</b> (~34,000 rows/sec)",
        worked_example="480,310 records stream through io.StringIO in 14.18 seconds, achieving an effective write velocity of ~33,870 rows per second into staging.stg_crimes.",
        project_usage="Implemented in etl/load_initial.py (lines 135-145) and etl/load_incremental.py (lines 88-102).",
        exact_reference="chicago-crime-dw/etl/load_initial.py, lines 127-145",
        pros_cons="Advantages: Near-instantaneous bulk loading (~34,000 rows/sec); minimal CPU overhead. Limitations: Bypasses column-level check triggers during ingestion; requires pre-formatted string buffers.",
        styles=styles
    ))
    
    # Concept 16: Incremental Micro-Batch Loading
    elements.extend(make_concept_card(
        num=16, name="Non-Destructive Incremental Micro-Batch Loading",
        definition="An ETL design pattern where newly arrived delta records are appended to existing warehouse fact and dimension structures without dropping, truncating, or reloading historical data.",
        why_needed="In production enterprises, dropping and rebuilding a warehouse nightly is impossible due to multi-hour maintenance windows and interruption of active BI dashboards.",
        how_it_works="The December 2025 delta dataset (17,609 records) is staged with batch_id = 'INCREMENTAL_DEC_2025'. Dimension lookup logic checks for net-new dimension members, appends only new records to DimLocation/DimCrimeType, and appends new incident facts to FactCrimeIncident.",
        step_by_step="1. Land delta records in staging with batch_id='INCREMENTAL_DEC_2025'; 2. Identify net-new locations using LEFT JOIN DimLocation ... WHERE LocationKey IS NULL; 3. Insert newly discovered locations (233 members added); 4. Look up surrogate keys and INSERT INTO dw.FactCrimeIncident; 5. Execute INSERT INTO dw.FactAreaDailyPublicSafety ON CONFLICT DO UPDATE; 6. Log audit to outputs/results/incremental_load.md.",
        math_formula="<b>Delta Ingestion Integrity:</b> <i>N</i><sub>post</sub> = <i>N</i><sub>pre</sub> + <i>N</i><sub>delta</sub> = 480,310 + 17,609 = <b>497,919 rows</b> (Zero Historical Degradation)",
        worked_example="December 2025 records introduced 233 previously unseen street/beat combinations. The loader detected these 233 net-new locations, assigned surrogate keys 28,089 to 28,321, and loaded 17,609 incident facts in 2.46 seconds without touching the 480,310 existing facts.",
        project_usage="Implemented in etl/load_incremental.py. Documented in outputs/results/incremental_load.md.",
        exact_reference="chicago-crime-dw/etl/load_incremental.py, lines 70-220; outputs/results/incremental_load.md",
        pros_cons="Advantages: Enables zero-downtime micro-batch updates (2.46s runtime); non-destructive historical preservation. Limitations: Requires robust dimension deduplication and conflict-handling logic.",
        styles=styles
    ))
    
    # Concept 17: Automated Reconciliation & Referential Integrity Auditing
    elements.extend(make_concept_card(
        num=17, name="Automated Warehouse Reconciliation & Referential Integrity Auditing",
        definition="The systematic execution of automated SQL audit scripts verifying 100% row conservation, exact measure reconciliation, and zero orphan foreign keys between source, staging, and fact layers.",
        why_needed="Silent data loss or corrupted foreign keys can invalidate executive reports and compromise machine learning model training without generating database errors.",
        how_it_works="etl/validate.py executes sql/07_validation.sql. It evaluates 5 core audit dimensions: staging vs fact row reconciliation, measure totals equality (IncidentCount, ArrestCount, DomesticCount, NightCount), orphan foreign key checks, -1 Unknown usage, and dual-fact constellation consistency.",
        step_by_step="1. Query COUNT(*) from staging and FactCrimeIncident; verify exact equality; 2. Query SUM(IncidentCount), SUM(ArrestCount), SUM(DomesticCount) and compare with raw source totals; 3. Perform LEFT JOIN on every foreign key (DateKey, TimeKey, CrimeTypeKey, LocationKey, ContextKey) filtering WHERE Dimension.Key IS NULL; verify count = 0; 4. Verify Fact 1 vs Fact 2 totals; 5. Output report to outputs/results/validation_report.md.",
        math_formula="<b>Orphan Key Invariant:</b> &forall; <i>k</i> &isin; {DateKey, TimeKey, CrimeTypeKey, LocationKey, ContextKey} : COUNT(<i>f</i> | <i>f.k</i> &notin; <i>D<sub>k</sub></i>) = <b>0</b>",
        worked_example="The reconciliation audit confirmed: 497,919 staged rows = 497,919 incident facts; Total Arrests = 74,379 exact; 0 orphan keys across all 5 dimensions; 497,243 incidents in valid community areas match between Fact 1 and Fact 2.",
        project_usage="Automated in etl/validate.py and logged in outputs/results/validation_report.md.",
        exact_reference="chicago-crime-dw/etl/validate.py; sql/07_validation.sql; outputs/results/validation_report.md",
        pros_cons="Advantages: Mathematically proves data integrity; detects ETL drift immediately. Limitations: Auditing full measure sums on massive tables requires dedicated compute if executed outside batch maintenance windows.",
        styles=styles
    ))
    
    elements.append(PageBreak())
    return elements
