"""
Pages 4 to 5:
- Page 4: End-to-End Batch ETL Lifecycle, Staging Layer, Bulk COPY, Flowchart, Incremental Load, and Reconciliation.
- Page 5: Data Preprocessing, Zero-Loss Curation Policy, Missingness Audit Table, and 3 Feature Engineering Mechanisms.
"""

from reportlab.platypus import Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from .config_18 import (
    USABLE_WIDTH, PRIMARY, SECONDARY, ACCENT, DARK_TEXT, LIGHT_BG, ALT_ROW_BG,
    BORDER_COLOR, MUTED_TEXT, SUCCESS_COLOR, make_callout, make_table, make_image_figure, PageTracker
)

def build_pages_04_05(styles, tracker):
    elements = []
    
    # =========================================================================
    # PAGE 4: ETL PIPELINE LIFECYCLE & INGESTION MECHANICS
    # =========================================================================
    elements.append(PageTracker('sec4_page', tracker))
    elements.append(Paragraph("<b>Section 4: ETL Pipeline and Data Preprocessing</b>", styles['SectionH1']))
    
    elements.append(Paragraph(
        "<b>4.1 End-to-End Batch ETL Lifecycle &amp; High-Throughput Ingestion Mechanics</b><br/>"
        "The project implements a resilient, multi-stage Batch ETL pipeline transitioning raw City of Chicago public data into clean, indexed "
        "dimensional warehouse tables. The pipeline enforces strict data staging, bulk streaming protocols, and post-load reconciliation:",
        styles['Body']
    ))
    elements.append(Spacer(1, 3))
    
    etl_stages = [
        ["Lifecycle Stage", "Script & File Reference", "Key Engineering Operation & Transformation Protocol"],
        ["1. Raw Extraction", "<code>etl/extract.py</code>", "Socrata SoQL REST API extraction; fetches crime records in 50,000-row JSON chunks; lands raw CSV."],
        ["2. Zero-Loss Curation", "<code>etl/curate.py</code>", "Cleanses schema, handles nulls via -1/'UNKNOWN', decomposes dates, derives 11 features; outputs curated CSV."],
        ["3. Transient Staging", "<code>sql/01_staging.sql</code>", "Creates unindexed heap table <code>staging.stg_crimes</code> to decouple external ingestion from dimensional lookups."],
        ["4. Bulk COPY Streaming", "<code>etl/load_initial.py</code>", "Serializes 480,310 rows into an in-memory TSV buffer; streams directly to PostgreSQL via COPY protocol in 14.2s."],
        ["5. Dimensional Loading", "<code>sql/02_dims.sql</code>", "Populates conformed dimensions using set-based SQL; assigns integer surrogate keys and seeds -1 Unknown members."],
        ["6. Fact Ingestion & Audit", "<code>etl/load_initial.py</code>", "Performs hash-join surrogate key lookups to populate atomic and aggregate facts; executes validation audits."]
    ]
    elements.append(make_table(etl_stages, col_widths=[85, 105, USABLE_WIDTH - 190], headers=True, styles=styles, padding=3.8))
    elements.append(Spacer(1, 8))
    
    # Embedded ETL Flowchart Diagram - enlarged for clarity
    elements.extend(make_image_figure(
        'chicago-crime-dw/docs/pdf_assets/etl_pipeline_flow.png',
        "Figure 4.1: Complete Batch ETL Lifecycle from Raw Socrata API Landing to Fact Ingestion & Audit.",
        width=485, height=165, styles=styles
    ))
    elements.append(Spacer(1, 8))
    
    # Bulk COPY vs Insert Comparison & Incremental Loading
    elements.append(Paragraph("<b>4.2 Ingestion Protocols &amp; Non-Destructive Incremental Micro-Batch Loading</b>", styles['SectionH2']))
    elements.append(Spacer(1, 2))
    
    copy_vs_insert = [
        ["Ingestion Method", "Execution Mechanism", "Measured Velocity", "Runtime (480k rows)", "Architectural Verdict"],
        ["Standard SQL INSERT", "Individual row-by-row INSERT statements; 480k network round trips.", "184 rows/sec", "43.5 minutes", "Unacceptable for production ETL."],
        ["PostgreSQL COPY (Used)", "Streams in-memory TSV buffer directly to disk heap, bypassing parser.", "<b>33,870 rows/sec</b>", "<b>14.18 seconds</b>", "<b>190x Speedup (Selected)</b>"]
    ]
    elements.append(make_table(copy_vs_insert, col_widths=[95, 155, 75, 75, USABLE_WIDTH - 400], headers=True, styles=styles, padding=3.8))
    elements.append(Spacer(1, 6))
    
    elements.append(Paragraph(
        "<b>Incremental Micro-Batch Ingestion (December 2025 Delta):</b> In enterprise environments, dropping and recreating warehouses nightly "
        "is infeasible. The project implements a non-destructive incremental loader (<code>etl/load_incremental.py</code>). The December 2025 delta "
        "(17,609 records) is staged with <code>batch_id = 'INCREMENTAL_DEC_2025'</code>. Net-new dimension members (233 previously unseen street/beat "
        "locations) are detected via <code>LEFT JOIN ... WHERE LocationKey IS NULL</code> and appended, followed by incident fact insertion in <b>2.46 seconds</b>, "
        "preserving historical integrity without downtime.",
        styles['Body']
    ))
    
    elements.append(PageBreak())
    
    # =========================================================================
    # PAGE 5: DATA PREPROCESSING & FEATURE ENGINEERING
    # =========================================================================
    elements.append(Paragraph("<b>Section 4 (Continued): Data Preprocessing and Feature Engineering</b>", styles['SectionH1']))
    
    elements.append(Paragraph(
        "<b>4.3 Zero-Loss Data Curation Policy (&Delta; = 0 Rows)</b><br/>"
        "In public safety analytics, deleting records with missing coordinates or wards distorts citywide incident counts, violent crime rates, "
        "and historical trends. The project enforces an absolute <b>Zero-Loss Curation Policy</b>: rather than calling <code>df.dropna()</code>, "
        "attributes are selectively imputed with standardized sentinel tokens (<code>-1</code> for integer foreign keys, <code>'UNKNOWN'</code> for text), "
        "guaranteeing that <b>100% of raw records (497,919 / 497,919)</b> are retained across the warehouse lifecycle.",
        styles['Body']
    ))
    elements.append(Spacer(1, 4))
    
    # Pre-Cleaning Missingness Audit Table
    elements.append(Paragraph("<b>Pre-Cleaning Raw Data Missingness Audit (City of Chicago Crime Extract)</b>", styles['SectionH3']))
    elements.append(Spacer(1, 2))
    missing_data = [
        ["Raw Source Field", "Raw Missing Count", "Missing %", "Data Cleaning Strategy", "Post-Cleaning Resolution in Warehouse"],
        ["community_area", "676", "0.14%", "Impute with -1 sentinel integer", "Maps cleanly to DimLocation(LocationKey = -1, 'Unknown Area')."],
        ["location_description", "6,183", "1.24%", "Impute with 'UNKNOWN' text", "Categorized as LocationGroup = 'Other / Unknown Premises'."],
        ["ward", "30", "0.01%", "Impute with -1 sentinel integer", "Ward surrogate key set to -1; prevents referential key failure."],
        ["latitude / longitude", "6,676", "1.34%", "Set has_valid_coordinates = 0", "Retained in non-spatial facts; omitted from scatter map layers."],
        ["district / beat", "17", "0.003%", "Impute with 'Unknown' string", "Assigned to generic unassigned administrative patrol boundary."]
    ]
    elements.append(make_table(missing_data, col_widths=[90, 65, 45, 115, USABLE_WIDTH - 315], headers=True, styles=styles, padding=4.0))
    elements.append(Spacer(1, 8))
    
    # Three Feature Engineering Mechanisms
    elements.append(Paragraph("<b>4.4 Three Core Feature Engineering Mechanisms Implemented in <code>etl/curate.py</code></b>", styles['SectionH2']))
    elements.append(Spacer(1, 2))
    
    elements.append(Paragraph(
        "<b>1. Temporal Feature Decomposition:</b> Raw ISO-8601 timestamps (<code>date</code>) cannot be grouped efficiently in relational queries "
        "without high-cardinality truncation. The curation pipeline parses timestamps into discrete dimensional attributes: calendar components "
        "(<code>year, month, quarter, day</code>), ISO day-of-week numbering (1=Monday to 7=Sunday), <code>day_name</code>, weekend status (<code>is_weekend</code>), "
        "and 4 non-overlapping operational shift bands: <b>Night</b> (21:00–04:59), <b>Morning</b> (05:00–11:59), <b>Afternoon</b> (12:00–16:59), and <b>Evening</b> (17:00–20:59). "
        "This enables instant multi-level roll-up and powers the 24x7 diurnal heatmaps.",
        styles['Body']
    ))
    elements.append(Spacer(1, 3))
    
    elements.append(Paragraph(
        "<b>2. Domain-Specific Hierarchical Categorical Binning:</b> The Chicago Police Department records 31 distinct primary crime types and 134 premises. "
        "Querying 134 premises directly causes high visual noise and sparse model matrices. The pipeline deterministically maps these into standardized high-level groups:<br/>"
        "&bull; <i>CrimeCategoryGroup (5 Classes):</i> Violent Crime (Homicide, Battery, Assault, Robbery), Property Crime (Theft, Burglary, Auto Theft), "
        "Substance Offense (Narcotics, Liquor), Public Order &amp; Weapons (Weapons Violations, Public Peace), and Other Offenses.<br/>"
        "&bull; <i>LocationGroup (6 Groups):</i> Street &amp; Outdoor, Residential, Commercial &amp; Retail, Transit &amp; CTA Vehicles, Public / Government, Other.",
        styles['Body']
    ))
    elements.append(Spacer(1, 3))
    
    elements.append(Paragraph(
        "<b>3. Spatial Stratification &amp; Quantile Risk Banding:</b> To transform continuous coordinate floats into actionable risk tiers, the pipeline "
        "computes empirical quartiles ($Q_1, Q_2, Q_3$) of two-year crime volume across all 77 community areas: <b>Critical (Q4)</b> (&gt;7,850 incidents), "
        "<b>High (Q3)</b>, <b>Moderate (Q2)</b>, and <b>Low (Q1)</b> (&le;2,100 incidents). Coordinates are simultaneously partitioned into geographic quadrants "
        "(North, Central, South, and West Chicago), enabling stratified spatial sampling for patrol resource allocation.",
        styles['Body']
    ))
    elements.append(Spacer(1, 8))
    
    elements.append(make_callout(
        "Quality Verification & Data Lineage Invariant",
        "The automated reconciliation audit (<code>etl/validate.py</code>) mathematically proves that <b>exact row conservation</b> is maintained: "
        "<code>len(df_raw) = len(df_curated) = len(stg_crimes) = len(FactCrimeIncident) = 497,919</code>. Furthermore, all 74,379 arrests and 87,624 domestic "
        "incidents match the raw source with zero deviation, confirming 100% data fidelity.",
        styles, accent_color=SUCCESS_COLOR, padding_v=6.0
    ))
    
    elements.append(PageBreak())
    return elements
