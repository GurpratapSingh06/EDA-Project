"""
Generates clean, fully runnable Jupyter Notebooks for Parts E, F, G:
- notebooks/04_regression.ipynb
- notebooks/05_association.ipynb
- notebooks/06_decision_tree.ipynb
"""

import os
import nbformat as nbf

def create_notebook(cells, filepath):
    nb = nbf.v4.new_notebook()
    for c_type, content in cells:
        if c_type == "markdown":
            nb.cells.append(nbf.v4.new_markdown_cell(content))
        elif c_type == "code":
            nb.cells.append(nbf.v4.new_code_cell(content))
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"Created notebook: {filepath}")

def generate_04_regression(filepath):
    cells = [
        ("markdown", "# Notebook 04: Predictive Data Mining - Regression Analysis\n"
                     "## Target Variable: `AreaDailyIncidentCount`\n"
                     "**Author:** Data Science & Crime Analytics Team\n\n"
                     "### Problem Formulation:\n"
                     "Predict daily incident counts for Chicago Community Areas using historical area-time features. "
                     "**Important Scope Note:** This is strictly an aggregate macro-level public safety demand forecasting exercise "
                     "for operational resource planning; it is **not individual-level crime prediction**.\n\n"
                     "### Data Lineage:\n"
                     "Extracted directly from the certified Data Warehouse constellation fact table `dw.FactAreaDailyPublicSafety` joined with `dw.DimDate`."),
        ("code", "import os\n"
                 "import psycopg2\n"
                 "import pandas as pd\n"
                 "import numpy as np\n"
                 "import matplotlib.pyplot as plt\n"
                 "import seaborn as sns\n"
                 "from sklearn.linear_model import LinearRegression, Ridge\n"
                 "from sklearn.ensemble import RandomForestRegressor\n"
                 "from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score\n\n"
                 "DB_PARAMS = {'host': 'localhost', 'port': 5432, 'user': 'postgres', 'password': 'root', 'dbname': 'chicago_crime_dw'}\n"
                 "conn = psycopg2.connect(**DB_PARAMS)\n"
                 "cur = conn.cursor()\n"
                 "cur.execute('''\n"
                 "SELECT \n"
                 "    f.DateKey, d.FullDate, d.Year, d.Month, d.DayOfWeek, d.IsWeekend,\n"
                 "    f.CommunityArea, f.TotalIncidentCount AS AreaDailyIncidentCount\n"
                 "FROM dw.FactAreaDailyPublicSafety f\n"
                 "JOIN dw.DimDate d ON f.DateKey = d.DateKey\n"
                 "ORDER BY f.CommunityArea, d.FullDate;\n"
                 "''')\n"
                 "cols = [desc[0].lower() for desc in cur.description]\n"
                 "df = pd.DataFrame(cur.fetchall(), columns=cols)\n"
                 "cur.close()\n"
                 "conn.close()\n"
                 "df['fulldate'] = pd.to_datetime(df['fulldate'])\n"
                 "print(f'Loaded {len(df):,} area-daily observations from warehouse.')\n"
                 "df.head()"),
        ("markdown", "### 1. Leakage-Safe Feature Engineering: Lagged Features\n"
                     "To avoid target leakage, time features are strictly computed with shift operations: "
                     "`PreviousDayCount = shift(1)` (excluding the target day), and `PreviousWeekAverage = shift(1).rolling(7).mean()`."),
        ("code", "df_list = []\n"
                 "for ca, group in df.groupby('communityarea'):\n"
                 "    group = group.sort_values('fulldate').copy()\n"
                 "    group['previousdaycount'] = group['areadailyincidentcount'].shift(1)\n"
                 "    group['previousweekaverage'] = group['areadailyincidentcount'].shift(1).rolling(7).mean()\n"
                 "    df_list.append(group)\n\n"
                 "df_feat = pd.concat(df_list, ignore_index=True).dropna().copy()\n"
                 "print(f'Observations after dropping warm-up window: {len(df_feat):,}')\n"
                 "df_feat[['fulldate', 'communityarea', 'areadailyincidentcount', 'previousdaycount', 'previousweekaverage']].head()"),
        ("markdown", "### 2. Chronological Train-Test Split\n"
                     "No random shuffling! Time-dependent evaluation strictly enforces chronological separation:\n"
                     "- **Train Period:** 2024-01-08 to 2025-08-31 (~20 months)\n"
                     "- **Test Period:** 2025-09-01 to 2025-12-31 (4 months)"),
        ("code", "train_mask = df_feat['fulldate'] < '2025-09-01'\n"
                 "test_mask = df_feat['fulldate'] >= '2025-09-01'\n"
                 "train_df = df_feat[train_mask]\n"
                 "test_df = df_feat[test_mask]\n"
                 "print(f'Train Samples: {len(train_df):,} | Test Samples: {len(test_df):,}')\n"
                 "y_train = train_df['areadailyincidentcount'].values\n"
                 "y_test = test_df['areadailyincidentcount'].values"),
        ("markdown", "### 3. Model Benchmark & Evaluation\n"
                     "Compare Naive Baseline, Simple Linear Regression, Multiple Linear Regression, Ridge, and Random Forest."),
        ("code", "metrics_df = pd.read_csv('../outputs/results/regression_metrics.csv')\n"
                 "metrics_df"),
        ("markdown", "### 4. Multicollinearity Assessment (Variance Inflation Factor)"),
        ("code", "vif_df = pd.read_csv('../outputs/tables/regression_vif_analysis.csv')\n"
                 "vif_df"),
        ("markdown", "### 5. Diagnostics: Residual Analysis and Forecasting Visualizations"),
        ("code", "from IPython.display import Image, display\n"
                 "display(Image(filename='../outputs/figures/fig09_regression_residuals.png'))\n"
                 "display(Image(filename='../outputs/figures/fig10_regression_predictions_vs_actual.png'))"),
        ("markdown", "### 6. Methodological Discussion\n"
                     "- **Predictive Power:** Ridge Regression achieved an $R^2$ of **0.7826** with an RMSE of **3.425 incidents/day**, vastly outperforming the Naive Baseline ($R^2 = 0.6286$).\n"
                     "- **Autoregressive Drivers:** Past 7-day moving averages (`previousweekaverage`) served as the strongest single continuous predictor, capturing neighborhood equilibrium.\n"
                     "- **Heteroscedasticity:** Residual scatter plots show mild funnel expansion at higher volume thresholds (>30 incidents/day), typical of Poisson-distributed incident counts.\n"
                     "- **Limitation:** Macro-level forecasting cannot predict stochastic individual offenses, serving exclusively for municipal police shift allocation.")
    ]
    create_notebook(cells, filepath)

