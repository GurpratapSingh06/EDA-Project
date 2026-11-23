"""
Section 1: Cover Page, Table of Contents, Project Purpose, Repository Anatomy,
and Warehouse Architectural Evaluation (Batch vs. Distributed vs. Streaming).
"""

from reportlab.platypus import Paragraph, Spacer, PageBreak, KeepTogether, Table, TableStyle
from reportlab.lib import colors
from .config import (
    USABLE_WIDTH, PRIMARY, SECONDARY, ACCENT, DARK_TEXT, LIGHT_BG,
    BORDER_COLOR, make_callout, make_table, make_image_figure, PageTracker
)

def build_cover_page(styles):
    """Constructs a professional university-level cover page."""
    elements = []
    
    # Header Banner Block
    banner_data = [[
        Paragraph("<font color='white' size=11><b>DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING</b></font><br/>"
                  "<font color='#CBD5E0' size=8.5>Integrated Data Warehouse, OLAP & Predictive Data Mining Project Reference</font>",
                  styles['THeader'])
    ]]
    banner_tbl = Table(banner_data, colWidths=[USABLE_WIDTH])
    banner_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), PRIMARY),
        ('TOPPADDING', (0,0), (-1,-1), 16),
        ('BOTTOMPADDING', (0,0), (-1,-1), 16),
        ('LEFTPADDING', (0,0), (-1,-1), 18),
        ('RIGHTPADDING', (0,0), (-1,-1), 18),
    ]))
    elements.append(banner_tbl)
    elements.append(Spacer(1, 40))
    
    # Document Super-Title & Title
    elements.append(Paragraph("<font color='#C05621' size=10><b>OFFICIAL LABORATORY & PRACTICAL VIVA REFERENCE MANUAL</b></font>", styles['BodyBold']))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph("Crime Incident & Public Safety Analytics Data Warehouse", styles['DocTitle']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("<b>Design and Implementation of a Centralized Batch Data Warehouse on PostgreSQL 16 with Conformed Dimensional Modeling, Multidimensional OLAP, Interactive BI Dashboards, and Predictive Data Mining</b>", styles['DocSubtitle']))
    elements.append(Spacer(1, 25))
    
    # Project Scope & Metadata Box
    meta_rows = [
        ["Study Scope & Window", "January 1, 2024 to December 31, 2025 (2 Full Calendar Years)"],
        ["Official Data Source", "City of Chicago Data Portal (Socrata API Identifier: ijzp-q8t2)"],
        ["Total Volume Analyzed", "497,919 Reported Crime Incidents (103.17 MB Raw / 203.07 MB Curated)"],
        ["Storage & Processing", "PostgreSQL 16 Alpine via Docker Compose (Port 5432) | Set-Oriented SQL COPY"],
        ["Dimensional Schema", "Dual-Grain Fact Constellation (Incident Grain + Daily Community Area Grain)"],
        ["Machine Learning Suite", "Ridge Regression (Demand Forecasting), FP-Growth (Association), CART Tree (Arrest)"],
        ["Analytics Dashboards", "Streamlit BI Web Application (4 Dynamic Pages) & Power BI Desktop (.pbip)"],
        ["Target Audience", "B.Tech / MCA Data Engineering & Data Mining Practical & Viva Voce Candidates"]
    ]
    meta_tbl = make_table(meta_rows, col_widths=[140, USABLE_WIDTH - 140], headers=False, styles=styles)
    elements.append(meta_tbl)
    elements.append(Spacer(1, 35))
    
    # Key Highlights Callout
    elements.append(make_callout(
        "<b>Rigorous Empirical Validation Notice:</b> Every concept, metric, SQL query, and algorithmic formula "
        "documented in this reference guide is directly derived from the verified source code in the <code>chicago-crime-dw/</code> "
        "repository. All reported benchmark figures (such as 497,919 reconciled records, Ridge Regression R² = 0.7826, "
        "FP-Growth 1.7x acceleration over Apriori, and 14.94% baseline arrest clearance) represent actual laboratory execution outputs.",
        title="Authoritative Project Baseline", color=SECONDARY, styles=styles
    ))
    
    elements.append(Spacer(1, 45))
    elements.append(Paragraph("<font size=7.5 color='#718096'>Compiled for Academic Year 2024–2026 | PEC Exploratory Data Analytics Laboratory | Strictly Grounded in Executable Implementation</font>", styles['Body']))
    elements.append(PageBreak())
    return elements

