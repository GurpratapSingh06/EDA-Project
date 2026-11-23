"""
Section 3: Dimensional Modeling & Fact Constellation Schema Design.
Implements Concepts 5 through 13 according to the strict 10-point educational format,
incorporates the physical ERD diagram, and details the schema comparison matrix.
"""

from reportlab.platypus import Paragraph, Spacer, PageBreak, KeepTogether, Table, TableStyle
from reportlab.lib import colors
from .config import (
    USABLE_WIDTH, PRIMARY, SECONDARY, ACCENT, DARK_TEXT, LIGHT_BG,
    BORDER_COLOR, make_callout, make_table, make_image_figure, make_concept_card, PageTracker
)

def build_section_3(styles, tracker):
    elements = []
    elements.append(PageTracker('sec3', tracker))
    
    elements.append(Paragraph("<b>Section 3: Dimensional Modeling & Fact Constellation Schema Design</b>", styles['SectionH1']))
    elements.append(Spacer(1, 4))
    
    elements.append(Paragraph("<b>3.1 Paradigm Selection: Star vs. Snowflake vs. Fact Constellation</b>", styles['SectionH2']))
    elements.append(Paragraph(
        "Dimensional modeling structures data for high-speed analytical reads, slice-and-dice queries, and reporting. "
        "The project conducted a formal evaluation in <code>docs/schema_comparison.md</code> comparing pure Star, Snowflake, and "
        "Fact Constellation schemas before physically implementing the <b>Fact Constellation Schema</b> in PostgreSQL 16.",
        styles['Body']
    ))
    elements.append(Spacer(1, 4))
    
    schema_comp = [
        ["Evaluation Dimension", "Pure Star Schema", "Normalized Snowflake Schema", "Fact Constellation Schema (Implemented)"],
        ["Fact Table Architecture", "Single Fact Table:\nOnly atomic FactCrimeIncident.", "Single Fact Table:\nOnly atomic FactCrimeIncident.", "Dual Fact Tables (Constellation):\nFactCrimeIncident (atomic) + FactAreaDailyPublicSafety (aggregate)."],
        ["Dimension Structure", "Denormalized dimensions;\nsingle-hop joins to fact.", "Normalized dimensions (e.g. Ward -> District -> City).", "Conformed dimensions shared seamlessly across both atomic and aggregate facts."],
        ["Join Complexity", "Low: Simple 1-hop star joins to all dimensions.", "High: Multi-hop cascading joins (Fact -> Beat -> District -> Area).", "Optimal: Star joins on atomic queries; 1-hop join on aggregate area-day queries."],
        ["Aggregate Query Latency", "High latency: ~280 ms\nRequires scanning 500k rows.", "Very high latency: >350 ms\nScans 500k rows + multi-hop joins.", "Ultra-low latency: ~4.2 ms (70x speedup!)\nDirectly queries pre-computed Area-Daily Fact."],
        ["Storage Overhead", "Moderate (~170 MB).", "Minimal (~145 MB), but join cost is prohibitive.", "Slightly higher (~185 MB due to aggregate fact table), easily justified by 70x query acceleration."],
        ["Suitability for Project", "Adequate for incident reporting, but slow for ML demand forecasting.", "Poor: Excessive join overhead without analytical benefit.", "Superior: Powers both incident-level BI drill-downs and sub-second ML regression training."]
    ]
    elements.append(make_table(schema_comp, col_widths=[90, 140, 140, 145], headers=True, styles=styles))
    elements.append(Spacer(1, 10))
    
    elements.append(Paragraph("<b>3.2 Physical Database ER Diagram (Constellation Schema)</b>", styles['SectionH2']))
    elements.extend(make_image_figure('chicago-crime-dw/docs/erd/constellation_schema_erd.png',
                                      "Figure 3.1: Physical Fact Constellation Schema implemented in PostgreSQL 16 showing dual fact tables and conformed dimensions.",
                                      width=485, styles=styles))
    elements.append(Spacer(1, 8))
    
    elements.append(Paragraph("<b>3.3 Core Dimensional Modeling Concepts & Technical Implementation</b>", styles['SectionH2']))
    
    # Concept 5: Fact Constellation Schema
    elements.extend(make_concept_card(
        num=5, name="Fact Constellation (Dual-Grain Multi-Fact Schema)",
        definition="A dimensional warehouse architecture containing multiple fact tables sharing conformed dimensions, allowing analytics at multiple distinct grains of aggregation without scanning atomic transaction tables.",
        why_needed="Atomic incident tables contain nearly 500,000 rows. Aggregating incident counts by community area and date for machine learning training or spatial heatmaps repeatedly scanned millions of records, bottlenecking performance.",
        how_it_works="The schema defines two fact tables: dw.FactCrimeIncident at transaction grain (1 row per crime incident) and dw.FactAreaDailyPublicSafety at periodic snapshot grain (Community Area x Date). Both facts reference the conformed dimension dw.DimDate.",
        step_by_step="1. Design conformed dimensions (DimDate, DimTime, DimCrimeType, DimLocation); 2. Implement atomic fact dw.FactCrimeIncident; 3. Implement aggregate fact dw.FactAreaDailyPublicSafety with unique constraint (DateKey, CommunityArea); 4. Populate atomic fact via ETL bulk COPY; 5. Populate aggregate fact via SQL GROUP BY DateKey, CommunityArea in initial and incremental ETL.",
        math_formula="<b>Speedup Factor:</b> <i>S</i> = <i>T</i><sub>atomic</sub> / <i>T</i><sub>constellation</sub> = 289.49 ms / 4.20 ms &asymp; <b>68.9&times; Latency Reduction (98.5% faster)</b>",
        worked_example="A machine learning query predicting daily crime in Community Area 25 queries dw.FactAreaDailyPublicSafety directly for 730 daily rows instead of scanning 497,919 individual incident records in dw.FactCrimeIncident, returning results in 4.2 ms instead of 280 ms.",
        project_usage="Defined in sql/03_facts.sql and populated in etl/load_initial.py (lines 261-290). Powers Notebook 04 (Regression) and the District analytics tab in dashboard/app.py.",
        exact_reference="chicago-crime-dw/sql/03_facts.sql, lines 31-52; etl/load_initial.py, lines 261-290",
        pros_cons="Advantages: Sub-5ms query latency for area-level analytics; 70x acceleration for machine learning feature extraction. Limitations: Requires dual-fact maintenance during ETL incremental loads.",
        styles=styles
    ))
    
    # Concept 6: Transaction Fact vs Periodic Snapshot Fact
    elements.extend(make_concept_card(
        num=6, name="Transaction Fact Table vs. Periodic Snapshot Fact Table",
        definition="A transaction fact table records an event at a single instantaneous point in time (atomic grain). A periodic snapshot fact table records summary status or performance metrics over a regular predefined time interval (periodic grain).",
        why_needed="Public safety requires both granular event tracking (e.g. investigating specific case numbers or midnight offenses) and regular macro-level operational tracking (e.g. daily patrol demand across 77 community areas).",
        how_it_works="FactCrimeIncident stores exactly one row per reported crime event, containing additive counts (IncidentCount=1, ArrestCount=0/1). FactAreaDailyPublicSafety summarizes these events at end-of-day per community area, calculating derived rates.",
        step_by_step="1. Incident occurs: FactCrimeIncident records IncidentKey, DateKey, TimeKey, CrimeTypeKey, LocationKey, ContextKey, IncidentCount=1, ArrestCount=1; 2. Daily summary: FactAreaDailyPublicSafety aggregates DateKey, CommunityArea, TotalIncidentCount=SUM(IncidentCount), TotalArrestCount=SUM(ArrestCount), ArrestRate=ROUND((TotalArrest/TotalIncident)*100, 2).",
        math_formula="<b>Dual Grain Definition:</b> Grain(Fact 1) = 1 row per CPD Incident Event; Grain(Fact 2) = 1 row per (Community Area <i>i</i>, Date <i>d</i>)",
        worked_example="On 2024-01-01 in Austin (Area 25), 34 separate incidents are recorded in FactCrimeIncident. FactAreaDailyPublicSafety stores exactly one row for DateKey=20240101, CommunityArea=25 with TotalIncidentCount=34.",
        project_usage="Defined in sql/03_facts.sql. dw.FactCrimeIncident holds 497,919 rows; dw.FactAreaDailyPublicSafety holds 53,935 area-daily snapshots.",
        exact_reference="chicago-crime-dw/sql/03_facts.sql, lines 8-52; outputs/results/validation_report.md",
        pros_cons="Advantages: Clean separation between transactional auditing and executive trend tracking. Limitations: Periodic snapshot requires reconciliation audits against atomic facts to prevent drift.",
        styles=styles
    ))
    
    # Concept 7: Conformed Dimensions
    elements.extend(make_concept_card(
        num=7, name="Conformed Dimensions & Shared Analytical Bus",
        definition="Dimension tables that have consistent data meanings, attribute definitions, and surrogate keys across multiple fact tables within a data warehouse.",
        why_needed="Without conformed dimensions, different business units or fact tables develop inconsistent definitions (e.g. conflicting date calendars or district boundaries), causing reporting discrepancies.",
        how_it_works="Dimensions are populated once and referenced by both FactCrimeIncident and FactAreaDailyPublicSafety. DimDate uses a standardized integer surrogate key YYYYMMDD (e.g. 20240101) representing calendar attributes identically across all queries.",
        step_by_step="1. Populate dw.DimDate for 2024–2025 (731 days); 2. Enforce foreign-key constraints on FactCrimeIncident.DateKey REFERENCES DimDate(DateKey); 3. Enforce foreign-key constraints on FactAreaDailyPublicSafety.DateKey REFERENCES DimDate(DateKey); 4. Query across both facts using identical Year, Month, Quarter attributes.",
        math_formula="<b>Conformed Dimension Rule:</b> DateKey(Fact<sub>1</sub>) &isin; dom(DimDate.DateKey) &amp; DateKey(Fact<sub>2</sub>) &isin; dom(DimDate.DateKey)",
        worked_example="A quarterly roll-up query joins both FactCrimeIncident and FactAreaDailyPublicSafety to DimDate using d.Quarter = 3 and d.Year = 2024, guaranteeing identical temporal boundaries.",
        project_usage="Implemented across dw.DimDate, dw.DimTime, dw.DimCrimeType, and dw.DimLocation in sql/02_dims.sql.",
        exact_reference="chicago-crime-dw/sql/02_dims.sql, lines 7-125; etl/load_initial.py, lines 43-100",
        pros_cons="Advantages: Guarantees 100% consistent reporting; enables drill-across queries between multiple facts. Limitations: Schema changes in a conformed dimension impact all referencing fact tables.",
        styles=styles
    ))
    
    # Concept 8: Surrogate Keys vs Natural Keys
    elements.extend(make_concept_card(
        num=8, name="Surrogate Keys vs. Natural Keys",
        definition="A surrogate key is an artificial, system-assigned integer primary key with no intrinsic business meaning, used to join facts and dimensions independently of external source system identifiers (natural keys).",
        why_needed="Source natural keys (like CPD IUCR codes or Case Numbers) can change format, contain alphanumeric characters, or re-occur across years, degrading join performance and breaking referential integrity.",
        how_it_works="Dimensions utilize integer surrogate keys (e.g. DimCrimeType.CrimeTypeKey, DimLocation.LocationKey generated via ROW_NUMBER() or IDENTITY). The Fact table stores compact 4-byte or 8-byte integers rather than 20-character strings.",
        step_by_step="1. Staging lands natural keys (iucr, primary_type, description, fbi_code); 2. During dimension load, assign distinct integer CrimeTypeKey; 3. During fact load, join staging natural keys against dimension natural keys to lookup the corresponding CrimeTypeKey; 4. Insert CrimeTypeKey into Fact table.",
        math_formula="<b>Storage Optimization:</b> sizeof(INT4 Surrogate Key) = 4 bytes vs sizeof(VARCHAR(40) Natural Key) &asymp; 41 bytes (<b>10&times; Join Memory Reduction</b>)",
        worked_example="Natural key combination ('0460', 'BATTERY', 'SIMPLE', '08B') is assigned surrogate key CrimeTypeKey = 42. FactCrimeIncident stores '42', enabling high-speed integer CPU comparison during joins.",
        project_usage="Implemented in sql/02_dims.sql across all dimensions and resolved in etl/load_initial.py (lines 242-254).",
        exact_reference="chicago-crime-dw/sql/02_dims.sql; etl/load_initial.py, lines 150-205",
        pros_cons="Advantages: Protects warehouse from source schema volatility; compact integer indexing; allows -1 Unknown rows. Limitations: Requires ETL lookup step during data ingestion.",
        styles=styles
    ))
    
    # Concept 9: Degenerate Dimensions
    elements.extend(make_concept_card(
        num=9, name="Degenerate Dimensions",
        definition="A dimension key or operational reference number that is stored directly in the fact table without joining to a separate dimension table, because it has no additional descriptive attributes.",
        why_needed="Creating separate dimension tables for high-cardinality transaction identifiers (like incident IDs or police case numbers) with 1:1 fact relationships wastes storage and causes unnecessary join overhead.",
        how_it_works="The operational natural identifiers IncidentID (BIGINT) and CaseNumber (VARCHAR(20)) are retained directly in dw.FactCrimeIncident. They serve as audit handles back to the source system without inflating dimensional tables.",
        step_by_step="1. Staging receives CPD 'id' and 'case_number'; 2. Define FactCrimeIncident with IncidentID BIGINT and CaseNumber VARCHAR(20); 3. Insert directly during fact bulk load; 4. Use in operational drill-through queries to inspect individual police reports.",
        math_formula="Cardinality Relationship: |DegenerateDimension| = |FactTable| = 497,919 (1:1 Bijection with Fact Grain)",
        worked_example="In FactCrimeIncident, CaseNumber = 'JH100028' and IncidentID = 13324861 reside directly in the fact row. A detective queries CaseNumber = 'JH100028' to pull all dimensional details in a single select without extra joins.",
        project_usage="Defined in sql/03_facts.sql (lines 19-20). Validated in reconciliation audits in etl/validate.py.",
        exact_reference="chicago-crime-dw/sql/03_facts.sql, lines 19-20; docs/data_dictionary.md",
        pros_cons="Advantages: Eliminates an unnecessary 500,000-row dimension table; provides immediate traceability to CPD records. Limitations: Cannot attach descriptive attributes without converting to a standard dimension.",
        styles=styles
    ))
    
    # Concept 10: Junk Dimension
    elements.extend(make_concept_card(
        num=10, name="Junk Dimension (Context Flag Compression)",
        definition="A single consolidated dimension table that combines multiple low-cardinality flags, boolean indicators, and contextual attributes, eliminating separate dimension tables or clutter in the fact table.",
        why_needed="Incidents contain three binary operational flags: Arrest (True/False), Domestic (True/False), and Night (True/False). Storing them as three separate foreign keys requires 3 dimension tables; storing them as strings in the fact table bloats storage.",
        how_it_works="dw.DimIncidentContext enumerates all 2^3 = 8 possible combinations of (ArrestFlag, DomesticFlag, NightFlag) with descriptive labels. The fact table references a single ContextKey (1 to 8).",
        step_by_step="1. Generate Cartesian product of {0,1} x {0,1} x {0,1} -> 8 rows; 2. Assign ContextKey 1 to 8 with ContextDescription (e.g. 'Arrest Made | Non-Domestic | Night Incident'); 3. Add -1 Unknown member; 4. Fact table stores single ContextKey.",
        math_formula="<b>Combinatorial Space:</b> |DimIncidentContext| = 2<sup><i>N</i><sub>flags</sub></sup> = 2<sup>3</sup> = 8 rows (+ 1 Unknown member = 9 rows total)",
        worked_example="An incident occurring at 23:30 with Arrest=True and Domestic=False maps to ContextKey = 5 ('Arrest Made | Non-Domestic | Night Incident').",
        project_usage="Defined in sql/02_dims.sql (lines 100-125). Joined in mart view sql/06_mart_view.sql.",
        exact_reference="chicago-crime-dw/sql/02_dims.sql, lines 100-125; sql/03_facts.sql, line 17",
        pros_cons="Advantages: Consolidates 3 foreign keys into 1; produces rich human-readable narrative labels for Power BI slicers. Limitations: Expanding flags exponentially increases row count (2^N).",
        styles=styles
    ))
    
    # Concept 11: Unknown Member (-1) Pattern
    elements.extend(make_concept_card(
        num=11, name="Standardized Unknown Member (-1) Pattern",
        definition="The pre-population of a dummy record with surrogate key -1 in every dimension table, representing missing, unrecorded, or inapplicable source data.",
        why_needed="Relational database foreign keys enforce referential integrity. If an incident has a missing ward or community area, a standard foreign key insert fails or requires a NULL foreign key, which causes outer joins to drop facts in inner-join queries.",
        how_it_works="Every dimension table inserts a row with PrimaryKey = -1 and attributes set to 'Unknown' during schema initialization. Any record with missing dimensional data points to -1, enabling standard INNER JOINs without losing records.",
        step_by_step="1. In 02_dims.sql, execute: INSERT INTO dw.DimLocation (LocationKey, District, Beat, Ward, CommunityArea) VALUES (-1, 'Unknown', 'Unknown', -1, -1); 2. In curate.py, map missing community areas: df['community_area'].fillna(-1); 3. Fact load matches missing areas to LocationKey=-1; 4. Reconcile in 07_validation.sql.",
        math_formula="<b>Referential Completeness:</b> &forall; <i>f</i> &isin; FactTable : <i>f</i>.ForeignKey &isin; dom(DimensionTable.PrimaryKey) &and; <i>f</i>.ForeignKey &ne; NULL",
        worked_example="676 incidents lack a recorded community area in source data. They are loaded with LocationKey pointing to DimLocation (-1). When filtering by CommunityArea = -1, all 676 incidents are cleanly retrieved.",
        project_usage="Implemented across all dimensions in sql/02_dims.sql and audited in outputs/results/validation_report.md (0 NULL FKs, 100% integrity).",
        exact_reference="chicago-crime-dw/sql/02_dims.sql, lines 25-29, 43-46, 63-67, 94-98; outputs/results/validation_report.md",
        pros_cons="Advantages: Eliminates NULL foreign keys; prevents outer-join performance penalties; enables explicit auditing of missing source data. Limitations: Requires disciplined ETL surrogate key lookup logic.",
        styles=styles
    ))
    
    # Concept 12: Certified Analytical Mart View
    elements.extend(make_concept_card(
        num=12, name="Certified Analytical Data Mart SQL View",
        definition="A certified, central SQL view that joins normalized facts and conformed dimensions into a unified, flattened analytical schema serving as the authoritative contract for BI tools and machine learning models.",
        why_needed="Exposing raw fact and dimension tables directly to end-users, BI analysts, and data scientists leads to fragmented join logic, duplicated SQL filters, and accidental Cartesian products.",
        how_it_works="mart.PublicSafetyAnalyticsMart executes a certified star-join across dw.FactCrimeIncident, DimDate, DimTime, DimCrimeType, DimLocation, and DimIncidentContext, exposing clean, lowercase column names and business-ready metrics.",
        step_by_step="1. Write CREATE VIEW mart.PublicSafetyAnalyticsMart AS SELECT ...; 2. Pre-join conformed dimensions on their primary surrogate keys; 3. Expose degenerate IDs, calendar attributes, geographic tags, and additive measure flags; 4. Direct Streamlit, Power BI, and Scikit-Learn pipelines to query this view exclusively.",
        math_formula="<b>View Interface Contract:</b> <i>V</i><sub>mart</sub> = FactCrimeIncident [JOIN] DimDate [JOIN] DimTime [JOIN] DimCrimeType [JOIN] DimLocation [JOIN] DimIncidentContext",
        worked_example="In dashboard/app.py and etl/run_ml_models.py, models execute: SELECT * FROM mart.PublicSafetyAnalyticsMart WHERE Year = 2024, abstracting all underlying surrogate key joins.",
        project_usage="Defined in sql/06_mart_view.sql. Consumed by dashboard/app.py, etl/run_ml_models.py, and Power BI semantic models.",
        exact_reference="chicago-crime-dw/sql/06_mart_view.sql, lines 7-50",
        pros_cons="Advantages: Single source of analytical truth; isolates downstream consumers from physical warehouse schema changes. Limitations: Complex views can be computationally expensive if underlying dimensional indexes are missing.",
        styles=styles
    ))
    
    # Concept 13: B-Tree Indexing Strategy
    elements.extend(make_concept_card(
        num=13, name="Secondary B-Tree Analytical Indexing Strategy",
        definition="The deliberate creation of balanced tree (B-Tree) index structures on foreign keys, temporal coordinates, and high-frequency analytical predicates to optimize multi-table star joins and selective range scans.",
        why_needed="Scanning an unindexed 500,000-row fact table for selective queries (e.g. violent crimes in July) triggers sequential table scans that saturate disk I/O and degrade dashboard responsiveness.",
        how_it_works="PostgreSQL builds balanced hierarchical tree structures storing sorted key values and physical row pointers (TIDs). Queries with selective predicates switch from Sequential Scans to high-speed Index Scans or Bitmap Index Scans.",
        step_by_step="1. Index all foreign keys in FactCrimeIncident (DateKey, TimeKey, CrimeTypeKey, LocationKey, ContextKey); 2. Create composite indexes for frequent multi-attribute slices: (DateKey, CrimeTypeKey) and (DateKey, LocationKey); 3. Index high-cardinality dimension filters: DimDate(Year, Month), DimLocation(District), DimCrimeType(PrimaryType); 4. Profile execution times pre- and post-index using EXPLAIN (ANALYZE, TIMING).",
        math_formula="Search Complexity: T<sub>B-Tree</sub> = O(log<sub>B</sub> N) vs Sequential Scan T<sub>Seq</sub> = O(N) (where B &asymp; 100&ndash;500 keys per page)",
        worked_example="Query 4 (filtering Violent Crime in top community areas) dropped from 289.05 ms to 248.24 ms, while selective composite index slices achieved up to 6.3x latency reduction.",
        project_usage="Defined in sql/04_indexes.sql (17 indexes built in 5.05 s) and benchmarked in etl/benchmark_indexes.py (outputs/results/indexing_report.md).",
        exact_reference="chicago-crime-dw/sql/04_indexes.sql; etl/benchmark_indexes.py; outputs/results/query_timings.csv",
        pros_cons="Advantages: Dramatic read acceleration for interactive dashboards; negligible build time (<5.1s). Limitations: Consumes secondary disk storage (~35 MB); incurs minor insert overhead during batch loading.",
        styles=styles
    ))
    
    elements.append(PageBreak())
    return elements