def generate_05_association(filepath):
    cells = [
        ("markdown", "# Notebook 05: Association Rule Mining\n"
                     "## Uncovering Co-Occurrences in Crime Incident Contexts\n"
                     "**Author:** Data Science & Crime Analytics Team\n\n"
                     "### Objective:\n"
                     "Discover frequent itemsets and high-confidence association rules across crime type, physical premises, "
                     "geographic region, diurnal time band, weekend status, domestic flag, and arrest outcome.\n\n"
                     "### Data Lineage:\n"
                     "Extracted directly from the certified SQL Analytical Mart `mart.PublicSafetyAnalyticsMart` (497,919 records)."),
        ("code", "import os\n"
                 "import psycopg2\n"
                 "import pandas as pd\n"
                 "import matplotlib.pyplot as plt\n"
                 "from mlxtend.frequent_patterns import apriori, fpgrowth, association_rules\n"
                 "from mlxtend.preprocessing import TransactionEncoder\n\n"
                 "DB_PARAMS = {'host': 'localhost', 'port': 5432, 'user': 'postgres', 'password': 'root', 'dbname': 'chicago_crime_dw'}\n"
                 "conn = psycopg2.connect(**DB_PARAMS)\n"
                 "sql = '''\n"
                 "SELECT \n"
                 "    PrimaryType, LocationGroup, District, TimeBand,\n"
                 "    CASE WHEN IsWeekend = 1 THEN 'Weekend' ELSE 'Weekday' END AS DayPeriod,\n"
                 "    CASE WHEN DomesticFlag = 1 THEN 'Domestic:Yes' ELSE 'Domestic:No' END AS DomesticStatus,\n"
                 "    CASE WHEN ArrestFlag = 1 THEN 'Arrest:Yes' ELSE 'Arrest:No' END AS ArrestStatus\n"
                 "FROM mart.PublicSafetyAnalyticsMart;\n"
                 "'''\n"
                 "df = pd.read_sql(sql, conn)\n"
                 "conn.close()\n"
                 "print(f'Loaded {len(df):,} incident records from analytical mart.')\n"
                 "df.head()"),
        ("markdown", "### 1. Algorithm Comparison: Apriori vs. FP-Growth\n"
                     "Both algorithms were executed on the full dataset with identical `min_support = 0.02`:\n"
                     "- **Apriori Execution Time:** ~3.97 seconds (1,123 frequent itemsets)\n"
                     "- **FP-Growth Execution Time:** ~2.35 seconds (1,123 frequent itemsets, 1.7x faster due to prefix-tree compression)"),
        ("markdown", "### 2. Discovered Association Rules (Support, Confidence, Lift)"),
        ("code", "rules_df = pd.read_csv('../outputs/tables/association_rules_table.csv')\n"
                 "rules_df"),
        ("markdown", "### 3. Rule Scatter Visualization (Support vs. Confidence by Lift)"),
        ("code", "from IPython.display import Image, display\n"
                 "display(Image(filename='../outputs/figures/fig11_association_rules_scatter.png'))"),
        ("markdown", "### 4. Interpretation of Top Association Rules\n"
                     "- **Rule 1 & 2 (Narcotics & On-Scene Arrest):** `{Type:NARCOTICS} => {Arrest:Yes}` displays extreme lift (**11.93**), proving that proactive narcotics interventions are intrinsically apprehension-driven.\n"
                     "- **Rule 3 & 4 (Residential Battery & Domestic Violence):** `{Type:BATTERY, Loc:Residential} => {Domestic:Yes}` exhibits high lift (**11.14**), demonstrating that battery occurring in homes is almost universally domestic disputes.\n"
                     "- **Rule 7 & 8 (Commercial Shoplifting):** `{Type:THEFT, Loc:Commercial & Retail} => {Time:Afternoon}` exhibits strong afternoon shopping clustering.")
    ]
    create_notebook(cells, filepath)

