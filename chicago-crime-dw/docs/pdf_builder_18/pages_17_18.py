"""
Pages 17 to 18:
- Page 17: Section 12: Comprehensive Viva Voce Examination Guide (Part 1: Questions 1 to 13).
- Page 18: Section 12: Comprehensive Viva Voce Examination Guide (Part 2: Questions 14 to 26).
"""

from reportlab.platypus import Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from .config_18 import (
    USABLE_WIDTH, PRIMARY, SECONDARY, ACCENT, DARK_TEXT, LIGHT_BG, ALT_ROW_BG,
    BORDER_COLOR, MUTED_TEXT, SUCCESS_COLOR, make_callout, make_table, PageTracker
)

def build_pages_17_18(styles, tracker):
    elements = []
    
    # =========================================================================
    # PAGE 17: VIVA VOCE QUESTIONS & ANSWERS (PART 1: QUESTIONS 1 TO 13)
    # =========================================================================
    elements.append(PageTracker('sec12_page', tracker))
    elements.append(Paragraph("<b>Section 12: Comprehensive Project-Specific Viva Voce Examination Guide</b>", styles['SectionH1']))
    
    elements.append(Paragraph(
        "<b>Part 1: Architecture, Dimensional Modeling, Ingestion &amp; OLAP Operations (Questions 1 to 13)</b><br/>"
        "These 26 high-yield questions provide concise, project-grounded model answers for practical examinations and project defenses:",
        styles['Body']
    ))
    elements.append(Spacer(1, 4))
    
    q_part1 = [
        ["#", "Viva Examination Question", "Project-Specific Model Answer &amp; Code Evidence"],
        ["Q1", "What is the core business objective and primary dataset size of this project?",
         "To build a decision-support data warehouse analyzing <b>497,919 recorded crime incidents</b> across Chicago (2024–2025). It bridges the gap between transactional reporting (OLTP) and strategic decision-support (OLAP), providing sub-5ms spatial-temporal queries, executive BI dashboards, and ML patrol demand forecasting."],
        ["Q2", "Why was a Fact Constellation schema chosen over a simple Star schema?",
         "A single star schema forces all queries to scan atomic transaction facts (497,919 rows). The <b>Fact Constellation</b> deploys dual fact tables sharing conformed dimensions: <code>FactCrimeIncident</code> at atomic grain and <code>FactAreaDailyPublicSafety</code> at periodic snapshot grain, accelerating area-level analytics by <b>68.9x (4.2ms vs 289ms)</b>."],
        ["Q3", "What is the exact difference in grain between the two fact tables?",
         "<code>dw.FactCrimeIncident</code> has a grain of <b>one row per reported crime event</b> (497,919 rows) containing additive flags. <code>dw.FactAreaDailyPublicSafety</code> has a grain of <b>one row per (Community Area &times; Calendar Date)</b> (53,935 rows) containing pre-aggregated daily counts and arrest clearance rates."],
        ["Q4", "What are conformed dimensions and which ones are implemented here?",
         "Conformed dimensions share identical surrogate keys and attribute definitions across multiple fact tables. The project implements four: <code>dw.DimDate</code> (731 days), <code>dw.DimTime</code> (1,440 mins), <code>dw.DimCrimeType</code> (487 codes), and <code>dw.DimLocation</code> (28,321 spatial points), guaranteeing consistent reporting across facts."],
        ["Q5", "Why did the project implement integer surrogate keys instead of natural keys?",
         "Natural keys (CPD IUCR codes, Case Numbers) are volatile alphanumeric strings. Integer surrogate keys (INT4) consume only 4 bytes vs 40+ bytes for UUIDs, achieving <b>10x memory compression</b> in B-Tree index structures, faster CPU equality joins, and allowing standardized -1 Unknown members."],
        ["Q6", "What is a degenerate dimension and how is it used in this project?",
         "A dimension key stored directly in the fact table without joining to an external table because it lacks descriptive attributes. The operational handles <code>IncidentID</code> (BIGINT) and <code>CaseNumber</code> (VARCHAR(20)) reside directly in <code>FactCrimeIncident</code>, providing instant audit traceability without join overhead."],
        ["Q7", "What is a junk dimension and what does <code>dw.DimIncidentContext</code> contain?",
         "A single consolidated dimension table combining multiple low-cardinality flags to prevent fact table clutter. <code>dw.DimIncidentContext</code> combines 3 binary flags ($2^3 = 8$ rows + 1 Unknown): <code>ArrestFlag</code>, <code>DomesticFlag</code>, and <code>NightFlag</code> into a single <code>ContextKey</code> (1 to 8) with descriptive narrative labels."],
        ["Q8", "How does the project handle missing source data without dropping records?",
         "The project enforces an absolute <b>Zero-Loss Curation Policy (&Delta;=0)</b>. Rather than calling <code>dropna()</code>, missing attributes are selectively imputed with standardized sentinel tokens: <code>-1</code> for numeric foreign keys (e.g. 676 missing community areas) and <code>'UNKNOWN'</code> for text descriptions, preserving all 497,919 rows."],
        ["Q9", "Why is PostgreSQL <code>COPY</code> used instead of standard SQL <code>INSERT</code> statements?",
         "Standard multi-row <code>INSERT</code> requires query parsing, statement planning, and per-row WAL overhead (taking ~43.5 minutes for 480k rows at 184 rows/s). PostgreSQL <code>COPY</code> streams an in-memory TSV buffer directly to disk blocks in <b>14.18 seconds (~34,000 rows/s)</b>, achieving a <b>190x throughput increase</b>."],
        ["Q10", "How does the non-destructive incremental micro-batch load work?",
         "In <code>etl/load_incremental.py</code>, the December 2025 delta (17,609 rows) lands in staging. Net-new dimension members (233 new street locations) are detected via <code>LEFT JOIN ... WHERE LocationKey IS NULL</code> and appended, followed by incident fact insertion in <b>2.46 seconds</b> without touching historical data."],
        ["Q11", "How does Relational OLAP (ROLAP) differ from a conceptual multidimensional cube?",
         "A conceptual hypercube models dimensions as orthogonal spatial axes (Time, Location, Crime Type). While MOLAP pre-materializes dense physical multi-dimensional arrays, ROLAP materializes the cube dynamically over normalized relational tables using secondary B-Tree indexes, avoiding multidimensional storage explosion."],
        ["Q12", "How are Roll-Up and Drill-Down demonstrated in the project?",
         "<b>Roll-Up:</b> Aggregates facts up the temporal hierarchy (Day &rarr; Month &rarr; Quarter &rarr; Year) via SQL <code>GROUP BY ROLLUP</code>. <b>Drill-Down:</b> De-aggregates summary data down to finer operational attributes (e.g. drilling from the July 2024 peak down to July 4th night hours 21:00–01:00)."],
        ["Q13", "What is the difference between an OLAP Slice and an OLAP Dice operation?",
         "<b>Slice:</b> Restricts the hypercube on <i>exactly one</i> dimension (e.g. filtering Location for District = '011' Harrison). <b>Dice:</b> Restricts the hypercube across <i>two or more</i> dimensions simultaneously (e.g. Districts IN (007,011,015) AND TimeBand = 'Night' AND Category = 'Violent')."]
    ]
    elements.append(make_table(q_part1, col_widths=[20, 140, USABLE_WIDTH - 160], headers=True, styles=styles, padding=3.8))
    
    elements.append(PageBreak())
    
    # =========================================================================
    # PAGE 18: VIVA VOCE QUESTIONS & ANSWERS (PART 2: QUESTIONS 14 TO 26)
    # =========================================================================
    elements.append(Paragraph("<b>Section 12 (Continued): Comprehensive Viva Voce Examination Guide</b>", styles['SectionH1']))
    
    elements.append(Paragraph(
        "<b>Part 2: Machine Learning Pipelines, Performance, Data Quality &amp; Dashboards (Questions 14 to 26)</b>",
        styles['Body']
    ))
    elements.append(Spacer(1, 4))
    
    q_part2 = [
        ["#", "Viva Examination Question", "Project-Specific Model Answer &amp; Code Evidence"],
        ["Q14", "What is the OLAP Pivot operation and how is it implemented in SQL?",
         "Pivot rotates reporting axes to project multidimensional data as a 2D matrix. In <code>sql/05_olap_queries.sql</code>, it groups by <code>Hour</code> (0–23) and uses conditional aggregation <code>COUNT(*) FILTER (WHERE DayOfWeek = i)</code> to project 7 days across columns, generating the 24x7 diurnal heatmap matrix."],
        ["Q15", "What is the purpose of SQL <code>CUBE</code> or <code>GROUPING SETS</code>?",
         "It calculates all $2^N$ simultaneous multidimensional subtotals and grand totals in a single table pass. For Year, District, and Category, <code>GROUP BY CUBE</code> generates all 8 cuboids in 281ms, replacing 8 separate queries joined via <code>UNION ALL</code>."],
        ["Q16", "Why was Ridge Regression chosen as the champion forecasting model over OLS?",
         "Time-lag features (<code>lag_1_day</code> and <code>lag_7_day_avg</code>) exhibit heavy correlation (Pearson $r=0.86$), while 77 community area dummies inflate feature dimensionality. Ridge adds an L2 penalty ($\\alpha=10.0$) that shrinks collinear weights, achieving the lowest test error: <b>$R^2 = 0.7826$</b> and <b>RMSE = 3.425</b>."],
        ["Q17", "How did you diagnose and prevent multicollinearity in regression features?",
         "Computed the Variance Inflation Factor (VIF) for each predictor: $\\text{VIF}_j = 1 / (1 - R_j^2)$. All features scored well below the 5.0 risk threshold (lag_1: 2.84, lag_7: 3.12, DayOfWeek: 1.08), mathematically proving feature matrix stability and preventing coefficient instability."],
        ["Q18", "What is the Apriori property and how does it prune candidate itemsets?",
         "The Apriori downward-closure property states: <i>All non-empty subsets of a frequent itemset must also be frequent</i>. If an itemset $X$ is infrequent ($\\text{Supp} < 0.05$), any superset containing $X$ is pruned immediately without scanning the 497,919 transactions."],
        ["Q19", "Why was FP-Growth significantly faster than Apriori in your benchmarks?",
         "Apriori performs $k$ full database passes and incurs massive combinatorial candidate generation ($C_k$). FP-Growth scans the dataset <b>only twice</b>, compressing transactions into a prefix tree (FP-Tree) and mining via recursive divide-and-conquer, completing in <b>2.35s vs 3.97s (1.7x faster)</b>."],
        ["Q20", "What do Support, Confidence, and Lift signify in public safety mining?",
         "<b>Support:</b> Global joint probability $P(X \\cup Y)$. <b>Confidence:</b> Conditional likelihood $P(Y \\mid X)$. <b>Lift:</b> Ratio of observed joint probability to independence: $\\text{Lift} > 1$ proves genuine correlation. For Street Narcotics &rarr; Arrest, <b>Lift = 11.93</b> proves arrests are 12x more likely than random baseline."],
        ["Q21", "What was the class imbalance in arrest prediction and how was it addressed?",
         "Only <b>14.94% of incidents (74,379)</b> resulted in an arrest, while 85.06% went unarrested. Standard models predict 'No Arrest' to achieve 85% accuracy. The project specified <code>class_weight='balanced'</code> ($w_{\\text{Arrest}} \\approx 3.35$), penalizing minority errors 5.7x more heavily and boosting arrest recall to <b>55.59%</b>."],
        ["Q22", "Why was CART chosen for arrest prediction and how was it pruned?",
         "CART provides human-auditable decision paths required for legal and police oversight. To prevent overfitting noisy training records, Minimal Cost-Complexity Pruning (CCP) restricted tree depth to <code>max_depth=5</code> (24 robust leaves), achieving <b>AUC = 0.7392</b> on unseen test data."],
        ["Q23", "Are ID3, C4.5, ECLAT, or K-Means clustering used in this project?",
         "<b>No.</b> Factual inspection confirms ID3, C4.5, ECLAT, and K-Means are not implemented anywhere in the repository. The project uses CART (Gini), Apriori, FP-Growth, and Ridge/OLS Regression. Stating otherwise is factually incorrect."],
        ["Q24", "What is the role of <code>mart.PublicSafetyAnalyticsMart</code>?",
         "A certified SQL view pre-joining normalized fact and dimension tables on integer surrogate keys. It provides a standardized, business-ready semantic interface for Streamlit dashboards, Power BI semantic models, and Scikit-Learn training pipelines."],
        ["Q25", "How does the Streamlit dashboard maintain resilience if PostgreSQL is offline?",
         "<code>dashboard/app.py</code> implements a resilient dual-engine loader: it attempts to connect to PostgreSQL (port 5432) first; if the container is offline, it automatically falls back to <code>data/curated/crimes_curated.csv</code>, ensuring 100% dashboard availability."],
        ["Q26", "What are the primary DAX measures configured in Power BI?",
         "Configured in <code>powerbi/model.bim</code>: <code>[Total Crimes]</code>, <code>[Arrest Count]</code>, <code>[Arrest Rate %]</code>, <code>[Violent Crime Share %]</code>, and <code>[YoY Incident Growth %]</code>, providing dynamic slicer filtering across Year, District, and Offense Category."]
    ]
    elements.append(make_table(q_part2, col_widths=[20, 140, USABLE_WIDTH - 160], headers=True, styles=styles, padding=3.8))
    elements.append(Spacer(1, 6))
    
    elements.append(make_callout(
        "Academic & Examination Conclusion",
        "The Chicago Crime Analytics Data Warehouse provides an end-to-end demonstration of enterprise data engineering: "
        "retaining 100% of data across 497,919 records, accelerating analytical queries by 68.9x through dimensional constellation design, "
        "and surfacing actionable public safety intelligence through rigorous, grounded machine learning pipelines.",
        styles, accent_color=SUCCESS_COLOR, padding_v=6.5
    ))
    
    return elements
