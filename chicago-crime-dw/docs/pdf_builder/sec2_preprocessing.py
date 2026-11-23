"""
Section 2: Data Preprocessing, Quality Auditing & Feature Engineering.
Implements Concepts 1 through 6 according to the strict 10-point educational format.
"""

from reportlab.platypus import Paragraph, Spacer, PageBreak, KeepTogether, Table, TableStyle
from reportlab.lib import colors
from .config import (
    USABLE_WIDTH, PRIMARY, SECONDARY, ACCENT, DARK_TEXT, LIGHT_BG,
    BORDER_COLOR, make_callout, make_table, make_concept_card, PageTracker
)

def build_section_2(styles, tracker):
    elements = []
    elements.append(PageTracker('sec2', tracker))
    
    elements.append(Paragraph("<b>Section 2: Data Preprocessing, Quality Auditing & Feature Engineering</b>", styles['SectionH1']))
    elements.append(Spacer(1, 4))
    
    elements.append(Paragraph("<b>2.1 Socrata Open Data Extraction Architecture</b>", styles['SectionH2']))
    elements.append(Paragraph(
        "Official Chicago crime incidents are published dynamically on the City of Chicago Open Data Portal via Socrata (Dataset ID: <code>ijzp-q8t2</code>). "
        "Because the API enforces default throttling limits (1,000 rows), extraction is orchestrated via <code>etl/extract.py</code> using "
        "multi-threaded SoQL queries with chunked offsets ($limit=50,000) executed concurrently across 6 worker threads.",
        styles['Body']
    ))
    elements.append(Spacer(1, 6))
    
    extract_table = [
        ["Extraction Parameter", "Operational Configuration & Value", "Engineering Justification"],
        ["Endpoint URL", "https://data.cityofchicago.org/resource/ijzp-q8t2.csv", "Official authoritative City of Chicago Police portal."],
        ["Temporal Boundary", "date >= '2024-01-01T00:00:00' and <= '2025-12-31T23:59:59'", "Captures two complete calendar years of modern incident data."],
        ["Selected Attributes", "21 standard CPD attributes (id, case_number, date, iucr, primary_type, etc.)", "Retains all identifying, temporal, statutory, and spatial fields."],
        ["Concurrency Architecture", "ThreadPoolExecutor(max_workers=6) with 50,000-row batch chunking", "Reduces extraction time from >12 minutes to 86.44 seconds."],
        ["Raw File Output", "data/raw/crimes_2024_2025.csv (103.17 MB, 497,919 records)", "Immutable raw landing dataset preserving full provenance in docs/source_log.md."]
    ]
    elements.append(make_table(extract_table, col_widths=[110, 195, USABLE_WIDTH - 305], headers=True, styles=styles))
    elements.append(Spacer(1, 10))
    
    elements.append(Paragraph("<b>2.2 Data Quality Profiling & Pre-Cleaning Audit Results</b>", styles['SectionH2']))
    elements.append(Paragraph(
        "Prior to applying any transformations, <code>etl/profile_data.py</code> profiled the raw dataset across missing values, "
        "duplicate records, coordinate boundaries, and timestamp consistency (logged to <code>outputs/tables/missing_profile.csv</code>).",
        styles['Body']
    ))
    elements.append(Spacer(1, 4))
    
    dq_table = [
        ["Audited Attribute", "Raw Null Count", "Missing %", "Observed Anomaly / Defect", "Curated Treatment Applied"],
        ["location_description", "2,383", "0.4786%", "Unrecorded crime scene venue.", "Imputed with 'UNKNOWN' (Mapped to DimLocation member)."],
        ["ward", "15", "0.0030%", "Missing municipal legislative ward.", "Imputed with -1 (Standard Unknown Ward member)."],
        ["community_area", "676", "0.1358%", "Unmapped community area tag.", "Imputed with -1 (Standard Unknown Area member)."],
        ["latitude / longitude", "12,987", "2.6083%", "Unprojected / unverified coordinates.", "Preserved with has_valid_coordinates=False; Lat/Lon set to Null."],
        ["case_number", "0 exact dups", "0.0000%", "92,971 rows share case numbers.", "Retained: Case numbers represent multi-charge or multi-victim events."],
        ["Primary Key 'id'", "0 dups", "0.0000%", "All 497,919 rows possess unique id.", "Validated as authoritative primary surrogate/natural key."]
    ]
    elements.append(make_table(dq_table, col_widths=[95, 60, 50, 140, USABLE_WIDTH - 345], headers=True, styles=styles))
    elements.append(Spacer(1, 10))
    
    elements.append(Paragraph("<b>2.3 Core Preprocessing Concepts & Technical Implementation</b>", styles['SectionH2']))
    
    # Concept 1: Zero-Loss Curation Strategy
    elements.extend(make_concept_card(
        num=1, name="Zero-Loss Curation & Selective Imputation Strategy",
        definition="A dimensional warehousing data cleaning policy where zero incident rows are discarded due to missing dimensional attributes, using default surrogate keys (-1 or 'UNKNOWN') to preserve aggregate metric integrity.",
        why_needed="In public safety analytics, deleting records with missing coordinates or wards distorts citywide incident counts, violent crime rates, and temporal trend analyses.",
        how_it_works="The pipeline audits records for missing administrative or geographic tags. Rather than calling df.dropna(), attributes are selectively imputed with standardized sentinel tokens (-1 for integer foreign keys, 'UNKNOWN' for text descriptions) that join cleanly to predefined Unknown dimension records.",
        step_by_step="1. Load raw extract; 2. Count missingness per column; 3. Impute text fields: df['location_description'].fillna('UNKNOWN'); 4. Impute integer foreign keys: df['ward'].fillna(-1).astype(int); 5. Set boolean coordinate validity flag: df['has_valid_coordinates'] = df['latitude'].notnull(); 6. Verify row count reconciliation: len(df_curated) == len(df_raw).",
        math_formula="<b>Row Retention Ratio:</b> <i>R</i><sub>retention</sub> = <i>N</i><sub>curated</sub> / <i>N</i><sub>raw</sub> = 497,919 / 497,919 = <b>1.000 (100.0% Zero-Loss Conservation, &Delta; = 0)</b>",
        worked_example="An incident ID 13324900 has valid timestamp and PrimaryType 'BATTERY', but missing community_area (Null). Instead of dropping the battery incident, community_area is imputed as -1. In OLAP queries, citywide battery volume remains 100% accurate, and area-specific queries route the incident to 'Unknown Area'.",
        project_usage="Implemented in etl/curate.py (lines 80-150). Resulted in 497,919 out of 497,919 records retained in data/curated/crimes_curated.csv.",
        exact_reference="chicago-crime-dw/etl/curate.py, lines 95-125; docs/dq_report.md",
        pros_cons="Advantages: Absolute measure conservation (497,919 incidents, 74,379 arrests exact); zero referential integrity violations. Limitations: Slightly inflates Unknown dimension slice volume (676 records in Community Area -1).",
        styles=styles
    ))
    
    # Concept 2: Temporal Feature Decomposition
    elements.extend(make_concept_card(
        num=2, name="Temporal Feature Decomposition & Cyclical Derivations",
        definition="The algorithmic breakdown of an ISO-8601 timestamp string into multiple discrete dimensional grains (date, time, day of week, time band) and operational flags.",
        why_needed="Raw timestamps cannot be grouped efficiently in relational queries or ingested directly by machine learning algorithms without high-cardinality fragmentation.",
        how_it_works="Using Pandas datetime accessors (dt), the pipeline parses the timestamp once into a datetime64[ns] object, then derives calendar attributes, day-of-week numbers, and non-overlapping operational shift bands.",
        step_by_step="1. Parse timestamp: df['incident_datetime'] = pd.to_datetime(df['date']); 2. Extract calendar parts: year, month, quarter, day; 3. Derive ISO day of week: dayofweek + 1 (1=Monday, 7=Sunday); 4. Assign day name: dt.day_name(); 5. Flag weekends: is_weekend = 1 if day_of_week in (6,7) else 0; 6. Map operational TimeBand: Night (21-05), Morning (05-12), Afternoon (12-17), Evening (17-21); 7. Set binary is_night_incident flag.",
        math_formula="<b>TimeBand(<i>h</i>):</b> 'Night' if <i>h</i> &isin; [21..23, 0..4] else 'Morning' if <i>h</i> &isin; [5..11] else 'Afternoon' if <i>h</i> &isin; [12..16] else 'Evening'",
        worked_example="Incident timestamp '2024-07-04 22:30:00' decomposes into: FullDate='2024-07-04', Year=2024, Month=7, Quarter=3, Day=4, DayOfWeek=4, DayName='Thursday', Hour=22, Minute=30, IsWeekend=0, TimeBand='Night', IsNightIncident=1.",
        project_usage="Applied across all 497,919 records in etl/curate.py (lines 190-215). Powers the 24x7 diurnal heatmap in dashboard/app.py and OLAP drill-down operations.",
        exact_reference="chicago-crime-dw/etl/curate.py, lines 191-211; docs/data_dictionary.md",
        pros_cons="Advantages: Enables instantaneous multi-grain roll-up (Hour -> Day -> Month -> Quarter -> Year) in SQL and Power BI. Limitations: Increases storage footprint from 1 timestamp column to 11 discrete derived columns.",
        styles=styles
    ))
    
    # Concept 3: Domain-Specific Hierarchical Grouping
    elements.extend(make_concept_card(
        num=3, name="Domain-Specific Hierarchical Categorical Binning",
        definition="The deterministic grouping of high-cardinality categorical codes into standardized, semantically meaningful operational classes based on municipal domain knowledge.",
        why_needed="Chicago Police Department records 31 distinct primary crime types and 134 unique premise descriptions. Querying or plotting 134 premises creates severe visual clutter and high model variance.",
        how_it_works="Rule-based classification functions evaluate primary offense codes and keyword patterns within location descriptions to map each record into one of 5 broad crime categories and 6 premise environments.",
        step_by_step="1. Evaluate primary_type: Map Homicide, Battery, Assault, Robbery, Sexual Assault -> 'Violent Crime'; Theft, Burglary, Motor Vehicle Theft, Arson, Damage -> 'Property Crime'; Narcotics, Liquor Law -> 'Substance Offense'; Weapons, Public Peace, Prostitution -> 'Public Order & Weapons'; remainder -> 'Other Offenses'. 2. Evaluate location_description using string pattern matching (e.g. 'STREET|SIDEWALK|ALLEY' -> 'Street & Outdoor'; 'RESIDENCE|APARTMENT' -> 'Residential').",
        math_formula="<b>Hierarchical Mapping:</b> <i>S</i><sub>primary</sub> (31 codes) &rarr; <i>C</i><sub>group</sub> (5 classes); &nbsp; <i>S</i><sub>location</sub> (134 premises) &rarr; <i>L</i><sub>group</sub> (6 classes)",
        worked_example="PrimaryType='MOTOR VEHICLE THEFT' -> CrimeCategoryGroup='Property Crime'. LocationDescription='CTA TRAIN' -> LocationGroup='Transit & Vehicles'.",
        project_usage="Implemented in etl/curate.py (lines 23-78). Formulates the high-level donut charts on Page 1 of the Streamlit dashboard and OLAP slicing operations.",
        exact_reference="chicago-crime-dw/etl/curate.py, lines 23-78; dashboard/app.py, lines 199-209",
        pros_cons="Advantages: Prevents high-cardinality fragmentation; allows executive dashboards to present clear macro distributions. Limitations: Masks granular legal distinctions within offense classes (e.g., petty theft vs grand auto theft).",
        styles=styles
    ))
    
    # Concept 4: Spatial Stratification and Risk Banding
    elements.extend(make_concept_card(
        num=4, name="Spatial Partitioning & Quantile Risk Banding",
        definition="The statistical discretization of continuous spatial coordinates and community area volume distributions into standardized categorical risk tiers using empirical quantiles.",
        why_needed="Raw latitude/longitude floats and raw area numbers (1–77) do not communicate intrinsic public safety risk levels to operational decision-makers.",
        how_it_works="The pipeline computes empirical quartiles (25th, 50th, 75th percentiles) of total two-year crime volume across all 77 community areas to classify each area into risk bands, while partitioning coordinates into geographical quadrants.",
        step_by_step="1. Group total incidents by community_area; 2. Calculate quartile cutoffs Q1, Q2, Q3; 3. Assign CommunityAreaBand: <= Q1 -> 'Low Volume (Q1)', Q1-Q2 -> 'Moderate Volume (Q2)', Q2-Q3 -> 'High Volume (Q3)', > Q3 -> 'Critical Volume (Q4)'; 4. Partition latitude: < 41.78 N -> South, 41.78–41.88 N -> Central, > 41.88 N -> North; 5. Partition longitude: < -87.72 W -> West, -87.72 to -87.64 W -> Central, > -87.64 W -> East / Lakefront.",
        math_formula="<b>Quantile Risk Band:</b> Band(Area<sub><i>i</i></sub>) = Critical (Q4) if Volume &gt; <i>Q</i><sub>0.75</sub>; High (Q3) if Volume &gt; <i>Q</i><sub>0.50</sub>; Moderate (Q2) if Volume &gt; <i>Q</i><sub>0.25</sub>; else Low (Q1)",
        worked_example="Community Area 25 (Austin) recorded 23,736 incidents (> 75th percentile of 7,850). It is assigned to 'Critical Volume (Q4)' and 'West Chicago (< -87.72 W)'.",
        project_usage="Engineered in etl/curate.py (lines 220-285). Stored in data/curated/crimes_curated.csv and populated into dw.DimLocation.",
        exact_reference="chicago-crime-dw/etl/curate.py, lines 244-285; docs/data_dictionary.md",
        pros_cons="Advantages: Supplies immediate socio-spatial stratification for patrol resource prioritization; normalizes area risk. Limitations: Quantile cutoffs reflect sample-period distribution and must be recalibrated across multi-decade studies.",
        styles=styles
    ))
    
    elements.append(PageBreak())
    return elements