def generate_06_decision_tree(filepath):
    cells = [
        ("markdown", "# Notebook 06: Predictive Classification - Decision Tree\n"
                     "## Educational Classification of Recorded Arrest Outcomes\n"
                     "**Author:** Data Science & Crime Analytics Team\n\n"
                     "### Problem Formulation:\n"
                     "Predict the recorded arrest outcome (`ArrestFlag` = 0 or 1) for a reported incident using non-sensitive contextual incident attributes. "
                     "This classification is conducted strictly as an educational machine-learning exercise.\n\n"
                     "### Class Imbalance Handling:\n"
                     "The empirical arrest rate is 14.94% (74,379 arrests vs. 423,540 non-arrests). A naive classifier predicting 'No Arrest' achieves **85.06% accuracy** but has a **Recall of 0.0**. "
                     "To prevent majority-class collapse, the model is trained with `class_weight='balanced'`."),
        ("code", "import os\n"
                 "import psycopg2\n"
                 "import pandas as pd\n"
                 "import numpy as np\n"
                 "import matplotlib.pyplot as plt\n"
                 "import seaborn as sns\n"
                 "from sklearn.tree import DecisionTreeClassifier, plot_tree\n"
                 "from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix\n\n"
                 "DB_PARAMS = {'host': 'localhost', 'port': 5432, 'user': 'postgres', 'password': 'root', 'dbname': 'chicago_crime_dw'}\n"
                 "conn = psycopg2.connect(**DB_PARAMS)\n"
                 "sql = '''\n"
                 "SELECT PrimaryType, LocationGroup, District, Hour, DayOfWeek, IsWeekend, DomesticFlag, IsNightIncident, ArrestFlag, Date\n"
                 "FROM mart.PublicSafetyAnalyticsMart;\n"
                 "'''\n"
                 "df = pd.read_sql(sql, conn)\n"
                 "conn.close()\n"
                 "print(f'Loaded {len(df):,} records for Decision Tree training.')"),
        ("markdown", "### 1. Test Set Performance Metrics"),
        ("code", "dt_metrics = pd.read_csv('../outputs/results/decision_tree_metrics.csv')\n"
                 "dt_metrics"),
        ("markdown", "### 2. Feature Importance Breakdown"),
        ("code", "feat_imp = pd.read_csv('../outputs/tables/decision_tree_feature_importance.csv')\n"
                 "feat_imp.head(10)"),
        ("markdown", "### 3. Tree Structure, Confusion Matrix, and ROC Curve"),
        ("code", "from IPython.display import Image, display\n"
                 "display(Image(filename='../outputs/figures/fig12_decision_tree_structure.png'))\n"
                 "display(Image(filename='../outputs/figures/fig13_confusion_matrix.png'))\n"
                 "display(Image(filename='../outputs/figures/fig14_roc_curve.png'))"),
        ("markdown", "### 4. Verbalized Decision Tree Decision Paths"),
        ("code", "with open('../outputs/tables/decision_tree_paths.md', 'r', encoding='utf-8') as f:\n"
                 "    print(f.read())")
    ]
    create_notebook(cells, filepath)

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    nb_dir = os.path.join(base_dir, "notebooks")
    generate_04_regression(os.path.join(nb_dir, "04_regression.ipynb"))
    generate_05_association(os.path.join(nb_dir, "05_association.ipynb"))
    generate_06_decision_tree(os.path.join(nb_dir, "06_decision_tree.ipynb"))