def build_table_of_contents(styles, tracker):
    """Builds the dynamic Table of Contents using PageTracker values."""
    elements = []
    elements.append(PageTracker('toc_page', tracker))
    elements.append(Paragraph("<b>Table of Contents</b>", styles['SectionH1']))
    elements.append(Spacer(1, 6))
    
    toc_items = [
        ("Section 1: Executive Overview, Project Anatomy & Architecture Justification", "sec1"),
        ("Section 2: Data Preprocessing, Quality Auditing & Feature Engineering", "sec2"),
        ("Section 3: Dimensional Modeling & Fact Constellation Schema Design", "sec3"),
        ("Section 4: End-to-End Batch ETL Lifecycle & Operational Mechanics", "sec4"),
        ("Section 5: Multidimensional OLAP Operations & Business Analysis", "sec5"),
        ("Section 6: Predictive Data Mining & Machine Learning Pipelines", "sec6"),
        ("Section 7: Business Intelligence & Interactive Dashboard Systems", "sec7"),
        ("Section 8: Technology Stack, Libraries & Execution Environment", "sec8"),
        ("Section 9: Master Concept-to-Implementation Mapping Catalog", "sec9"),
        ("Section 10: Comprehensive Project-Specific Viva Voce Examination Guide (35 Q&As)", "sec10")
    ]
    
    toc_data = [["Section Title", "Page"]]
    for title, key in toc_items:
        page_str = str(tracker.get(key, "--"))
        toc_data.append([title, page_str])
        
    t = make_table(toc_data, col_widths=[USABLE_WIDTH - 45, 45], headers=True, styles=styles)
    elements.append(t)
    elements.append(Spacer(1, 15))
    
    elements.append(make_callout(
        "<b>How to use this guide:</b> This document serves as a complete study guide and viva preparation manual. "
        "Every concept is formulated according to a 10-point educational template: Definition, Business Need, Working Principle, "
        "Step-by-Step Mechanics, Mathematical Formulas, Concrete Numerical Examples, Exact Project Usage, Source Code Links, "
        "and Inherent Trade-offs. Refer directly to Section 9 for instantaneous file-level lookups during examinations.",
        title="Examiner & Candidate Study Note", color=ACCENT, styles=styles
    ))
    elements.append(PageBreak())
    return elements

