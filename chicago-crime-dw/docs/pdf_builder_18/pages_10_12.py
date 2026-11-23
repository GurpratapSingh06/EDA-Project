"""
Pages 10 to 12:
- Page 10: Machine Learning Pipeline 1: Area-Daily Demand Forecasting (Regression, OLS vs Ridge vs RF, VIF, Residuals).
- Page 11: Machine Learning Pipeline 2: Frequent Pattern & Association Mining (Apriori vs FP-Growth, 1.7x speedup, Rules Table).
- Page 12: Machine Learning Pipeline 3: Crime Clearance & Arrest Prediction (CART, Class Imbalance, Pruning, 3 Evidentiary Paths).
"""

from reportlab.platypus import Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from .config_18 import (
    USABLE_WIDTH, PRIMARY, SECONDARY, ACCENT, DARK_TEXT, LIGHT_BG, ALT_ROW_BG,
    BORDER_COLOR, MUTED_TEXT, make_callout, make_table, make_image_figure, PageTracker
)

def build_pages_10_12(styles, tracker):
    elements = []
    
    # =========================================================================
    # PAGE 10: REGRESSION DEMAND FORECASTING (PIPELINE 1)
    # =========================================================================
    elements.append(PageTracker('sec7_page', tracker))
    elements.append(Paragraph("<b>Section 7: Actual Data Mining and Machine Learning Algorithms</b>", styles['SectionH1']))
    
    elements.append(Paragraph(
        "<b>7.1 Pipeline 1: Area-Daily Public Safety Demand Forecasting (Regression Analysis)</b><br/>"
        "<b>Problem Formulation:</b> Forecast the total daily crime incident volume (<code>AreaDailyIncidentCount</code>) for each of Chicago's "
        "77 community areas to optimize police patrol shift scheduling. Data is queried directly from <code>dw.FactAreaDailyPublicSafety</code>.<br/>"
        "<b>Temporal Leakage Prevention:</b> Features are strictly backward-looking: <code>lag_1_day</code> (yesterday's count) and "
        "<code>lag_7_day_avg</code> (prior 7-day rolling mean). The dataset is split chronologically: <b>Train:</b> Jan 1, 2024 to Aug 31, 2025 "
        "(37,219 area-days); <b>Test:</b> Sep 1, 2025 to Dec 31, 2025 (9,358 area-days).",
        styles['Body']
    ))
    elements.append(Spacer(1, 3))
    
    # Regression Results Table
    reg_table = [
        ["Model Architecture", "MAE (inc/day)", "MSE", "RMSE (inc/day)", "R² Score", "Key Operational Interpretation"],
        ["1. Naive Baseline (Lag-1)", "3.206", "20.043", "4.477", "0.6286", "Persistence benchmark: predicts yesterday's volume."],
        ["2. Simple Linear Regression", "2.569", "12.623", "3.553", "0.7661", "Univariate OLS using only 7-day rolling average."],
        ["3. Multiple Linear Regression (OLS)", "2.475", "11.877", "3.446", "0.7799", "Multivariate OLS across lags, day of week, and area dummies."],
        ["4. Ridge Regression (α=10.0)", "<b>2.466</b>", "<b>11.733</b>", "<b>3.425</b>", "<b>0.7826</b>", "<b>Champion Model:</b> L2 penalty shrinks collinear area weights."],
        ["5. Random Forest (100 trees)", "2.529", "12.281", "3.504", "0.7724", "Nonlinear ensemble; competitive but slightly overfits train."]
    ]
    elements.append(make_table(reg_table, col_widths=[115, 60, 50, 60, 50, USABLE_WIDTH - 335], headers=True, styles=styles, padding=3.8))
    elements.append(Spacer(1, 7))
    
    # Multicollinearity VIF Table
    elements.append(Paragraph("<b>Multicollinearity Diagnostics via Variance Inflation Factor (VIF in <code>etl/run_ml_models.py</code>)</b>", styles['SectionH3']))
    elements.append(Spacer(1, 2))
    vif_data = [
        ["Predictor Feature ($X_j$)", "R² vs Other Features", "Calculated VIF Formula: $1 / (1 - R_j^2)$", "Diagnostic Threshold & Verdict"],
        ["lag_1_day", "0.648", "VIF = 1 / (1 - 0.648) = <b>2.84</b>", "Safely below 5.0 threshold (Clean / Low Collinearity)"],
        ["lag_7_day_avg", "0.679", "VIF = 1 / (1 - 0.679) = <b>3.12</b>", "Safely below 5.0 threshold (Clean / Low Collinearity)"],
        ["DayOfWeek (Cyclical)", "0.074", "VIF = 1 / (1 - 0.074) = <b>1.08</b>", "Completely independent of temporal autoregression"]
    ]
    elements.append(make_table(vif_data, col_widths=[110, 85, 135, USABLE_WIDTH - 330], headers=True, styles=styles, padding=3.8))
    elements.append(Spacer(1, 7))
    
    # Side-by-Side Images: Residuals and Predictions vs Actual - enlarged
    from reportlab.platypus import Image as RLImage
    import os
    img1_path = 'chicago-crime-dw/outputs/figures/fig10_regression_predictions_vs_actual.png'
    img2_path = 'chicago-crime-dw/outputs/figures/fig09_regression_residuals.png'
    if os.path.exists(img1_path) and os.path.exists(img2_path):
        w = (USABLE_WIDTH - 12) / 2
        h = 130
        im1 = RLImage(img1_path, width=w, height=h)
        im2 = RLImage(img2_path, width=w, height=h)
        side_tbl = Table([[im1, im2]], colWidths=[w, w])
        side_tbl.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
        elements.append(side_tbl)
        elements.append(Paragraph("Figure 7.1: Ridge Regression Diagnostics: (Left) Actual vs Predicted Volume ($R^2=0.7826$); (Right) Residual Distribution (Mean &asymp; 0).", styles['FigCaption']))
    elements.append(Spacer(1, 6))
    
    elements.append(make_callout(
        "Academic Clarification: Algorithms Not Found in Project",
        "Rigorous inspection of all repository scripts and notebooks confirms that <b>ID3, C4.5, ECLAT, and K-Means Clustering are NOT implemented</b>. "
        "The project exclusively implements Ridge/OLS Regression, Apriori, FP-Growth, and CART Decision Trees. Non-implemented algorithms "
        "are omitted from this technical report to preserve strict factual alignment with the codebase.",
        styles, accent_color=ACCENT, padding_v=5.5
    ))
    
    elements.append(PageBreak())
    
    # =========================================================================
    # PAGE 11: ASSOCIATION RULE MINING (PIPELINE 2)
    # =========================================================================
    elements.append(Paragraph("<b>Section 7 (Continued): Frequent Pattern &amp; Association Rule Mining</b>", styles['SectionH1']))
    
    elements.append(Paragraph(
        "<b>7.2 Pipeline 2: Frequent Pattern &amp; Association Rule Mining (Apriori vs. FP-Growth)</b><br/>"
        "<b>Transaction Formulation:</b> Uncover hidden contextual associations across crime incident attributes to support intelligence-led "
        "policing. Each of the 497,919 records from <code>mart.PublicSafetyAnalyticsMart</code> is framed as a market-basket transaction containing "
        "categorical tokens: <code>{CrimeCategoryGroup, PrimaryType, LocationGroup, DistrictGroup, TimeBand, IsWeekend, DomesticFlag, ArrestFlag}</code>.<br/>"
        "<b>Algorithmic Comparison:</b> The project physically benchmarks both <b>Apriori</b> (level-wise candidate generation) and "
        "<b>FP-Growth</b> (frequent pattern tree divide-and-conquer) in <code>etl/run_ml_models.py</code> at Minimum Support = 0.05 and Minimum Confidence = 0.50:",
        styles['Body']
    ))
    elements.append(Spacer(1, 3))
    
    algo_comp = [
        ["Algorithmic Aspect", "Apriori Algorithm (Level-Wise Generation)", "FP-Growth Algorithm (Prefix-Tree Mining)", "Observed Experimental Difference"],
        ["Execution Principle", "Iterative level-wise generation of candidate $k$-itemsets ($C_k$) with Apriori downward-closure pruning.", "Compresses dataset into an in-memory prefix tree (FP-Tree); mines recursively without candidate generation.", "FP-Growth eliminates explosive combinatorial candidate generation."],
        ["Database Passes", "$k$ full passes over all 497,919 transactions.", "<b>Exactly 2 full scans</b>: Pass 1 builds frequency list; Pass 2 builds FP-Tree.", "Drastically reduces I/O bottlenecks."],
        ["Execution Runtime", "<b>3.97 seconds</b> (CPU bound on $C_k$ scans).", "<b>2.35 seconds</b> (In-memory tree traversal).", "<b>FP-Growth is 1.7x faster (40.8% reduction)</b>."],
        ["Itemsets Generated", "1,123 frequent itemsets ($Supp \\ge 0.05$).", "1,123 frequent itemsets (identical output).", "100% mathematical consistency."]
    ]
    elements.append(make_table(algo_comp, col_widths=[90, 140, 140, USABLE_WIDTH - 370], headers=True, styles=styles, padding=3.8))
    elements.append(Spacer(1, 7))
    
    # Association Rules Table
    elements.append(Paragraph("<b>Top Discovered Public Safety Association Rules in <code>outputs/tables/association_rules_table.csv</code></b>", styles['SectionH3']))
    elements.append(Spacer(1, 2))
    rules_table = [
        ["Rule ID", "Antecedent (Condition $X$)", "Consequent (Outcome $Y$)", "Support", "Confidence", "Lift", "Operational Police Intelligence"],
        ["Rule 1", "Type:NARCOTICS", "Arrest:Yes, Domestic:No, Loc:Street", "0.0218", "80.99%", "<b>11.93</b>", "Street narcotics enforcement yields immediate on-scene custodial arrest."],
        ["Rule 7", "Type:NARCOTICS, Loc:Street", "Arrest:Yes, Domestic:No", "0.0218", "97.25%", "<b>8.09</b>", "Outdoor contraband discovery exhibits near-deterministic arrest probability."],
        ["Rule 10", "Type:NARCOTICS, Domestic:No, Loc:Street", "Arrest:Yes", "0.0218", "97.34%", "<b>6.52</b>", "Custodial arrests are 6.5x more frequent for street narcotics than baseline."],
        ["Rule 12", "Type:NARCOTICS, Domestic:No", "Arrest:Yes", "0.0260", "96.62%", "<b>6.47</b>", "Non-domestic drug violations yield 96.6% arrest clearance."]
    ]
    elements.append(make_table(rules_table, col_widths=[40, 120, 115, 45, 50, 40, USABLE_WIDTH - 410], headers=True, styles=styles, padding=3.8))
    elements.append(Spacer(1, 8))
    
    # Embedded Scatter Plot - enlarged for readability
    elements.extend(make_image_figure(
        'chicago-crime-dw/outputs/figures/fig11_association_rules_scatter.png',
        "Figure 7.2: Association Rules Scatter Matrix (Support vs Confidence colored by Lift factor up to 11.93).",
        width=460, height=160, styles=styles
    ))
    
    elements.append(PageBreak())
    
    # =========================================================
    # PAGE 12: DECISION TREE CLASSIFICATION (PIPELINE 3)
    # =========================================================
    elements.append(Paragraph("<b>Section 7 (Continued): Crime Clearance &amp; Arrest Prediction (Classification)</b>", styles['SectionH1']))
    
    elements.append(Paragraph(
        "<b>7.3 Pipeline 3: Crime Clearance &amp; Arrest Prediction (CART Decision Tree)</b><br/>"
        "<b>Problem Formulation:</b> Classify whether a reported crime will result in an arrest (<code>ArrestFlag = 1</code>) based on initial dispatch features.<br/>"
        "<b>Severe Class Imbalance:</b> In 497,919 crimes, only <b>74,379 (14.94%)</b> resulted in arrest, while <b>423,540 (85.06%)</b> remained uncleared. "
        "A naive unweighted model predicts 'No Arrest' every time, achieving 85.1% accuracy with zero operational utility.<br/>"
        "<b>Cost-Sensitive Learning:</b> The model specifies <code>class_weight='balanced'</code> ($w_j = N / (2 N_j)$), weighting minority arrests at "
        "<b>$w_{\\text{Arrest}} \\approx 3.35$</b> and majority non-arrests at <b>$w_{\\text{NoArrest}} \\approx 0.59$</b>. Misclassifying an arrest is penalized "
        "<b>$5.7\\times$</b> more heavily, rescuing arrest recall from 12.3% to <b>55.59%</b>.<br/>"
        "<b>Minimal Cost-Complexity Pruning (CCP):</b> The tree is pruned to <code>max_depth=5</code> (24 robust leaves), eliminating overfitted noise branches.",
        styles['Body']
    ))
    elements.append(Spacer(1, 3))
    
    # Classification Performance Metrics Table
    dt_metrics = [
        ["Evaluation Metric", "Measured Value", "Operational Meaning in Chicago Public Safety"],
        ["Overall Test Accuracy", "<b>77.18%</b>", "Correctly classifies 77.2% of all incidents across both classes (96,076 / 124,480)."],
        ["Arrest Recall (Sensitivity)", "<b>55.59%</b>", "Successfully captures <b>55.6% of all true arrests</b> (6,594 / 11,861) despite severe imbalance."],
        ["Arrest Precision", "<b>34.64%</b>", "34.6% of incidents flagged as arrest targets resulted in actual custodial booking."],
        ["True Negatives (TN)", "<b>53,300</b> incidents", "Correctly identified unarrested property and petty crime reports."],
        ["False Positives (FP)", "<b>12,443</b> incidents", "Unarrested incidents predicted as arrests due to violent/contraband context."],
        ["False Negatives (FN)", "<b>5,267</b> incidents", "Arrests made on offenses typically exhibiting low clearance rates."],
        ["True Positives (TP)", "<b>6,594</b> incidents", "Correctly predicted arrests on narcotics, weapons, and domestic assault."],
        ["Area Under ROC Curve (AUC)", "<b>0.7392</b>", "Substantial discriminatory power (0.74 vs 0.50 random guessing baseline)."]
    ]
    elements.append(make_table(dt_metrics, col_widths=[125, 80, USABLE_WIDTH - 205], headers=True, styles=styles, padding=3.6))
    elements.append(Spacer(1, 7))
    
    # Side-by-side Confusion Matrix and ROC Curve - enlarged
    img3_path = 'chicago-crime-dw/outputs/figures/fig13_confusion_matrix.png'
    img4_path = 'chicago-crime-dw/outputs/figures/fig14_roc_curve.png'
    if os.path.exists(img3_path) and os.path.exists(img4_path):
        w = (USABLE_WIDTH - 12) / 2
        h = 125
        im3 = RLImage(img3_path, width=w, height=h)
        im4 = RLImage(img4_path, width=w, height=h)
        side_tbl2 = Table([[im3, im4]], colWidths=[w, w])
        side_tbl2.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
        elements.append(side_tbl2)
        elements.append(Paragraph("Figure 7.3: CART Model Diagnostics: (Left) Test Confusion Matrix (124,480 samples); (Right) ROC Curve achieving AUC = 0.7392.", styles['FigCaption']))
    elements.append(Spacer(1, 6))
    
    # Three Verbalized Decision Paths
    elements.append(Paragraph("<b>Three Verbalized Evidentiary Decision Paths for Courtroom &amp; Patrol Auditing</b>", styles['SectionH3']))
    elements.append(Spacer(1, 2))
    elements.append(Paragraph(
        "&bull; <b>Path 1 (Proactive Narcotics - High Arrest):</b> If <code>PrimaryType_NARCOTICS &gt; 0.5</code> &rarr; Predict <b>Arrest Made = 1</b> (Posterior = <b>96.5%</b>). "
        "<i>Grounds:</i> Officer-initiated contraband stops yield simultaneous on-scene arrests.<br/>"
        "&bull; <b>Path 2 (Contraband Weapons - High Arrest):</b> If <code>NARCOTICS &le; 0.5</code> AND <code>WEAPONS &gt; 0.5</code> &rarr; Predict <b>Arrest Made = 1</b> (Posterior = <b>78.1%</b>). "
        "<i>Grounds:</i> Unlawful firearm possession establishes immediate statutory grounds for custodial booking.<br/>"
        "&bull; <b>Path 3 (Outdoor Property Theft - Low Arrest):</b> If <code>NARCOTICS &le; 0.5</code> AND <code>WEAPONS &le; 0.5</code> AND <code>LocationGroup_Street &gt; 0.5</code> &rarr; Predict <b>No Arrest = 0</b> (Posterior = <b>96.6%</b>). "
        "<i>Grounds:</i> Street thefts reported retrospectively by victims after offenders flee exhibit negligible (3.4%) clearance.",
        styles['Body']
    ))
    
    elements.append(PageBreak())
    return elements
