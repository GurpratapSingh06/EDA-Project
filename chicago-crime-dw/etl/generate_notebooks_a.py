"""
Generates clean, fully runnable Jupyter Notebooks for Part A:
- notebooks/01_profiling.ipynb
- notebooks/02_curation.ipynb
- notebooks/03_eda.ipynb
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

def generate_01_profiling(filepath):
    cells = [
        ("markdown", "# Notebook 01: Chicago Crime Dataset Profiling (Pre-Cleaning)\n"
                     "## Scope: January 2024 to December 2025 Reported Incidents\n"
                     "**Author:** Data Engineering & Analytics Team\n\n"
                     "### Objective:\n"
                     "Thoroughly profile the raw Chicago Police Department crime dataset (City of Chicago Data Portal: `ijzp-q8t2`) "
                     "prior to any data cleaning or imputation. Identify missing values, duplicate records, timestamp consistency, "
                     "coordinate boundaries, and categorical code validity."),
        ("code", "import os\n"
                 "import pandas as pd\n"
                 "import numpy as np\n\n"
                 "raw_path = '../data/raw/crimes_2024_2025.csv'\n"
                 "print(f'Loading raw data from: {raw_path}')\n"
                 "df_raw = pd.read_csv(raw_path, low_memory=False)\n"
                 "print(f'Dataset Dimensions: {df_raw.shape[0]:,} rows x {df_raw.shape[1]} columns')\n"
                 "df_raw.head()"),
        ("markdown", "### 1. Attribute Data Types and Non-Null Summary"),
        ("code", "df_raw.info()"),
        ("markdown", "### 2. Missing Value Analysis"),
        ("code", "missing_counts = df_raw.isnull().sum()\n"
                 "missing_pct = (missing_counts / len(df_raw)) * 100\n"
                 "missing_summary = pd.DataFrame({'Missing_Count': missing_counts, 'Missing_Pct': missing_pct.round(4)})\n"
                 "missing_summary[missing_summary['Missing_Count'] > 0].sort_values(by='Missing_Count', ascending=False)"),
        ("markdown", "### 3. Duplicate Identification: Exact vs. Logical Duplicates"),
        ("code", "exact_dups = df_raw.duplicated().sum()\n"
                 "id_dups = df_raw.duplicated(subset=['id']).sum()\n"
                 "case_dups = df_raw.duplicated(subset=['case_number']).sum()\n"
                 "print(f'Exact Row Duplicates: {exact_dups}')\n"
                 "print(f'Duplicate Incident Primary Keys (id): {id_dups}')\n"
                 "print(f'Records Sharing CPD Case Numbers (Logical Multi-Charge Incidents): {case_dups}')"),
        ("markdown", "### 4. Timestamp and Temporal Validity"),
        ("code", "df_raw['parsed_date'] = pd.to_datetime(df_raw['date'], errors='coerce')\n"
                 "unparseable = df_raw['parsed_date'].isnull().sum()\n"
                 "min_dt = df_raw['parsed_date'].min()\n"
                 "max_dt = df_raw['parsed_date'].max()\n"
                 "out_of_bounds_date = ((df_raw['parsed_date'] < '2024-01-01') | (df_raw['parsed_date'] > '2025-12-31 23:59:59')).sum()\n"
                 "print(f'Unparseable Timestamps: {unparseable}')\n"
                 "print(f'Earliest Reported Incident: {min_dt}')\n"
                 "print(f'Latest Reported Incident: {max_dt}')\n"
                 "print(f'Incidents Outside 2024-2025 Study Window: {out_of_bounds_date}')"),
        ("markdown", "### 5. Geocoordinate Quality and Bounding Box Verification"),
        ("code", "coord_nulls = df_raw['latitude'].isnull().sum()\n"
                 "coord_zeroes = ((df_raw['latitude'] == 0) | (df_raw['longitude'] == 0)).sum()\n"
                 "valid_mask = df_raw['latitude'].notnull() & df_raw['longitude'].notnull()\n"
                 "out_of_bounds = valid_mask & ((df_raw['latitude'] < 41.60) | (df_raw['latitude'] > 42.06) | (df_raw['longitude'] < -87.95) | (df_raw['longitude'] > -87.50))\n"
                 "print(f'Missing Coordinates: {coord_nulls:,} ({coord_nulls/len(df_raw)*100:.2f}%)')\n"
                 "print(f'Coordinates at (0,0): {coord_zeroes}')\n"
                 "print(f'Valid Coordinates Outside Chicago Bounding Box: {out_of_bounds.sum()}')"),
        ("markdown", "### 6. Categorical Attributes & Offense Code Inspection"),
        ("code", "print(f'Unique Primary Crime Types: {df_raw[\"primary_type\"].nunique()}')\n"
                 "print(f'Unique IUCR Offense Codes: {df_raw[\"iucr\"].nunique()}')\n"
                 "print(f'Unique FBI Codes: {df_raw[\"fbi_code\"].nunique()}')\n"
                 "print(f'Unique Location Descriptions: {df_raw[\"location_description\"].nunique()}')\n"
                 "print(f'Arrest Flag Distribution:\\n{df_raw[\"arrest\"].value_counts(dropna=False)}')\n"
                 "print(f'Domestic Flag Distribution:\\n{df_raw[\"domestic\"].value_counts(dropna=False)}')")
    ]
    create_notebook(cells, filepath)

def generate_02_curation(filepath):
    cells = [
        ("markdown", "# Notebook 02: Data Curation and Feature Engineering\n"
                     "## Transformation, Imputation, and Feature Derivation\n"
                     "**Author:** Data Engineering & Analytics Team\n\n"
                     "### Objective:\n"
                     "Execute attribute-specific data quality treatments without dropping useful fact records. "
                     "Engineer all temporal, contextual, spatial, and categorization features required for dimensional loading and predictive analytics."),
        ("code", "import os\n"
                 "import pandas as pd\n"
                 "import numpy as np\n\n"
                 "raw_path = '../data/raw/crimes_2024_2025.csv'\n"
                 "df = pd.read_csv(raw_path, low_memory=False)\n"
                 "initial_rows = len(df)\n"
                 "print(f'Initial Raw Record Count: {initial_rows:,}')"),
        ("markdown", "### 1. Attribute-Specific Treatments (No Blanket Deletions)"),
        ("code", "# Impute missing location description with UNKNOWN\n"
                 "df['location_description'] = df['location_description'].fillna('UNKNOWN').astype(str).str.strip().str.upper()\n"
                 "# Impute missing administrative Ward and Community Area with sentinel -1\n"
                 "df['ward'] = df['ward'].fillna(-1).astype(int)\n"
                 "df['community_area'] = df['community_area'].fillna(-1).astype(int)\n"
                 "# Geocoordinate flag\n"
                 "df['has_valid_coordinates'] = (df['latitude'].notnull() & df['longitude'].notnull()).astype(int)\n"
                 "print('Data quality treatments applied successfully.')"),
        ("markdown", "### 2. Standardize Offense Codes and Text Formatting"),
        ("code", "df['iucr'] = df['iucr'].astype(str).str.strip().str.zfill(4)\n"
                 "df['fbi_code'] = df['fbi_code'].astype(str).str.strip()\n"
                 "df['primary_type'] = df['primary_type'].astype(str).str.strip().str.upper()\n"
                 "df['district'] = df['district'].astype(str).str.strip().str.zfill(3)\n"
                 "df['beat'] = df['beat'].astype(str).str.strip().str.zfill(4)"),
        ("markdown", "### 3. Date & Time Decomposition"),
        ("code", "df['incident_datetime'] = pd.to_datetime(df['date'])\n"
                 "df['full_date'] = df['incident_datetime'].dt.date\n"
                 "df['year'] = df['incident_datetime'].dt.year\n"
                 "df['month'] = df['incident_datetime'].dt.month\n"
                 "df['quarter'] = df['incident_datetime'].dt.quarter\n"
                 "df['day'] = df['incident_datetime'].dt.day\n"
                 "df['day_of_week'] = df['incident_datetime'].dt.day_of_week + 1 # 1=Mon, 7=Sun\n"
                 "df['day_name'] = df['incident_datetime'].dt.day_name()\n"
                 "df['hour'] = df['incident_datetime'].dt.hour\n"
                 "df['minute'] = df['incident_datetime'].dt.minute\n"
                 "df['is_weekend'] = df['day_of_week'].apply(lambda d: 1 if d in [6, 7] else 0)"),
        ("markdown", "### 4. Operational TimeBands and Night Incident Flag\n"
                     "- **Night:** 21:00 to 04:59 (Hours 21-23, 0-4)\n"
                     "- **Morning:** 05:00 to 11:59 (Hours 5-11)\n"
                     "- **Afternoon:** 12:00 to 16:59 (Hours 12-16)\n"
                     "- **Evening:** 17:00 to 20:59 (Hours 17-20)"),
        ("code", "def get_time_band(h):\n"
                 "    if h in [21, 22, 23, 0, 1, 2, 3, 4]: return 'Night'\n"
                 "    elif h in [5, 6, 7, 8, 9, 10, 11]: return 'Morning'\n"
                 "    elif h in [12, 13, 14, 15, 16]: return 'Afternoon'\n"
                 "    else: return 'Evening'\n\n"
                 "df['time_band'] = df['hour'].apply(get_time_band)\n"
                 "df['is_night_incident'] = (df['time_band'] == 'Night').astype(int)\n"
                 "df['arrest_flag'] = (df['arrest'] == True).astype(int)\n"
                 "df['domestic_flag'] = (df['domestic'] == True).astype(int)"),
        ("markdown", "### 5. Crime and Location Operational Groupings"),
        ("code", "def categorize_crime(pt):\n"
                 "    pt = str(pt).strip().upper()\n"
                 "    violent = {'HOMICIDE', 'CRIMINAL SEXUAL ASSAULT', 'ROBBERY', 'ASSAULT', 'BATTERY', 'KIDNAPPING', 'INTIMIDATION', 'STALKING'}\n"
                 "    prop = {'THEFT', 'BURGLARY', 'MOTOR VEHICLE THEFT', 'ARSON', 'DECEPTIVE PRACTICE', 'CRIMINAL DAMAGE', 'CRIMINAL TRESPASS'}\n"
                 "    subst = {'NARCOTICS', 'OTHER NARCOTIC VIOLATION', 'LIQUOR LAW VIOLATION'}\n"
                 "    pub = {'WEAPONS VIOLATION', 'PUBLIC PEACE VIOLATION', 'INTERFERENCE WITH PUBLIC OFFICER', 'CONCEALED CARRY LICENSE VIOLATION', 'PROSTITUTION', 'GAMBLING', 'PUBLIC INDECENCY', 'OBSCENITY'}\n"
                 "    if pt in violent: return 'Violent Crime'\n"
                 "    elif pt in prop: return 'Property Crime'\n"
                 "    elif pt in subst: return 'Substance Offense'\n"
                 "    elif pt in pub: return 'Public Order & Weapons'\n"
                 "    else: return 'Other Offenses'\n\n"
                 "df['crime_category_group'] = df['primary_type'].apply(categorize_crime)\n"
                 "print(df['crime_category_group'].value_counts())"),
        ("markdown", "### 6. Curation Reconciliation Summary"),
        ("code", "print(f'Initial Raw Rows: {initial_rows:,}')\n"
                 "print(f'Curated Rows:     {len(df):,}')\n"
                 "print(f'Preservation Rate: {len(df)/initial_rows*100:.2f}% (0 rows dropped)')\n"
                 "print(f'Total Arrests:    {df[\"arrest_flag\"].sum():,}')\n"
                 "print(f'Total Domestic:   {df[\"domestic_flag\"].sum():,}')")
    ]
    create_notebook(cells, filepath)

def generate_03_eda(filepath):
    cells = [
        ("markdown", "# Notebook 03: Exploratory Data Analysis (EDA)\n"
                     "## Statistical Profiles, Distributions, Temporal Trends, and Rate Analytics\n"
                     "**Author:** Data Engineering & Analytics Team\n\n"
                     "### Objective:\n"
                     "Perform comprehensive exploratory data analysis across numerical metrics (mean, std, quartiles, IQR, skewness, kurtosis), "
                     "categorical distributions, diurnal hourly patterns, weekly rhythms, geographic concentrations, and critical volume vs. rate distinctions."),
        ("code", "import os\n"
                 "import pandas as pd\n"
                 "import numpy as np\n"
                 "import matplotlib.pyplot as plt\n"
                 "import seaborn as sns\n"
                 "from scipy import stats\n\n"
                 "curated_path = '../data/curated/crimes_curated.csv'\n"
                 "df = pd.read_csv(curated_path, low_memory=False)\n"
                 "print(f'Loaded {len(df):,} curated incidents.')"),
        ("markdown", "### 1. Numerical Statistical Summary Table"),
        ("code", "stats_df = pd.read_csv('../outputs/tables/numerical_stats_table.csv')\n"
                 "stats_df"),
        ("markdown", "### 2. Primary Crime Type Volume and Percentage Share"),
        ("code", "pt_freq = pd.read_csv('../outputs/tables/primary_type_frequencies.csv')\n"
                 "pt_freq.head(15)"),
        ("markdown", "### 3. Volume vs. Arrest Rate: The Critical Distinction"),
        ("code", "crosstab_cat = pd.read_csv('../outputs/tables/crosstab_category_arrest.csv', index_col=0)\n"
                 "crosstab_cat"),
        ("markdown", "### 4. Visualizations"),
        ("code", "from IPython.display import Image, display\n"
                 "display(Image(filename='../outputs/figures/fig01_top_crime_types.png'))\n"
                 "display(Image(filename='../outputs/figures/fig02_volume_vs_arrest_rate.png'))\n"
                 "display(Image(filename='../outputs/figures/fig03_monthly_temporal_trend.png'))\n"
                 "display(Image(filename='../outputs/figures/fig04_hourly_distribution_peaks.png'))\n"
                 "display(Image(filename='../outputs/figures/fig05_hour_day_heatmap.png'))\n"
                 "display(Image(filename='../outputs/figures/fig06_district_volume_vs_arrest_rate.png'))\n"
                 "display(Image(filename='../outputs/figures/fig07_top20_community_areas.png'))\n"
                 "display(Image(filename='../outputs/figures/fig08_location_group_distribution.png'))")
    ]
    create_notebook(cells, filepath)

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    nb_dir = os.path.join(base_dir, "notebooks")
    generate_01_profiling(os.path.join(nb_dir, "01_profiling.ipynb"))
    generate_02_curation(os.path.join(nb_dir, "02_curation.ipynb"))
    generate_03_eda(os.path.join(nb_dir, "03_eda.ipynb"))
