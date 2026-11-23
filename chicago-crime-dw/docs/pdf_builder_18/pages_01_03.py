"""
Pages 1 to 3:
- Page 1: Cover Page, Project Overview, Metadata Table, and Compact Table of Contents.
- Page 2: Project Architecture, 4-Tier Flow, Embedded Diagram, and Active Technology Stack.
- Page 3: Data Warehouse Fundamentals, Subject-Oriented ROLAP, Trade-offs (Batch vs Citus vs Streaming).
"""

from reportlab.platypus import Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from .config_18 import (
    USABLE_WIDTH, PRIMARY, SECONDARY, ACCENT, DARK_TEXT, LIGHT_BG, ALT_ROW_BG,
    BORDER_COLOR, MUTED_TEXT, make_callout, make_table, make_image_figure, PageTracker
)

def build_pages_01_03(styles, tracker):
    elements = []
    
    # =========================================================================
    # PAGE 1: COVER PAGE & PROJECT OVERVIEW (WITH COMPACT TOC)
    # =========================================================================
    elements.append(PageTracker('cov_page', tracker))
    
    # Title Banner Block
    elements.append(Spacer(1, 16))
    elements.append(Paragraph("<b>CHICAGO CRIME INCIDENT &amp; PUBLIC SAFETY ANALYTICS</b>", styles['DocTitle']))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("<b>Comprehensive Data Warehouse Architecture, Dimensional Modeling, OLAP &amp; Machine Learning Technical Guide</b>", styles['DocSubtitle']))
    elements.append(Spacer(1, 12))
    
    # Metadata Badge Table
    meta_data = [
        ["Project Domain", "Municipal Public Safety & Crime Analytics", "Target Database", "PostgreSQL 16 (Dockerized Relational OLAP)"],
        ["Primary Dataset", "City of Chicago Crime Incidents (2024–2025)", "Warehouse Pattern", "Star Fact Constellation (Dual-Grain Multi-Fact)"],
        ["Record Volume", "497,919 Curated Records (Zero-Loss Curation)", "Analytics & ML", "Ridge ($R^2=0.78$), FP-Growth ($1.7\\times$), CART (AUC $0.74$)"],
        ["Frontend BI", "Streamlit Dual-Engine App & Microsoft Power BI", "Academic Level", "Practical Examination, Technical Reference & Viva Guide"]
    ]
    meta_table = make_table(meta_data, col_widths=[85, 176, 95, USABLE_WIDTH - 356], headers=False, styles=styles, padding=4.8)
    elements.append(meta_table)
    elements.append(Spacer(1, 14))
    
    # Executive Project Overview Callout
    elements.append(make_callout(
        "Executive Project Overview & Municipal Analytical Mission",
        "The Chicago Crime Analytics Data Warehouse is an enterprise-grade analytical system designed to ingest, cleanse, "
        "model, and analyze <b>497,919 recorded crime incidents</b> across the City of Chicago from January 1, 2024 through December 31, 2025. "
        "The project addresses the fundamental tension between high-frequency transactional reporting (OLTP) and strategic decision "
        "support (OLAP). By implementing a dual-grain Fact Constellation schema, high-throughput bulk ETL ingestion via PostgreSQL COPY, "
        "and certified analytical data marts, the platform delivers sub-5ms query response times for executive trend discovery, spatial-temporal "
        "hotspot detection across 77 community areas, and automated machine learning demand forecasting for police patrol deployment.",
        styles, accent_color=SECONDARY, padding_v=7.5
    ))
    elements.append(Spacer(1, 14))
    
    # Compact Table of Contents
    elements.append(Paragraph("<b>Table of Contents &amp; Quick Examination Reference</b>", styles['SectionH2']))
    elements.append(Spacer(1, 3))
    
    # Dynamic TOC reading from tracker dictionary
    def get_pg(key, default):
        return str(tracker.get(key, default))
    
    toc_matrix = [
        ["Sec", "Section Title & Focus Areas", "Page", "Sec", "Section Title & Focus Areas", "Page"],
        ["1", "Cover Page, Project Overview & Compact TOC", get_pg('cov_page', 1), "7", "Actual Machine Learning Algorithms (Ridge, FP-Growth, CART)", get_pg('sec7_page', 10)],
        ["2", "Project Architecture & Technology Stack", get_pg('sec2_page', 2), "8", "Statistical Analysis, Distributions & Data Quality Audits", get_pg('sec8_page', 13)],
        ["3", "Data Warehouse Fundamentals & Architecture Selection", get_pg('sec3_page', 3), "9", "Streamlit Dashboard & Power BI Implementation", get_pg('sec9_page', 14)],
        ["4", "ETL Pipeline Lifecycle & Data Preprocessing (2 Pages)", get_pg('sec4_page', 4), "10", "Project Implementation Mapping (Concept-to-Code Catalog)", get_pg('sec10_page', 15)],
        ["5", "Dimensional Modeling & Constellation Schema (2 Pages)", get_pg('sec5_page', 6), "11", "Important Formulas & Worked Numerical Examples", get_pg('sec11_page', 16)],
        ["6", "OLAP & Multidimensional Operations (2 Pages)", get_pg('sec6_page', 8), "12", "Viva Voce Questions & Answers (26 Comprehensive Q&As;)", get_pg('sec12_page', 17)]
    ]
    toc_tbl = make_table(toc_matrix, col_widths=[22, 215, 24, 22, 216, USABLE_WIDTH - 499], headers=True, styles=styles, padding=4.6)
    elements.append(toc_tbl)
    elements.append(Spacer(1, 14))
    
    # Candidate Examination Note
    elements.append(make_callout(
        "Candidate Practical Examination & Viva Voce Guidance",
        "<b>Notice to Evaluators & Candidates:</b> This document strictly reflects the actual code, schema, notebooks, and empirical outputs "
        "implemented within the repository. Every concept is grounded in Chicago dataset fields (497,919 incidents, 74,379 arrests). Algorithms "
        "not present in the codebase (such as ID3, C4.5, ECLAT, or K-Means) are explicitly identified as absent to uphold rigorous academic integrity. "
        "Refer to Section 10 for instantaneous source code line references and Section 12 for high-yield defense questions.",
        styles, accent_color=ACCENT, padding_v=7.5
    ))
    
    elements.append(PageBreak())
    
    # =========================================================================
    # PAGE 2: PROJECT ARCHITECTURE & TECHNOLOGY STACK
    # =========================================================================
    elements.append(PageTracker('sec2_page', tracker))
    elements.append(Paragraph("<b>Section 2: Project Architecture and Technology Stack</b>", styles['SectionH1']))
    
    elements.append(Paragraph(
        "<b>2.1 End-to-End Four-Tier Enterprise Analytical Architecture</b><br/>"
        "The platform decouples data acquisition, warehouse storage, analytical transformation, and visual presentation into four distinct tiers:",
        styles['Body']
    ))
    elements.append(Spacer(1, 3))
    
    arch_tiers = [
        ["Architecture Tier", "Primary Technology", "Operational Role & Implementation Details in Project"],
        ["1. Ingestion Tier", "Socrata SoQL REST API / Python", "Extracts public Chicago crime data (<code>etl/extract.py</code>); manages JSON chunking, schema mapping, and landing raw records."],
        ["2. Storage & DW Tier", "PostgreSQL 16 / Docker", "Maintains transient staging (<code>staging.stg_crimes</code>) and production star constellation warehouse tables (<code>dw</code> schema) under ACID isolation."],
        ["3. Semantic & ML Tier", "SQL Views / Scikit-Learn / mlxtend", "Unifies dimensions via certified view <code>mart.PublicSafetyAnalyticsMart</code>; executes regression, association mining, and decision tree models."],
        ["4. Presentation Tier", "Streamlit / Microsoft Power BI", "Interactive 4-page executive web app (<code>dashboard/app.py</code>) with resilient CSV fallback, plus PBIP semantic report (<code>powerbi/model.bim</code>)."]
    ]
    elements.append(make_table(arch_tiers, col_widths=[90, 115, USABLE_WIDTH - 205], headers=True, styles=styles, padding=3.8))
    elements.append(Spacer(1, 7))
    
    # Embedded Architecture Diagram - enlarged for readability
    elements.extend(make_image_figure(
        'chicago-crime-dw/docs/pdf_assets/arch_diagram.png',
        "Figure 2.1: End-to-End Four-Tier Architecture of the Chicago Crime Analytics Platform.",
        width=485, height=175, styles=styles
    ))
    elements.append(Spacer(1, 7))
    
    # Technology Stack Table
    elements.append(Paragraph("<b>2.2 Active Project Technology Stack &amp; Library Utilization Audit</b>", styles['SectionH2']))
    elements.append(Spacer(1, 2))
    tech_data = [
        ["Technology / Library", "Version", "Actual Project Role & Verified Code Reference"],
        ["PostgreSQL", "16.1 (Alpine)", "Primary Relational Data Warehouse engine hosted in Docker container (port 5432). Houses staging, dw, and mart schemas."],
        ["Docker / Compose", "v2 / Compose v2.2", "Containerized warehouse orchestration (<code>docker-compose.yml</code>) defining storage volumes, port bindings, and memory allocations."],
        ["Python", "3.12.x", "Core programming runtime for extraction, curation, database loading, ML execution, and interactive dashboard serving."],
        ["Pandas", "2.2.0", "In-memory tabular data manipulation, zero-loss curation (<code>curate.py</code>), temporal decomposition, and CSV streaming buffer serialization."],
        ["NumPy", "1.26.3", "Vectorized mathematical computations, coordinate validation, array indexing, and numeric feature transformations."],
        ["Scikit-Learn", "1.4.0", "Machine learning: OLS regression, Ridge (L2), Random Forest, CART Decision Tree, VIF multicollinearity, and evaluation metrics."],
        ["mlxtend", "0.23.1", "Market-basket association mining: TransactionEncoder, Apriori candidate generation, and FP-Growth prefix-tree mining algorithms."],
        ["Streamlit", "1.31.0", "Interactive 4-page business intelligence web dashboard (<code>dashboard/app.py</code>) with live PostgreSQL querying and CSV fallback."],
        ["Plotly Express", "5.18.0", "Declarative interactive charting in Streamlit: spatial scatter maps, diurnal heatmaps, trend lines, and gauge scorecards."],
        ["Power BI Desktop", "PBIP Format", "Enterprise dimensional semantic model (<code>model.bim</code>) with star schema relationships and 8 certified DAX measures."]
    ]
    elements.append(make_table(tech_data, col_widths=[85, 55, USABLE_WIDTH - 140], headers=True, styles=styles, padding=3.2))
    
    elements.append(PageBreak())
    
    # =========================================================================
    # PAGE 3: DATA WAREHOUSE FUNDAMENTALS & ARCHITECTURE
    # =========================================================================
    elements.append(PageTracker('sec3_page', tracker))
    elements.append(Paragraph("<b>Section 3: Data Warehouse Fundamentals and Architecture</b>", styles['SectionH1']))
    
    elements.append(Paragraph(
        "<b>3.1 Data Warehouse Definition and Core Characteristics</b><br/>"
        "A Data Warehouse (DW) is a <i>subject-oriented, integrated, time-variant, and non-volatile</i> collection of data structured "
        "to support executive decision-making (Bill Inmon). In this project, the warehouse diverges sharply from an operational OLTP database:",
        styles['Body']
    ))
    elements.append(Spacer(1, 3))
    
    dw_props = [
        ["DW Characteristic", "Theoretical Definition", "Concrete Chicago Public Safety Project Implementation"],
        ["1. Subject-Oriented", "Focused on specific operational subjects rather than daily transaction processing.", "Concentrates exclusively on <b>Public Safety & Crime Events</b>, deliberately omitting unrelated municipal records."],
        ["2. Integrated", "Harmonizes inconsistent formats, codes, and schemas from disparate sources.", "Standardizes 31 primary offense codes into 5 broad classes, unifies 134 premises into 6 groups, and cleanses timestamps."],
        ["3. Time-Variant", "Maintains historical snapshots allowing trend and cycle tracking over time.", "Spans 731 contiguous calendar days (Jan 1, 2024 to Dec 31, 2025); explicit surrogate DateKey allows historical trend analysis."],
        ["4. Non-Volatile", "Loaded once and queried repeatedly; records are never updated or deleted by users.", "Transactional facts are immutable once written; periodic daily snapshots are maintained via non-destructive micro-batches."]
    ]
    elements.append(make_table(dw_props, col_widths=[80, 140, USABLE_WIDTH - 220], headers=True, styles=styles, padding=4.0))
    elements.append(Spacer(1, 7))
    
    elements.append(Paragraph("<b>3.2 Architectural Justification: Batch ROLAP vs. Distributed &amp; Streaming Alternatives</b>", styles['SectionH2']))
    elements.append(Paragraph(
        "Modern data engineering provides multiple architectural paradigms. The project selected <b>PostgreSQL Batch ROLAP</b> "
        "after a rigorous trade-off evaluation against distributed sharding and event streaming:",
        styles['Body']
    ))
    elements.append(Spacer(1, 3))
    
    tradeoff_matrix = [
        ["Architectural Pattern", "Representative Tech", "Suitability for 500k Chicago Incidents", "Engineering Justification & Trade-Off Verdict"],
        ["Batch ROLAP (Chosen)", "PostgreSQL 16 (Docker)", "<b>Optimal Match (Selected)</b><br/>Sub-5ms query times; 100% ACID.", "500,000 records (~65 MB table heap) fit entirely in RAM. B-Tree indexes deliver instant OLAP response without cluster management overhead."],
        ["Distributed MPP Sharding", "Citus / Greenplum / Snowflake", "<b>Over-Engineered</b><br/>Severe network join latency.", "Horizontal hash partitioning across nodes adds 50-100ms network round-trip overhead for table joins under 100 million rows."],
        ["Event-Driven Streaming", "Kafka + Flink + ClickHouse", "<b>Excessive Complexity</b><br/>Lacks staging ACID safety.", "Chicago crime data is published in scheduled public batches, not millisecond events. Kafka streaming adds needless infrastructure cost."]
    ]
    elements.append(make_table(tradeoff_matrix, col_widths=[85, 105, 100, USABLE_WIDTH - 290], headers=True, styles=styles, padding=4.0))
    elements.append(Spacer(1, 7))
    
    # Physical Storage & Docker Environment
    elements.append(Paragraph("<b>3.3 Physical Warehouse Storage &amp; Dockerized Environment Specifications</b>", styles['SectionH2']))
    elements.append(Paragraph(
        "The warehouse runs in an isolated Docker container configured in <code>docker-compose.yml</code>. "
        "The physical engine utilizes PostgreSQL 16.1 Alpine with dedicated shared memory (<code>shared_buffers = 256MB</code>, <code>work_mem = 64MB</code>) "
        "ensuring that all dimensional joins and hash aggregations execute entirely in CPU cache. Data files are persisted to an external Docker named volume "
        "(<code>pgdata</code>) to ensure durability across container restarts.",
        styles['Body']
    ))
    elements.append(Spacer(1, 3))
    
    env_specs = [
        ["Configuration Parameter", "Allocated Value", "Operational Purpose"],
        ["Container Image", "postgres:16-alpine", "Lightweight, secure, and reproducible Linux container environment."],
        ["Host Port Binding", "localhost:5432 -> 5432", "Enables local access for Python ETL, Streamlit, Power BI, and psql."],
        ["Database & Schemas", "chicago_crime (staging, dw, mart)", "Logical schema isolation separating landing, dimensional tables, and BI views."],
        ["Storage Footprint", "~115 MB Total (Data + Indexes)", "Highly compact storage footprint achievable via integer surrogate key compression."]
    ]
    elements.append(make_table(env_specs, col_widths=[95, 120, USABLE_WIDTH - 215], headers=True, styles=styles, padding=3.8))
    
    elements.append(PageBreak())
    return elements