def build_section_1(styles, tracker):
    """Constructs Section 1: Executive Overview, Anatomy, and Architectural Evaluation."""
    elements = []
    elements.append(PageTracker('sec1', tracker))
    
    elements.append(Paragraph("<b>Section 1: Executive Overview, Project Anatomy & Architecture Evaluation</b>", styles['SectionH1']))
    elements.append(Spacer(1, 4))
    
    elements.append(Paragraph("<b>1.1 Project Purpose and Strategic Public Safety Objectives</b>", styles['SectionH2']))
    elements.append(Paragraph(
        "Municipal law enforcement agencies record hundreds of thousands of incident records annually. While operational "
        "databases excel at Online Transaction Processing (OLTP) for immediate call dispatching and case booking, they are "
        "fundamentally ill-equipped for longitudinal resource allocation, hotspot trend forecasting, and clearance rate analysis. "
        "The Chicago Crime Analytics Data Warehouse resolves this fundamental bottleneck by implementing a high-throughput, "
        "reconciled Batch Data Warehouse spanning <b>497,919 crime incidents</b> occurring between January 1, 2024 and December 31, 2025. "
        "The system equips municipal leadership, police district commanders, and public policy researchers with certified analytical marts, "
        "sub-5ms multi-dimensional slice-and-dice aggregations, and predictive machine learning models.",
        styles['Body']
    ))
    elements.append(Spacer(1, 6))
    
    # Repository Inventory Table
    elements.append(Paragraph("<b>1.2 Comprehensive Repository File & Directory Manifest</b>", styles['SectionH2']))
    repo_rows = [
        ["Directory / File", "Technical Function & Role in Lifecycle"],
        ["docker-compose.yml", "Container definition for PostgreSQL 16 Alpine with isolated pgdata volume on port 5432."],
        ["requirements.txt", "Explicit Python package dependencies (pandas, scikit-learn, mlxtend, psycopg2, etc.)."],
        ["data/raw/crimes_2024_2025.csv", "497,919 raw extracted incident records (103.17 MB) directly from the Socrata SoQL API."],
        ["data/curated/crimes_curated.csv", "497,919 clean records (203.07 MB) with 13 engineered features; zero records dropped."],
        ["etl/extract.py", "Multi-threaded extraction client using ThreadPoolExecutor (6 workers) with SoQL pagination."],
        ["etl/profile_data.py", "Pre-cleaning diagnostic script auditing nulls, duplicate keys, timestamps, and bounding boxes."],
        ["etl/curate.py", "Data quality remediation pipeline imputing -1/UNKNOWN and deriving analytical dimensions."],
        ["etl/load_initial.py", "Bulk warehouse ingestion script loading Jan 2024–Nov 2025 (480,310 rows) in 88.61 seconds."],
        ["etl/load_incremental.py", "Micro-batch delta loader ingesting December 2025 (17,609 rows) non-destructively in 2.46 seconds."],
        ["etl/validate.py", "Reconciliation engine checking row totals (497,919/497,919), zero orphan keys, and measures."],
        ["etl/benchmark_indexes.py", "Profiling suite running EXPLAIN ANALYZE across 5 OLAP queries pre- and post-indexing."],
        ["etl/run_olap_and_dashboard.py", "Executes 6 OLAP operations, answers 10 business questions, and exports Power BI CSVs."],
        ["etl/run_ml_models.py", "Trains Ridge Regression, evaluates Apriori vs FP-Growth, and builds balanced Decision Tree."],
        ["sql/00_schemas.sql to 07_validation.sql", "Modular SQL DDL/DML defining staging, dw, mart schemas, constraints, views, and tests."],
        ["dashboard/app.py", "Interactive 4-page Streamlit BI application connecting to live PostgreSQL with CSV fallback."],
        ["powerbi/ChicagoCrimeAnalytics.pbip", "Ready-to-open Power BI Developer Project with 8 DAX measures and Star Schema bindings."],
        ["notebooks/01 to 06.ipynb", "Fully executed Jupyter notebooks with rich interactive figures and analytical interpretations."]
    ]
    elements.append(make_table(repo_rows, col_widths=[145, USABLE_WIDTH - 145], headers=True, styles=styles))
    elements.append(Spacer(1, 10))
    
    # System Architecture Diagram
    elements.append(Paragraph("<b>1.3 End-to-End System Engineering Architecture</b>", styles['SectionH2']))
    elements.extend(make_image_figure('chicago-crime-dw/docs/pdf_assets/arch_diagram.png',
                                      "Figure 1.1: Four-Tier Centralized Batch Data Warehouse Architecture from Socrata Ingestion to BI Applications.",
                                      width=485, styles=styles))
    elements.append(Spacer(1, 8))
    
    # Architectural Evaluation
    elements.append(Paragraph("<b>1.4 Architectural Evaluation: Why Centralized Batch DW Outperformed Alternatives</b>", styles['SectionH2']))
    elements.append(Paragraph(
        "A critical engineering question in municipal data warehousing is the choice of architectural paradigm. "
        "The project conducted a rigorous comparison in <code>docs/architecture_evaluation.md</code> evaluating three paradigms: "
        "Centralized Batch DW (PostgreSQL 16), Distributed DW (Citus / Spark), and Real-Time Streaming DW (Kafka / ClickHouse).",
        styles['Body']
    ))
    elements.append(Spacer(1, 4))
    
    arch_comp = [
        ["Evaluation Dimension", "Centralized Batch DW (PostgreSQL 16)\n[Physically Implemented & Measured]", "Distributed DW (Citus / Spark)\n[Analytical Reasoning Evaluation]", "Streaming DW (Kafka + ClickHouse)\n[Analytical Reasoning Evaluation]"],
        ["Data Arrival Pattern", "Micro-batch / Monthly Delta:\nInitial 480k bulk load, monthly increment 17.6k.", "Large Partitioned Batches:\nNightly chunk ingestion across worker shards.", "Continuous Event Stream:\nSub-second event stream generated via CAD dispatch."],
        ["Storage Engine", "Single-Node PostgreSQL 16:\nB-Tree indexes, foreign-key ACID MVCC.", "Sharded Worker Nodes:\nTables distributed horizontally by hash keys.", "Columnar ClickHouse MergeTree:\nSparse primary indexes, SIMD vectorization."],
        ["Ingestion Latency", "Initial: 88.61 s (480k rows)\nIncremental: 2.46 s (17.6k rows)", "Moderate: 15–30 s per chunk dominated by coordinator scatter/gather dispatch.", "Ultra-Low: < 1 s from Kafka topic to ClickHouse table queryability."],
        ["Scalability Horizon", "10–20 Million rows comfortably in memory (500k rows uses only 187 MB).", "Linear Horizontal Scaling:\nHundreds of millions across commodity nodes.", "Extreme Throughput:\n100,000+ streaming events per second."],
        ["Analytical Join Depth", "Full ANSI SQL Support:\nMulti-table joins, subqueries, certified views.", "Co-located joins fast; non-colocated cross-shard joins incur high network shuffle overhead.", "Limited relational join depth; optimized for single-table columnar aggregations."],
        ["Engineering Overhead", "Minimal: 1 Docker container, standard SQL, zero cluster synchronization.", "High: Shard placement, 2PC distributed transactions, rebalancing complexity.", "Very High: Zookeeper/KRaft, Kafka brokers, Spark workers, schema drift monitoring."]
    ]
    elements.append(make_table(arch_comp, col_widths=[95, 140, 140, 140], headers=True, styles=styles))
    elements.append(Spacer(1, 8))
    
    elements.append(make_callout(
        "<b>Architectural Decision Justification:</b> For a two-year municipal dataset of ~500,000 rows (103 MB raw CSV), "
        "the entire dataset fits comfortably into the operating system page cache and PostgreSQL <code>shared_buffers</code>. "
        "A distributed Citus architecture would introduce unnecessary TCP serialization and 20–40ms cross-node network shuffle "
        "penalties with zero analytical gain. Furthermore, municipal crime data is released in retrospective batch cycles by the "
        "police department rather than live streams. Thus, a centralized relational batch warehouse on PostgreSQL 16 provides "
        "optimal performance, sub-5ms query response via constellation aggregation, and guaranteed ACID consistency.",
        title="Design Choice Justification", color=PRIMARY, styles=styles
    ))
    
    elements.append(PageBreak())
    return elements
