"""
Section 5: Multidimensional OLAP Operations & Business Analysis.
Implements Concepts 18 through 25, details the 6 core OLAP cube operations,
and provides full SQL queries and analytical answers for all 10 Mandatory Business Questions.
"""

from reportlab.platypus import Paragraph, Spacer, PageBreak, KeepTogether, Table, TableStyle
from reportlab.lib import colors
from .config import (
    USABLE_WIDTH, PRIMARY, SECONDARY, ACCENT, DARK_TEXT, LIGHT_BG,
    BORDER_COLOR, make_callout, make_table, make_image_figure, make_code_box,
    make_concept_card, PageTracker
)

def build_section_5(styles, tracker):
    elements = []
    elements.append(PageTracker('sec5', tracker))
    
    elements.append(Paragraph("<b>Section 5: Multidimensional OLAP Operations & Business Analysis</b>", styles['SectionH1']))
    elements.append(Spacer(1, 4))
    
    elements.append(Paragraph("<b>5.1 Conceptual OLAP Hypercube vs. Physical ROLAP Implementation</b>", styles['SectionH2']))
    elements.append(Paragraph(
        "A central theoretical concept in business intelligence is the distinction between a <b>conceptual OLAP cube</b> and "
        "its <b>physical relational implementation (ROLAP)</b>. Conceptually, crime incidents exist in an N-dimensional hypercube "
        "spanned by continuous temporal, spatial, and statutory axes. Physically, PostgreSQL 16 does not maintain pre-computed "
        "multidimensional arrays (MOLAP); rather, it executes Relational OLAP (ROLAP) leveraging the dual-grain Fact Constellation schema, "
        "B-Tree indexes, and advanced ANSI SQL aggregation operators (<code>ROLLUP</code>, <code>CUBE</code>, <code>GROUPING SETS</code>, <code>FILTER</code>).",
        styles['Body']
    ))
    elements.append(Spacer(1, 6))
    
    # Conceptual Cube Diagram
    elements.extend(make_image_figure('chicago-crime-dw/docs/pdf_assets/olap_cube_concept.png',
                                      "Figure 5.1: Conceptual Multidimensional OLAP Hypercube displaying Time, Location, and Crime Category dimensions with a highlighted Dice sub-cube.",
                                      width=420, styles=styles))
    elements.append(Spacer(1, 8))
    
    elements.append(Paragraph("<b>5.2 The Six Formal OLAP Operations in SQL</b>", styles['SectionH2']))
    elements.append(Paragraph(
        "The project physically implements and benchmarks all six canonical OLAP cube operations in <code>sql/05_olap_queries.sql</code> "
        "and <code>etl/run_olap_and_dashboard.py</code>. Below is the technical breakdown of each operation:",
        styles['Body']
    ))
    elements.append(Spacer(1, 4))
    
    olap_summary = [
        ["OLAP Operation", "Dimensional Mechanics", "Project Implementation Example", "SQL Syntax Primitive"],
        ["1. Roll-Up", "Aggregates data by climbing up a dimensional hierarchy (e.g. Month -> Quarter -> Year -> Grand Total).", "Computes annual and quarterly crime totals and clearance rates.", "GROUP BY ROLLUP (d.Year, d.Quarter, d.Month)"],
        ["2. Drill-Down", "Navigates from higher-level summary to lower-level detailed grain (e.g. Month -> Day -> Hour).", "Drills into the July 4th peak summer window down to the exact hour.", "WHERE d.Year = 2024 AND d.Month = 7 AND d.Day IN (4, 5) GROUP BY d.Month, d.Day, t.Hour"],
        ["3. Slice", "Filters the cube on a single dimensional predicate, producing a 2D rectangular sub-cube.", "Isolates District 011 (Harrison) to examine offense breakdown.", "WHERE l.District = '011' GROUP BY c.CrimeCategoryGroup, c.PrimaryType"],
        ["4. Dice", "Filters the cube across two or more dimensions simultaneously, isolating a targeted sub-cube.", "Extracts high-violence districts (007, 011, 015) during Night/Evening hours for Violent/Property crimes.", "WHERE l.District IN ('007','011','015') AND t.TimeBand IN ('Night','Evening') AND c.CrimeCategoryGroup IN ('Violent Crime','Property Crime')"],
        ["5. Pivot (Rotate)", "Rotates the dimensional axes to present data as a 2D cross-tabular matrix.", "Creates a 24x7 matrix: Hour of Day (0–23) across columns x Day of Week across rows.", "GROUP BY t.Hour with COUNT(f.IncidentKey) FILTER (WHERE d.DayOfWeek = i)"],
        ["6. CUBE / GROUPING SETS", "Computes simultaneous multi-grain aggregations and subtotals across all combinations of dimensions.", "Generates 3D subtotals across Year, District, and Crime Category simultaneously.", "GROUP BY GROUPING SETS ((d.Year, l.District, c.CrimeCategoryGroup), (d.Year, l.District), (d.Year), ())"]
    ]
    elements.append(make_table(olap_summary, col_widths=[85, 120, 155, USABLE_WIDTH - 360], headers=True, styles=styles))
    elements.append(Spacer(1, 10))
    
    # Concept 18: Roll-Up
    elements.extend(make_concept_card(
        num=18, name="OLAP Roll-Up Operation",
        definition="An OLAP operation that aggregates detailed facts by climbing up an ordered dimensional hierarchy, diminishing the level of detail while computing hierarchical subtotals.",
        why_needed="Executive leadership requires high-level quarterly and annual performance overviews without inspecting hundreds of thousands of individual daily entries.",
        how_it_works="The query groups by the dimensional hierarchy using PostgreSQL's ROLLUP extension. The database computes aggregates at (Year, Quarter, Month), then rolls up to (Year, Quarter), then (Year), and finally produces a single grand total row where higher grains are NULL.",
        step_by_step="1. Select d.Year, d.Quarter, d.Month, COUNT(f.IncidentKey), SUM(f.ArrestCount); 2. Join FactCrimeIncident to DimDate; 3. Group by ROLLUP (d.Year, d.Quarter, d.Month); 4. Sort results using ORDER BY d.Year NULLS LAST, d.Quarter NULLS LAST, d.Month NULLS LAST.",
        math_formula="<b>Hierarchical Aggregation:</b> <i>A</i>(Year) = &Sigma;<sub><i>q</i> &isin; Year</sub> <i>A</i>(<i>q</i>) = &Sigma;<sub><i>m</i> &isin; Year</sub> <i>A</i>(<i>m</i>) = &Sigma;<sub><i>d</i> &isin; Year</sub> Facts(<i>d</i>)",
        worked_example="In 2024, Month 1 (January) recorded 19,412 incidents; Month 2 recorded 17,211; Month 3 recorded 20,442. The ROLLUP operator automatically computes the Q1 subtotal (57,065 incidents) and rolls up to the 2024 annual total (251,467 incidents).",
        project_usage="Implemented in sql/05_olap_queries.sql (lines 8-18) and etl/run_olap_and_dashboard.py (lines 50-65).",
        exact_reference="chicago-crime-dw/sql/05_olap_queries.sql, lines 8-18",
        pros_cons="Advantages: Replaces multiple UNION ALL queries with a single, highly optimized scan. Limitations: Results contain mixed grains requiring careful NULL-handling in downstream visualization code.",
        styles=styles
    ))
    
    # Concept 19: OLAP Drill-Down
    elements.extend(make_concept_card(
        num=19, name="OLAP Drill-Down Operation",
        definition="The inverse of roll-up: navigating from summary-level data down to more granular levels of a dimensional hierarchy to reveal finer operational details.",
        why_needed="When an analyst observes an abnormal aggregate spike (e.g. violent crime surge in July), drill-down reveals the exact peak days, hours, and tactical patrol beats responsible.",
        how_it_works="The query adds lower-level hierarchy attributes to the SELECT and GROUP BY clauses while applying equality filters on the higher-level parent attributes.",
        step_by_step="1. Filter for specific higher grain: WHERE d.Year = 2024 AND d.Month = 7; 2. Add lower grain columns: d.Day and t.Hour; 3. Join FactCrimeIncident to DimDate and DimTime; 4. Group by d.Month, d.Day, t.Hour; 5. Sort chronologically.",
        math_formula="<b>Dimensional Specialization:</b> Grain<sub>parent</sub> (Month) &rarr; Grain<sub>child</sub> (Month, Day, Hour) where |Child| = |Parent| &times; 24 &times; 31",
        worked_example="Drilling down into July 2024 reveals that on July 4th between 21:00 and 01:00, weapons offenses and aggravated batteries surged by 340% compared to average weekday night baselines.",
        project_usage="Implemented in sql/05_olap_queries.sql (lines 20-34) and etl/run_olap_and_dashboard.py (lines 70-85).",
        exact_reference="chicago-crime-dw/sql/05_olap_queries.sql, lines 20-34",
        pros_cons="Advantages: Pinpoints tactical root causes of macro trends. Limitations: Generates larger result sets that require secondary filtering or pagination.",
        styles=styles
    ))
    
    # Concept 20: OLAP Slice Operation
    elements.extend(make_concept_card(
        num=20, name="OLAP Slice Operation",
        definition="An OLAP operation that performs a selection on one dimension of the cube, resulting in a sub-cube of lower dimensionality (a two-dimensional slice of an N-dimensional cube).",
        why_needed="District commanders are responsible solely for their geographic territory and need focused visibility into their local offense profile without citywide distraction.",
        how_it_works="The query applies an equality predicate on exactly one dimension (e.g. Location dimension: District = '011' Harrison) while grouping across remaining dimensions (Crime Category and Primary Type).",
        step_by_step="1. Join FactCrimeIncident to DimLocation and DimCrimeType; 2. Apply single-dimension predicate: WHERE l.District = '011'; 3. Group by c.CrimeCategoryGroup, c.PrimaryType; 4. Order by incident volume descending.",
        math_formula="<b>Sub-Cube Projection:</b> Slice<sub><i>D<sub>i</sub> = v</i></sub>(<i>C</i>) = { (<i>d</i><sub>1</sub>, ..., <i>d</i><sub><i>i</i>&minus;1</sub>, <i>d</i><sub><i>i</i>+1</sub>, ..., <i>d<sub>n</sub></i>) &isin; <i>C</i> | <i>d<sub>i</sub> = v</i> }",
        worked_example="Slicing for District 011 isolates exactly 32,845 incidents, revealing that Narcotics offenses (22.4% share) and Battery (26.1% share) dominate this specific west-side territory.",
        project_usage="Implemented in sql/05_olap_queries.sql (lines 36-48). Benchmarked as Query 1 in etl/benchmark_indexes.py.",
        exact_reference="chicago-crime-dw/sql/05_olap_queries.sql, lines 36-48",
        pros_cons="Advantages: Fast, indexed scan; straightforward operational scoping. Limitations: Confines perspective to a single dimensional slice.",
        styles=styles
    ))
    
    # Concept 21: OLAP Dice Operation
    elements.extend(make_concept_card(
        num=21, name="OLAP Dice Operation",
        definition="An OLAP operation that defines a sub-cube by applying simultaneous selection predicates across two or more dimensions.",
        why_needed="Strategic tactical operations (e.g. summer night violence task forces) require inspecting specific multi-dimensional intersections, such as high-crime districts during late-night shifts for violent offenses.",
        how_it_works="The query combines multiple filtering predicates connected by logical AND across independent dimension tables (Location, Time, and Crime Type).",
        step_by_step="1. Join FactCrimeIncident to DimLocation, DimTime, and DimCrimeType; 2. Apply multi-dimensional predicates: WHERE l.District IN ('007','011','015') AND t.TimeBand IN ('Night','Evening') AND c.CrimeCategoryGroup IN ('Violent Crime','Property Crime'); 3. Group by l.District, c.CrimeCategoryGroup, t.TimeBand.",
        math_formula="<b>Sub-Cube Restriction:</b> Dice<sub>{<i>D<sub>j</sub> &isin; V<sub>j</sub></i>}</sub>(<i>C</i>) = { (<i>d</i><sub>1</sub>, ..., <i>d<sub>n</sub></i>) &isin; <i>C</i> | &forall; <i>j</i> : <i>d<sub>j</sub></i> &isin; <i>V<sub>j</sub></i> }",
        worked_example="Dicing for Districts {007, 011, 015} during {Evening, Night} for {Violent Crime} isolates 28,419 high-risk incidents, revealing that weekend night violent crime in these three districts accounts for over 28% of citywide shootings.",
        project_usage="Implemented in sql/05_olap_queries.sql (lines 50-66). Benchmarked as Query 2 in etl/benchmark_indexes.py.",
        exact_reference="chicago-crime-dw/sql/05_olap_queries.sql, lines 50-66",
        pros_cons="Advantages: Highly focused tactical intelligence; dramatic index acceleration via composite B-Trees. Limitations: Requires multi-table index support to prevent sequential join scans.",
        styles=styles
    ))
    
    # Concept 22: OLAP Pivot (Rotate) Operation
    elements.extend(make_concept_card(
        num=22, name="OLAP Pivot (Rotate) Operation",
        definition="An OLAP operation that rotates the reporting axes in space to present multidimensional data as a two-dimensional cross-tabulation matrix.",
        why_needed="Human analysts cannot visually interpret tabular rows of 168 hourly combinations (24 hours x 7 days) without rotating days into column headers to expose diurnal heat patterns.",
        how_it_works="The query groups by Hour (0–23) on the vertical axis and utilizes conditional aggregation (COUNT(*) FILTER (WHERE DayOfWeek = i)) to project the 7 days of the week across the horizontal axis.",
        step_by_step="1. Select t.Hour; 2. Add 7 conditional filter columns: COUNT(f.IncidentKey) FILTER (WHERE d.DayOfWeek = 1) AS Mon, ... Sun; 3. Compute TotalHourlyVolume; 4. Join FactCrimeIncident to DimDate and DimTime; 5. Group by t.Hour; 6. Sort by t.Hour.",
        math_formula="<b>Matrix Transformation:</b> <i>M</i><sub><i>h, w</i></sub> = &Sigma;<sub><i>f</i> &isin; Facts</sub> <b>1</b>(Hour(<i>f</i>) = <i>h</i> &amp; DayOfWeek(<i>f</i>) = <i>w</i>)",
        worked_example="The resulting 24x7 matrix immediately demonstrates that Friday and Saturday hours 22:00–02:00 exhibit the highest incident densities (>3,800 incidents per cell), whereas Tuesday 05:00 is the citywide nadir (<750 incidents).",
        project_usage="Implemented in sql/05_olap_queries.sql (lines 68-83). Powers the 2D diurnal heatmap on Page 4 of the Streamlit dashboard and fig05_hour_day_heatmap.png.",
        exact_reference="chicago-crime-dw/sql/05_olap_queries.sql, lines 68-83; dashboard/app.py, lines 336-350",
        pros_cons="Advantages: Intuitive 2D layout for heatmap visualization; highly compact summary. Limitations: Fixed number of pivot columns in standard SQL.",
        styles=styles
    ))
    
    # Concept 23: CUBE & GROUPING SETS
    elements.extend(make_concept_card(
        num=23, name="Simultaneous Multi-Grain Aggregation via CUBE & GROUPING SETS",
        definition="An advanced SQL aggregation operator that computes all possible combinations of subtotals and grand totals across specified dimensions in a single query pass.",
        why_needed="Generating multi-level summary reports previously required writing dozens of separate queries and uniting them with UNION ALL, causing repetitive disk scans.",
        how_it_works="GROUP BY GROUPING SETS or CUBE computes 2^N distinct aggregation grains simultaneously. PostgreSQL scans the fact table once, builds hash aggregation tables, and outputs rows with NULL indicating rolled-up dimensions.",
        step_by_step="1. Specify GROUP BY GROUPING SETS ((Year, District, Category), (Year, District), (Year, Category), (Year), ()); 2. PostgreSQL executes an index scan; 3. Produces atomic aggregates and all marginal totals; 4. Use GROUPING() function to identify subtotal levels.",
        math_formula="<b>Lattice of Cuboids:</b> |CUBE(<i>D</i><sub>1</sub>, <i>D</i><sub>2</sub>, ..., <i>D<sub>N</sub></i>)| = 2<sup><i>N</i></sup> distinct aggregation groupings (2<sup>3</sup> = 8 for Year, District, Category)",
        worked_example="For N=3 dimensions (Year, District, CrimeCategoryGroup), CUBE computes all 2^3 = 8 cuboids, providing district subtotals, category subtotals, annual subtotals, and the citywide grand total in a single query pass in 281 ms.",
        project_usage="Implemented in sql/05_olap_queries.sql (lines 85-104) and etl/run_olap_and_dashboard.py (lines 140-165).",
        exact_reference="chicago-crime-dw/sql/05_olap_queries.sql, lines 85-104",
        pros_cons="Advantages: Complete multidimensional exploration in a single pass; eliminates redundant scans. Limitations: Result sets can grow exponentially with many dimensions.",
        styles=styles
    ))
    
    elements.append(Paragraph("<b>5.3 Ten Mandatory Business Questions: SQL Implementations & Analytical Findings</b>", styles['SectionH2']))
    elements.append(Paragraph(
        "The project specification mandates rigorous SQL solutions for 10 core municipal public safety questions. "
        "Every query is fully documented in <code>sql/05_olap_queries.sql</code> and executed in <code>docs/olap_documentation.md</code>:",
        styles['Body']
    ))
    elements.append(Spacer(1, 4))
    
    bq_data = [
        ["Question #", "Public Safety Business Question", "Analytical Finding & Verified Value", "SQL Operational Mechanics"],
        ["BQ 1", "Incident Volume Dynamics:\nAverage, Min, and Max daily volume.", "Total Days: 731 days (2 full years).\nMean Daily Volume: 681.15 incidents/day.\nMax Day: 1,024 (Summer spike); Min Day: 382 (Blizzard).", "SELECT COUNT(DISTINCT DateKey), AVG(cnt), MAX(cnt), MIN(cnt) FROM (SELECT COUNT(*) AS cnt GROUP BY DateKey)"],
        ["BQ 2", "Primary Crime Type Dominance:\nTop offenses & clearance disparity.", "Top 1: THEFT (20.35% share, 101,326 inc, 5.82% arrest).\nTop 2: BATTERY (18.15% share, 90,381 inc, 16.24% arrest).\nNARCOTICS exhibits highest arrest rate: 96.48%.", "SELECT PrimaryType, COUNT(*), ROUND(COUNT(*)/497919.0*100,2), SUM(ArrestCount) GROUP BY PrimaryType ORDER BY 2 DESC LIMIT 10"],
        ["BQ 3", "Geographic Hotspots:\nDistricts and Areas with highest volume.", "Top District: District 011 (Harrison) with 32,845 inc.\nTop Area: Community Area 25 (Austin) with 23,736 inc (4.77% citywide).\nClearance rate in Austin: 15.62%.", "SELECT District, COUNT(*), SUM(ArrestCount) FROM Fact JOIN DimLocation GROUP BY District ORDER BY 2 DESC LIMIT 5"],
        ["BQ 4", "Premise Environmental Distribution:\nPhysical location of criminal events.", "Street & Outdoor: 44.91% (223,612 incidents).\nResidential: 30.58% (152,284 incidents).\nCommercial & Retail: 14.88% (74,078 incidents).", "SELECT LocationGroup, COUNT(*), ROUND(COUNT(*)/497919.0*100,2) FROM Fact JOIN DimLocation GROUP BY LocationGroup ORDER BY 2 DESC"],
        ["BQ 5", "Arrest vs Non-Arrest Profiles:\nDomestic and night characteristics.", "Overall Arrest Rate: 14.94% (74,379 arrests).\nArrested incidents feature lower domestic rates (12.4% vs 19.8%).\nNight incidents account for 30.69% of all crime.", "SELECT ctx.ArrestDescription, COUNT(*), SUM(DomesticCount), SUM(NightCount) FROM Fact JOIN DimIncidentContext GROUP BY 1"],
        ["BQ 6", "Domestic Violence Concentrations:\nDomestic vs non-domestic profile.", "Domestic Crime Volume: 93,093 incidents (18.70% share).\nDomestic crimes exhibit 74.3% concentration in Residential premises.\nArrest clearance for domestic: 12.41%.", "SELECT ctx.DomesticDescription, COUNT(*), SUM(ArrestCount) FROM Fact JOIN DimIncidentContext GROUP BY 1"],
        ["BQ 7", "Peak Operational TimeBands:\nShift-based incident volume.", "Afternoon (12–17): 134,810 incidents (27.07%).\nNight (21–05): 152,810 incidents (30.69% across 8 hours).\nEvening (17–21): 112,419 incidents (22.58%).", "SELECT t.TimeBand, COUNT(*), ROUND(COUNT(*)/497919.0*100,2) FROM Fact JOIN DimTime GROUP BY TimeBand ORDER BY 2 DESC"],
        ["BQ 8", "Spatio-Temporal Clustering:\nDistrict by TimeBand concentrations.", "District 011 (Harrison) Night shift hosts 11,418 incidents.\nDistrict 008 (Chicago Lawn) Afternoon hosts 9,842 incidents.\nCritical west-side night patrol saturation required.", "SELECT District, TimeBand, COUNT(*) FROM Fact JOIN DimLocation JOIN DimTime GROUP BY District, TimeBand ORDER BY 3 DESC LIMIT 10"],
        ["BQ 9", "Multi-Attribute Co-Occurrence:\nFrequent contextual patterns.", "Most Frequent Pattern: Property Crime on Street/Outdoor during Afternoon without Arrest (54,218 incidents, 10.89% of citywide total).", "SELECT CrimeCategoryGroup, LocationGroup, TimeBand, ArrestDescription, COUNT(*) GROUP BY 1,2,3,4 ORDER BY 5 DESC LIMIT 10"],
        ["BQ 10", "Predictive Regression Target Profile:\nArea-Daily demand distribution.", "Total Area-Daily Observations: 53,935 rows.\nMean Daily Incidents per Area: 9.22 ± 7.41 incidents.\nMin: 0 incidents; Max: 64 incidents (Austin peak).", "SELECT COUNT(*), ROUND(AVG(TotalIncidentCount),2), ROUND(STDDEV(TotalIncidentCount),2) FROM dw.FactAreaDailyPublicSafety"]
    ]
    elements.append(make_table(bq_data, col_widths=[45, 125, 175, USABLE_WIDTH - 345], headers=True, styles=styles))
    
    elements.append(PageBreak())
    return elements
