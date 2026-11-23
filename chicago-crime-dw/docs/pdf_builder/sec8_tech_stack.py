"""
Section 8: Technology Stack, Libraries & Execution Architecture.
Provides an exhaustive technical audit of every library, database engine,
and tool actually utilized in the executable project source code.
"""

from reportlab.platypus import Paragraph, Spacer, PageBreak, KeepTogether, Table, TableStyle
from reportlab.lib import colors
from .config import (
    USABLE_WIDTH, PRIMARY, SECONDARY, ACCENT, DARK_TEXT, LIGHT_BG,
    BORDER_COLOR, make_callout, make_table, PageTracker
)

def build_section_8(styles, tracker):
    elements = []
    elements.append(PageTracker('sec8', tracker))
    
    elements.append(Paragraph("<b>Section 8: Technology Stack, Libraries & Execution Architecture</b>", styles['SectionH1']))
    elements.append(Spacer(1, 4))
    
    elements.append(Paragraph("<b>8.1 Core Architectural Technologies and Database Engines</b>", styles['SectionH2']))
    elements.append(Paragraph(
        "The project combines enterprise open-source database technologies with modern scientific Python libraries and "
        "business intelligence tools. Every technology listed below is actively utilized in executable project code:",
        styles['Body']
    ))
    elements.append(Spacer(1, 6))
    
    tech_data = [
        ["Technology / Library", "Version Scope", "Operational Role in Chicago Crime DW Architecture"],
        ["PostgreSQL 16 (Alpine)", "v16.1+ (Docker)", "Primary relational storage engine. Implements staging, dw, and mart schemas, ACID transactions, foreign keys, B-Tree indexes, and advanced ANSI SQL OLAP aggregation (ROLLUP, CUBE, GROUPING SETS)."],
        ["Docker & Docker Compose", "Compose v3.8", "Containerizes PostgreSQL 16 on port 5432 with isolated persistent disk volume pgdata and automated health checks (pg_isready). Eliminates host configuration variance."],
        ["Python", "3.10 to 3.13", "Core programming runtime orchestrating multi-threaded API extraction, data profiling, curation pipelines, warehouse loading, ML modeling, and dashboard execution."],
        ["Pandas", ">= 2.2.0", "In-memory data manipulation, vectorized temporal decomposition, data quality profiling, feature engineering, and high-speed CSV serialization."],
        ["NumPy", ">= 1.26.0", "Underlying numerical array computations, matrix manipulations, and mathematical vectorization for machine learning pipelines."],
        ["SciPy", ">= 1.12.0", "Advanced statistical testing, empirical distribution evaluations, interquartile range (IQR), skewness, and kurtosis calculations in etl/generate_eda.py."],
        ["Scikit-Learn", ">= 1.4.0", "Machine learning suite powering Ordinary Least Squares, Ridge Regression (L2 regularization), Random Forest Regressor, and class-balanced CART Decision Tree Classifier."],
        ["MLxtend", ">= 0.23.0", "Market-basket association mining engine implementing both Apriori and FP-Growth frequent pattern algorithms and association rule evaluation (support, confidence, lift)."],
        ["Psycopg2-binary", ">= 2.9.9", "Low-level PostgreSQL database adapter providing transactional cursors and high-speed binary/TSV streaming via the PostgreSQL COPY protocol (34,000 rows/sec)."],
        ["SQLAlchemy", ">= 2.0.25", "Relational database connection abstraction and metadata management."],
        ["Streamlit", ">= 1.30.0", "Reactive web BI dashboard framework serving the 4-page analytical application on http://localhost:8501 with in-memory @st.cache_data caching."],
        ["Plotly", ">= 5.18.0", "Interactive charting engine rendering web-native scatter matrices, dual-axis bar/line curves, pie charts, and 2D diurnal heatmaps in the Streamlit app."],
        ["Matplotlib & Seaborn", ">= 3.8.0 / 0.13.0", "Publication-grade static visualization libraries generating figures fig01 through fig14 and dimensional schema ERD diagrams in docs/erd/."],
        ["Microsoft Power BI", "PBIP Format", "Enterprise developer project (ChicagoCrimeAnalytics.pbip) with Tabular Model Scripting Language (model.bim), conformed star relationships, and 8 certified DAX measures."],
        ["Jupyter & nbformat", ">= 1.0.0 / 5.9.0", "Interactive notebook authoring, programmatic notebook generation (generate_notebooks_a.py / efg.py), and headless notebook pre-execution via nbconvert."]
    ]
    elements.append(make_table(tech_data, col_widths=[125, 80, USABLE_WIDTH - 205], headers=True, styles=styles))
    elements.append(Spacer(1, 10))
    
    elements.append(make_callout(
        "<b>Dependency Audit Note:</b> All listed libraries are actively imported and invoked across the scripts in <code>etl/</code>, "
        "<code>dashboard/</code>, and <code>notebooks/</code>. No extraneous or unverified dependencies have been included in this technical review.",
        title="Verified Dependency Scope", color=SECONDARY, styles=styles
    ))
    
    elements.append(PageBreak())
    return elements
