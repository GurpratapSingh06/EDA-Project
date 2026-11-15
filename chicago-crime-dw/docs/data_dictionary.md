# Chicago Crime Incident Warehouse: Data Dictionary

This data dictionary provides a formal catalog of all attributes utilized in the Chicago Crime Batch Data Warehouse, explicitly distinguishing original source fields from engineered derived attributes.

## 1. Original Source Attributes (City of Chicago Portal: ijzp-q8t2)

| Attribute Name | Source Data Type | Target Warehouse Type | Description | Sample Values |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | BIGINT | Unique CPD incident identifier (primary surrogate/natural key) | `13324861`, `27932` |
| `case_number` | TEXT | VARCHAR(20) | Chicago Police Department RD (Records Division) case number | `JH100028`, `JH102838` |
| `date` | TIMESTAMP | TIMESTAMP | Incident reported timestamp (ISO 8601 string in source) | `2024-01-01 00:56:00` |
| `block` | TEXT | VARCHAR(100) | Anonymized block-level incident address (e.g., 070XX S WABASH AVE) | `070XX S WABASH AVE` |
| `iucr` | TEXT | VARCHAR(10) | Illinois Uniform Crime Reporting 4-digit offense code | `0110`, `0460`, `0820` |
| `primary_type` | TEXT | VARCHAR(60) | Primary offense categorization defined by CPD | `BATTERY`, `THEFT`, `HOMICIDE` |
| `description` | TEXT | VARCHAR(100) | Detailed statutory offense subcategory | `AGGRAVATED - HANDGUN`, `SIMPLE` |
| `location_description` | TEXT | VARCHAR(100) | Physical environment or premises where crime occurred | `STREET`, `RESIDENCE`, `ALLEY` |
| `arrest` | BOOLEAN | BOOLEAN | Indicates whether an arrest was made at the time of reporting | `true`, `false` |
| `domestic` | BOOLEAN | BOOLEAN | Indicates whether incident involved the Illinois Domestic Violence Act | `true`, `false` |
| `beat` | TEXT | VARCHAR(10) | Smallest geographic police patrol territory (4 digits) | `0322`, `1531` |
| `district` | TEXT | VARCHAR(10) | Police district administrative territory (22 active districts) | `001`, `011`, `015` |
| `ward` | INTEGER | INTEGER | Chicago City Council legislative ward (1–50) | `1` to `50`, `-1` for Unknown |
| `community_area` | INTEGER | INTEGER | Official Chicago community area identifier (1–77) | `1` to `77`, `-1` for Unknown |
| `fbi_code` | TEXT | VARCHAR(10) | FBI Uniform Crime Reporting (UCR) classification code | `01A`, `06`, `08B`, `14` |
| `x_coordinate` | FLOAT | DOUBLE PRECISION | State Plane Illinois East NAD 1983 projection coordinate (feet) | `1177944.0` |
| `y_coordinate` | FLOAT | DOUBLE PRECISION | State Plane Illinois East NAD 1983 projection coordinate (feet) | `1858323.0` |
| `latitude` | FLOAT | DOUBLE PRECISION | WGS 84 latitude coordinate | `41.766555` |
| `longitude` | FLOAT | DOUBLE PRECISION | WGS 84 longitude coordinate | `-87.623324` |
| `updated_on` | TIMESTAMP | TIMESTAMP | Timestamp when record was last updated by CPD in source portal | `2024-01-09 15:40:58` |

## 2. Derived and Feature-Engineered Attributes

| Derived Attribute Name | Data Type | Derivation Formula / Logic | Thresholds / Binning Definitions | Analytical Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `hour` | INTEGER | `EXTRACT(HOUR FROM date)` | `0` to `23` | Hourly temporal distribution and peak analysis |
| `day_of_week` | INTEGER | `EXTRACT(ISODOW FROM date)` | `1` (Monday) to `7` (Sunday) | Weekly cyclical trend analysis |
| `day_name` | VARCHAR(15) | `TO_CHAR(date, 'Day')` | Monday through Sunday | Dashboard filtering and human-readable reporting |
| `month` | INTEGER | `EXTRACT(MONTH FROM date)` | `1` to `12` | Monthly trend evaluation and seasonal analysis |
| `quarter` | INTEGER | `EXTRACT(QUARTER FROM date)` | `1` to `4` | Quarterly OLAP roll-up aggregations |
| `year` | INTEGER | `EXTRACT(YEAR FROM date)` | `2024` or `2025` | Annual multi-year comparisons |
| `is_weekend` | INTEGER | `1 if day_of_week IN (6,7) else 0` | Binary {0, 1} | Weekend vs. weekday comparative pattern mining |
| `time_band` | VARCHAR(20) | Case-based hourly binning | **Night:** 21:00–04:59 (hours 21–23, 0–4)<br>**Morning:** 05:00–11:59 (hours 5–11)<br>**Afternoon:** 12:00–16:59 (hours 12–16)<br>**Evening:** 17:00–20:59 (hours 17–20) | Operational shift-based aggregation & OLAP slicing |
| `is_night_incident` | INTEGER | `1 if time_band == 'Night' else 0` | Binary {0, 1} | Direct measure aggregation of night crime volume |
| `arrest_flag` | INTEGER | `1 if arrest == True else 0` | Binary {0, 1} | Additive measure for computing arrest rates |
| `domestic_flag` | INTEGER | `1 if domestic == True else 0` | Binary {0, 1} | Additive measure for computing domestic incident rates |
| `crime_category_group` | VARCHAR(40) | Mapping from `primary_type` | **Violent Crime:** Homicide, Assault, Battery, Robbery, Sexual Assault, Kidnapping<br>**Property Crime:** Theft, Burglary, Motor Vehicle Theft, Arson, Damage<br>**Substance Offense:** Narcotics, Liquor Law<br>**Public Order & Weapons:** Weapons, Public Peace, Concealed Carry<br>**Other Offenses:** All remaining | High-level categorization for executive dashboards & OLAP |
| `location_group` | VARCHAR(40) | Keyword classification of `location_description` | **Street & Outdoor:** Street, Sidewalk, Alley, Park<br>**Residential:** Apartment, Residence, Porch<br>**Commercial & Retail:** Store, Restaurant, Bank, Hotel<br>**Transit & Vehicles:** CTA, Bus, Train, Airport, Vehicle<br>**Public Facility:** Hospital, School, Police, Church<br>**Other/Unknown:** Unclassified | Dimensional grouping to prevent high-cardinality fragmentation |
| `latitude_band` | VARCHAR(40) | Spatial partitioning by latitude | South (< 41.78 N), Central (41.78–41.88 N), North (> 41.88 N), Unknown | Macro-geographic spatial stratification |
| `longitude_band` | VARCHAR(40) | Spatial partitioning by longitude | West (< -87.72 W), Central (-87.72– -87.64 W), East (> -87.64 W), Unknown | Macro-geographic longitudinal stratification |
| `community_area_band` | VARCHAR(30) | Quartiles of total 2-year crime volume per community area | **Low Volume (Q1):** <= 25th percentile<br>**Moderate Volume (Q2):** 25–50th percentile<br>**High Volume (Q3):** 50–75th percentile<br>**Critical Volume (Q4):** > 75th percentile | Socio-demographic area risk stratification |
| `incident_density_band` | VARCHAR(30) | Daily community area incident frequency quartiles | **Band 1:** Very Low (0–25%)<br>**Band 2:** Low-Medium (25–50%)<br>**Band 3:** Medium-High (50–75%)<br>**Band 4:** High Density (> 75%) | Area-day intensity classification for regression target |
