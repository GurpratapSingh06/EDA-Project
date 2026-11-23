"""
Pages 15 to 16:
- Page 15: Section 10: Project Implementation Mapping (Master Concept-to-File Catalog).
- Page 16: Section 11: Important Formulas & Worked Numerical Examples (Mathematical Formulations & Numbers).
"""

from reportlab.platypus import Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from .config_18 import (
    USABLE_WIDTH, PRIMARY, SECONDARY, ACCENT, DARK_TEXT, LIGHT_BG, ALT_ROW_BG,
    BORDER_COLOR, MUTED_TEXT, make_callout, make_table, make_image_figure, PageTracker
)

def build_pages_15_16(styles, tracker):
    elements = []
    
    # =========================================================================
    # PAGE 15: PROJECT IMPLEMENTATION MAPPING (SECTION 10)
    # =========================================================================
    elements.append(PageTracker('sec10_page', tracker))
    elements.append(Paragraph("<b>Section 10: Project Implementation Mapping</b>", styles['SectionH1']))
    
    elements.append(Paragraph(
        "<b>10.1 Master Concept-to-Implementation Cross-Reference Catalog</b><br/>"
        "This master table indexes all 31 core technical concepts, database patterns, and machine learning algorithms implemented in the Chicago "
        "Crime Analytics project, linking each directly to its exact repository source file, line number interval, and empirical output artifact:",
        styles['Body']
    ))
    elements.append(Spacer(1, 2))
    
    mapping_matrix = [
        ["#", "Technical Concept / Technique", "How It Is Implemented in Project", "Exact Repository Source File", "Line Ref / Output Artifact"],
        ["1", "Socrata SoQL API Ingestion", "Fetches 50k-row JSON chunks with rate limiting", "<code>etl/extract.py</code>", "Lines 45–110; <code>data/raw/</code>"],
        ["2", "Zero-Loss Curation (&Delta;=0)", "Retains 100% of 497,919 rows via -1/'UNKNOWN'", "<code>etl/curate.py</code>", "Lines 80–150; <code>crimes_curated.csv</code>"],
        ["3", "Temporal Decomposition", "Derives 11 calendar and 4 shift band features", "<code>etl/curate.py</code>", "Lines 190–215; <code>docs/data_dict.md</code>"],
        ["4", "Hierarchical Categorical Binning", "Maps 31 types to 5 classes; 134 premises to 6 groups", "<code>etl/curate.py</code>", "Lines 23–78; <code>crimes_curated.csv</code>"],
        ["5", "Quantile Spatial Risk Banding", "Computes Q1–Q4 risk tiers across 77 areas", "<code>etl/curate.py</code>", "Lines 220–285; <code>dw.DimLocation</code>"],
        ["6", "Transient Staging Layer", "Decouples landing heap from dimensional joins", "<code>sql/01_staging.sql</code>", "Lines 6–35; <code>staging.stg_crimes</code>"],
        ["7", "High-Speed Bulk COPY", "Streams in-memory TSV buffer to heap (34k rows/s)", "<code>etl/load_initial.py</code>", "Lines 127–145; 190x speedup"],
        ["8", "Incremental Micro-Batching", "Appends Dec 2025 delta (17,609 rows) non-destructively", "<code>etl/load_incremental.py</code>", "Lines 70–220; <code>incremental_load.md</code>"],
        ["9", "Fact Constellation Schema", "Dual-grain facts (Atomic 497k rows vs Daily 54k rows)", "<code>sql/03_facts.sql</code>", "Lines 8–52; <code>dw.Fact*</code>"],
        ["10", "Conformed Dimensions", "Shared analytical bus across DimDate, DimLocation", "<code>sql/02_dims.sql</code>", "Lines 7–125; <code>dw.Dim*</code>"],
        ["11", "Surrogate Key Optimization", "Compact 4-byte INT keys replacing 40-byte natural UUIDs", "<code>sql/02_dims.sql</code>", "Lines 15–120; 10x memory saving"],
        ["12", "Degenerate Dimensions", "IncidentID &amp; CaseNumber stored directly in fact", "<code>sql/03_facts.sql</code>", "Lines 19–20; zero join overhead"],
        ["13", "Junk Dimension (Context)", "Compresses 3 boolean flags into 8 combo rows + 1 unk", "<code>sql/02_dims.sql</code>", "Lines 100–125; <code>DimIncidentContext</code>"],
        ["14", "Unknown Member (-1) Pattern", "Pre-seeds -1 key to eliminate NULL FK outer-join loss", "<code>sql/02_dims.sql</code>", "Lines 25, 43, 63, 94; 0 NULL FKs"],
        ["15", "Certified Analytics Mart View", "Standardized SQL abstraction for BI &amp; Scikit-Learn", "<code>sql/06_mart_view.sql</code>", "Lines 7–50; <code>mart.PublicSafety*</code>"],
        ["16", "Secondary B-Tree Indexing", "17 strategic indexes accelerating slices by up to 6.3x", "<code>sql/04_indexes.sql</code>", "Lines 6–45; <code>indexing_report.md</code>"],
        ["17", "OLAP Roll-Up &amp; Drill-Down", "Hierarchical aggregation (Year/Qtr/Mo) &amp; holiday peak", "<code>sql/05_olap_queries.sql</code>", "Lines 8–34; <code>olap_doc.md</code>"],
        ["18", "OLAP Slice &amp; Dice", "Single-district slice (011) &amp; high-violence multi-dice", "<code>sql/05_olap_queries.sql</code>", "Lines 36–66; <code>query_timings.csv</code>"],
        ["19", "OLAP Pivot Matrix (24x7)", "Conditional aggregation matrix across hours and days", "<code>sql/05_olap_queries.sql</code>", "Lines 68–83; <code>fig05_heatmap.png</code>"],
        ["20", "CUBE &amp; GROUPING SETS", "Simultaneous multi-grain aggregation across 8 cuboids", "<code>sql/05_olap_queries.sql</code>", "Lines 85–104; 281ms single pass"],
        ["21", "OLS Multiple Regression", "Baseline parametric model on backward lags", "<code>etl/run_ml_models.py</code>", "Lines 55–95; $R^2=0.7799$"],
        ["22", "Ridge Regularization (L2)", "Champion regression model shrinking collinear area weights", "<code>etl/run_ml_models.py</code>", "Lines 100–140; $R^2=0.7826, \\text{RMSE}=3.42$"],
        ["23", "VIF Multicollinearity Check", "Mathematically proves feature independence (VIF &lt; 3.2)", "<code>etl/run_ml_models.py</code>", "Lines 145–165; <code>vif_analysis.csv</code>"],
        ["24", "Apriori Association Mining", "Level-wise candidate generation across 497k transactions", "<code>etl/run_ml_models.py</code>", "Lines 180–215; 3.97s runtime"],
        ["25", "FP-Growth Association Mining", "Prefix-tree mining; 1.7x faster than Apriori", "<code>etl/run_ml_models.py</code>", "Lines 220–270; 2.35s runtime"],
        ["26", "CART Decision Tree", "Classifies arrest clearance with Gini impurity", "<code>etl/run_ml_models.py</code>", "Lines 280–330; <code>fig12_tree.png</code>"],
        ["27", "Cost-Sensitive Balancing", "class_weight='balanced' boosts recall to 55.59%", "<code>etl/run_ml_models.py</code>", "Line 335; $\\text{AUC}=0.7392$"],
        ["28", "Minimal CCP Tree Pruning", "Prunes tree to max_depth=5 to eliminate noise", "<code>etl/run_ml_models.py</code>", "Lines 340–355; 24 robust leaves"],
        ["29", "Streamlit BI Web App", "4-page dual-engine app with CSV fallback resilience", "<code>dashboard/app.py</code>", "Lines 40–350; live port 8501"],
        ["30", "Power BI Semantic Model", "PBIP model with 8 certified DAX measures", "<code>powerbi/model.bim</code>", "Tables, measures, and relationships"],
        ["31", "Reconciliation Auditing", "Automated SQL audit proving 100% row/measure conservation", "<code>etl/validate.py</code>", "Lines 20–120; <code>validation_report.md</code>"]
    ]
    elements.append(make_table(
        mapping_matrix,
        col_widths=[16, 115, 155, 115, USABLE_WIDTH - 401],
        headers=True,
        styles=styles,
        padding=1.8,
        cell_style=styles['MapCell'],
        header_style=styles['MapCellHeader']
    ))
    
    elements.append(PageBreak())
    
    # =========================================================================
    # PAGE 16: IMPORTANT FORMULAS & WORKED EXAMPLES (SECTION 11)
    # =========================================================================
    elements.append(PageTracker('sec11_page', tracker))
    elements.append(Paragraph("<b>Section 11: Important Formulas and Worked Numerical Examples</b>", styles['SectionH1']))
    
    elements.append(Paragraph(
        "<b>11.1 Mathematical Formulations, Derivations &amp; Concrete Project Calculations</b><br/>"
        "This section documents the formal mathematical foundations and exact numerical calculations implemented across the project's "
        "data engineering and machine learning pipelines:",
        styles['Body']
    ))
    elements.append(Spacer(1, 4))
    
    formulas_data = [
        ["#", "Mathematical Concept", "Formal Equation / Derivation", "Variables &amp; Operational Definition", "Concrete Chicago Project Worked Example"],
        ["1", "OLS Normal Equation", "$\\hat{\\beta} = (X^T X)^{-1} X^T y$", "$X$: Design matrix of lags &amp; dummies; $y$: actual daily count; $\\hat{\\beta}$: estimated weights.", "For Area 25 (Austin) on July Saturday: $\\hat{y} = 0.85 + 0.32(10) + 0.54(12) + 1.15(Wknd) = \\mathbf{12.13}$ daily incidents."],
        ["2", "Ridge L2 Regularization", "$\\hat{\\beta}_{\\text{Ridge}} = (X^T X + \\alpha I)^{-1} X^T y$", "$\\alpha=10.0$: Regularization parameter penalizing large weights to prevent overfitting.", "Shrinks collinear lag_1 coefficient from 0.38 to 0.29, boosting test $R^2$ to <b>0.7826</b> and reducing RMSE to <b>3.425</b>."],
        ["3", "Variance Inflation Factor", "$\\text{VIF}_j = \\frac{1}{1 - R_j^2}$", "$R_j^2$: Coefficient of determination from regressing feature $X_j$ against remaining predictors.", "For lag_1_day: $R^2 = 0.648 \\implies \\text{VIF} = 1 / (1 - 0.648) = \\mathbf{2.84}$ (Safely below 5.0 multicollinearity limit)."],
        ["4", "Gini Impurity (CART)", "$I_G(t) = 1 - \\sum_{i=0}^1 p_i^2$", "$p_i$: Proportion of samples belonging to class $i$ (Arrest vs No Arrest) at tree node $t$.", "Root node (14.94% arrests): $I_G = 1 - (0.8506^2 + 0.1494^2) = \\mathbf{0.2542}$. Splitting on Narcotics isolates $I_G = 0.0679$."],
        ["5", "Gini Gain (Split Criterion)", "$\\Delta I_G = I_G(p) - \\sum \\frac{N_c}{N} I_G(c)$", "$I_G(p)$: Parent node impurity; $N_c$: Child node sample count; $I_G(c)$: Child impurity.", "Splitting 373,439 training samples on PrimaryType_NARCOTICS yields maximum Gini Gain, forming root split in CART tree."],
        ["6", "Balanced Sample Weights", "$w_j = \\frac{N}{K \\cdot N_j}$", "$N$: Total samples (373,439); $K$: Class count (2); $N_j$: Frequency of class $j$.", "Minority Arrest weight: $w_1 = 373,439 / (2 \\times 55,797) = \\mathbf{3.35}$; Majority No Arrest weight: $w_0 = \\mathbf{0.59}$."],
        ["7", "Cost-Complexity Pruning", "$R_\\alpha(T) = R(T) + \\alpha |T|$", "$R(T)$: Training misclassification cost; $|T|$: Number of terminal leaf nodes; $\\alpha$: penalty.", "Pruning at $\\text{max\\_depth}=5$ collapsed 1,280 noisy leaves into 24 robust evidentiary leaves, optimizing test generalization."],
        ["8", "Association Rule Support", "$\\text{Supp}(X \\to Y) = \\frac{\\sigma(X \\cup Y)}{N}$", "$\\sigma(X \\cup Y)$: Count of transactions containing both $X$ and $Y$; $N = 497,919$.", "Street Narcotics with Arrest: 10,854 transactions / 497,919 = <b>0.0218 (2.18% Support)</b>."],
        ["9", "Association Rule Confidence", "$\\text{Conf}(X \\to Y) = \\frac{\\text{Supp}(X \\cup Y)}{\\text{Supp}(X)}$", "Conditional probability $P(Y \\mid X)$ that transaction contains $Y$ given it contains $X$.", "$\\text{Conf}(\\text{Street Narcotics} \\to \\text{Arrest}) = 0.0218 / 0.0224 = \\mathbf{97.34\\%}$ (Near-deterministic arrest likelihood)."],
        ["10", "Association Rule Lift", "$\\text{Lift}(X \\to Y) = \\frac{\\text{Conf}(X \\to Y)}{\\text{Supp}(Y)}$", "Ratio of observed rule joint probability to expected probability under independence.", "$\\text{Lift} = 0.9734 / 0.1494 = \\mathbf{6.52}$ (Street narcotics presence increases arrest probability by 6.5x over baseline)."],
        ["11", "Bulk Ingestion Speedup", "$S = \\frac{T_{\\text{INSERT}}}{T_{\\text{COPY}}}$", "$T_{\\text{INSERT}}$: Standard SQL multi-row insert time; $T_{\\text{COPY}}$: Streaming COPY time.", "$S = 2,700\\text{ s} / 14.18\\text{ s} = \\mathbf{190.4x}$ throughput increase (from 184 rows/s to 33,870 rows/s)."]
    ]
    elements.append(make_table(formulas_data, col_widths=[14, 95, 115, 120, USABLE_WIDTH - 344], headers=True, styles=styles, padding=4.2))
    
    elements.append(PageBreak())
    return elements
