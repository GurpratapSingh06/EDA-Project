"""
Pages 8 to 9:
- Page 8: Conceptual Hypercube vs ROLAP, Embedded 3D OLAP Cube Diagram, and Formal Mechanics of 6 OLAP Operations.
- Page 9: Ten Mandatory Municipal Business Questions: Production SQL Queries & Empirical Analytical Findings.
"""

from reportlab.platypus import Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from .config_18 import (
    USABLE_WIDTH, PRIMARY, SECONDARY, ACCENT, DARK_TEXT, LIGHT_BG, ALT_ROW_BG,
    BORDER_COLOR, MUTED_TEXT, make_callout, make_table, make_image_figure, PageTracker
)

def build_pages_08_09(styles, tracker):
    elements = []
    
    # =========================================================================
    # PAGE 8: OLAP & MULTIDIMENSIONAL OPERATIONS
    # =========================================================================
    elements.append(PageTracker('sec6_page', tracker))
    elements.append(Paragraph("<b>Section 6: OLAP and Multidimensional Operations</b>", styles['SectionH1']))
    
    elements.append(Paragraph(
        "<b>6.1 Conceptual Hypercube vs. Relational OLAP (ROLAP) Architecture</b><br/>"
        "In multidimensional analytics, data is conceptualized as an <b>N-dimensional Hypercube</b> where each axis represents an independent "
        "dimension (Time, Location, Crime Type) and each coordinate cell contains additive numeric measures (Incident Count, Arrest Count). "
        "While specialized Multidimensional OLAP (MOLAP) engines store dense arrays on disk, this project implements <b>Relational OLAP (ROLAP)</b> "
        "on PostgreSQL 16. The logical hypercube is materialized on demand over relational tables using secondary B-Tree indexes and ANSI SQL-99 "
        "grouping extensions, delivering sub-second response times without the storage explosion of pre-materialized multidimensional arrays.",
        styles['Body']
    ))
    elements.append(Spacer(1, 6))
    
    # Embedded 3D OLAP Cube Diagram - enlarged for full perspective clarity
    elements.extend(make_image_figure(
        'chicago-crime-dw/docs/pdf_assets/olap_cube_concept.png',
        "Figure 6.1: Conceptual 3D OLAP Hypercube (Time, Location, Crime Type) with Highlighted Slice/Dice Sub-Cube.",
        width=470, height=165, styles=styles
    ))
    elements.append(Spacer(1, 8))
    
    # Six Core OLAP Operations Table
    elements.append(Paragraph("<b>6.2 Formal Mechanics of the Six Implemented OLAP Operations in <code>sql/05_olap_queries.sql</code></b>", styles['SectionH2']))
    elements.append(Spacer(1, 2))
    olap_ops = [
        ["OLAP Operation", "Mathematical Definition", "SQL Implementation Syntax", "Chicago Public Safety Analytical Demonstration"],
        ["1. Roll-Up", "Aggregates facts by climbing up an ordered dimensional hierarchy (Hour &rarr; Day &rarr; Month &rarr; Year).", "<code>GROUP BY ROLLUP (d.Year, d.Quarter, d.Month)</code>", "Computes monthly totals, quarterly subtotals (Q1: 57,065), and annual totals (2024: 251,467) in a single pass."],
        ["2. Drill-Down", "De-aggregates data; moves from summary level down to fine-grained operational attributes.", "<code>WHERE d.Month = 7 GROUP BY d.Day, t.Hour</code>", "Drills into the July 2024 peak to reveal that July 4th night hours (21:00–01:00) experienced a 340% weapons spike."],
        ["3. Slice", "Filters the hypercube on a single dimensional predicate, producing a 2D sub-cube.", "<code>WHERE l.District = '011' GROUP BY c.PrimaryType</code>", "Isolates District 011 (Harrison; 32,845 crimes), revealing that Battery (26.1%) and Narcotics (22.4%) dominate."],
        ["4. Dice", "Restricts the hypercube across two or more dimensions simultaneously, isolating a targeted sub-cube.", "<code>WHERE l.District IN ('007','011','015') AND t.TimeBand = 'Night' AND c.Group = 'Violent'</code>", "Dices high-violence districts during Night shifts for Violent Crime (28,419 crimes), revealing 28%+ of city shootings."],
        ["5. Pivot (Rotate)", "Rotates the dimensional axes to present data as a 2D cross-tabular matrix.", "<code>GROUP BY t.Hour; COUNT(*) FILTER (WHERE DayOfWeek = i)</code>", "Transforms 168 hourly combinations into a 24-hour &times; 7-day cross-tabular matrix, powering diurnal heatmaps."],
        ["6. CUBE / GROUPING SETS", "Computes simultaneous multi-grain subtotals across all $2^N$ combinations in a single pass.", "<code>GROUP BY GROUPING SETS ((Year, District, Category), (Year, District), ())</code>", "Calculates 8 distinct cuboids across Year, District, and Offense Category in 281ms, eliminating UNION ALL scans."]
    ]
    elements.append(make_table(olap_ops, col_widths=[75, 115, 125, USABLE_WIDTH - 315], headers=True, styles=styles, padding=3.8))
    
    elements.append(PageBreak())
    
    # =========================================================================
    # PAGE 9: TEN MANDATORY BUSINESS QUESTIONS & FINDINGS
    # =========================================================================
    elements.append(Paragraph("<b>Section 6 (Continued): Ten Mandatory Municipal Business Questions &amp; Findings</b>", styles['SectionH1']))
    
    elements.append(Paragraph(
        "<b>6.3 Production SQL Implementations and Empirical Analytical Findings</b><br/>"
        "The project specification mandates rigorous SQL solutions for 10 core public safety questions. "
        "Every query was executed against <code>mart.PublicSafetyAnalyticsMart</code> and benchmarked:",
        styles['Body']
    ))
    elements.append(Spacer(1, 3))
    
    biz_queries = [
        ["#", "Business Analysis Question", "Production SQL Implementation Strategy", "Empirical Findings & Public Safety Intelligence"],
        ["Q1", "Annual, Quarterly &amp; Monthly Trends", "<code>GROUP BY ROLLUP (d.Year, d.Quarter, d.Month)</code>", "2024: 251,467; 2025: 246,452 (-2.0%). Summer peaks in July/August (>23,500/mo); winter nadir in February (17,211)."],
        ["Q2", "Top 5 High-Crime Community Areas", "<code>GROUP BY l.CommunityArea ORDER BY Count DESC LIMIT 5</code>", "1. Austin: 23,736; 2. Near North: 20,404; 3. Loop: 18,367; 4. West Town: 15,364; 5. North Lawndale: 14,028."],
        ["Q3", "Arrest Clearance Rates by Offense", "<code>ROUND((SUM(ArrestCount)::numeric / COUNT(*))*100, 2)</code>", "Substance: 96.5% arrest rate; Weapons: 78.1%; Violent: 17.8%; Other: 15.2%; Property: <b>4.8%</b> (severe clearance gap)."],
        ["Q4", "Diurnal Shift &amp; Night Crime Breakdown", "<code>GROUP BY t.TimeBand, t.IsNightIncident</code>", "Night (21-05): 190,443 (38.2%); Afternoon (12-17): 145,021 (29.1%); Evening: 106,455 (21.4%); Morning: 56,000 (11.3%)."],
        ["Q5", "Domestic Violence Premise Distribution", "<code>WHERE f.DomesticFlag = 1 GROUP BY l.LocationGroup</code>", "Residential premises account for <b>64.2%</b> of all domestic offenses; outdoor street incidents account for only 12.1%."],
        ["Q6", "Weekend vs. Weekday Severity Shift", "<code>GROUP BY d.IsWeekend, c.CrimeCategoryGroup</code>", "Weekend volume increases by 8.4%; weekend late-night violent crimes (shootings, batteries) surge by <b>24.6%</b>."],
        ["Q7", "High-Risk Tactical Patrol Sub-Cube", "<code>WHERE District IN ('007','011','015') AND Night AND Violent</code>", "Districts 007, 011, and 015 account for 28.4% of all night-time violent offenses despite representing 13.6% of population."],
        ["Q8", "Property Crime &amp; Auto Theft Clearances", "<code>WHERE PrimaryType = 'MOTOR VEHICLE THEFT'</code>", "Motor vehicle thefts (54,821 incidents) exhibit an extremely low custodial arrest rate of <b>3.4%</b> (victim retrospective reporting)."],
        ["Q9", "Seasonal Climate Volatility Correlation", "<code>GROUP BY d.MonthName, c.CrimeCategoryGroup</code>", "Violent street crimes surge by <b>38.2%</b> from February (coldest) to July (warmest), tracking outdoor social density."],
        ["Q10", "Simultaneous Multi-Grain Cube Summary", "<code>GROUP BY CUBE (d.Year, l.District, c.CrimeCategoryGroup)</code>", "Computes all 8 dimensional cuboids in 281ms, providing immediate citywide, district, and offense subtotals."]
    ]
    elements.append(make_table(biz_queries, col_widths=[18, 115, 140, USABLE_WIDTH - 273], headers=True, styles=styles, padding=4.6))
    elements.append(Spacer(1, 10))
    
    elements.append(make_callout(
        "Strategic Operational Implications for Police Resource Allocation",
        "The empirical findings derived from OLAP queries Q1 through Q10 provide immediate municipal intelligence: "
        "(1) <b>Patrol Density:</b> Patrol forces must be dynamically surged toward western districts (011 Harrison, 015 Austin) during summer weekend night shifts, where violent crime density peaks at 24.6% above weekday baselines; "
        "(2) <b>Technological Intervention:</b> Property crimes require automated license plate readers (ALPR) and digital forensic tracking rather than static visible patrols due to an acute 95.2% non-arrest rate; "
        "and (3) <b>Community Co-Response:</b> Domestic violence is overwhelmingly concentrated in residential premises (64.2%), necessitating integrated mental health and victim-advocacy co-responder units directly embedded in neighborhood precinct dispatches.",
        styles, accent_color=PRIMARY, padding_v=7.0
    ))
    
    elements.append(PageBreak())
    return elements
