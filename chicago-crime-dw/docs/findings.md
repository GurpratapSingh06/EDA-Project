# Ten Analytical Findings and Policy Recommendations

Each finding strictly adheres to the empirical framework: **Question -> Analysis -> Evidence -> Interpretation -> Recommendation**.

## Finding 1: Diurnal Crime Surge and Peak Operating Windows
- **Question:** At what specific diurnal hours and operational shifts does Chicago experience peak crime concentrations?
- **Analysis:** Hourly aggregation of 497,919 incidents across 24-hour military cycles was performed, tracking incident counts, arrest clearance rates, and night classifications.
- **Evidence:** Chart [`outputs/figures/fig04_hourly_distribution_peaks.png`](file:///M:/Third%20Year/PEC%20Exploratory%20Data%20Analytics%20LAB/EDA%20Project/chicago-crime-dw/outputs/figures/fig04_hourly_distribution_peaks.png) and table [`outputs/tables/hourly_summary.csv`](file:///M:/Third%20Year/PEC%20Exploratory%20Data%20Analytics%20LAB/EDA%20Project/chicago-crime-dw/outputs/tables/hourly_summary.csv). Citywide crime peaks between **18:00 and 22:00**, reaching an apex of **28,812 incidents at 18:00** and **28,154 incidents at 20:00**, compared to the diurnal nadir at **05:00 (7,159 incidents)**—a **4.02x surge**.
- **Interpretation:** Peak crime corresponds with evening commuter transit, commercial retail closings, and night-time socializing. Patrol shifts ending at 18:00 create an operational handover vulnerability.
- **Recommendation:** Implement staggered shift deployments with peak patrol saturation between 17:00 and 23:00, avoiding shift handovers during the 18:00 peak.

## Finding 2: Property Crime Volume Dominance vs. Clearance Deficit
- **Question:** How does raw incident volume correlate with police arrest clearance rates across major crime categories?
- **Analysis:** Evaluated categorical cross-tabulations of Crime Category Groups against recorded arrest outcomes.
- **Evidence:** Chart [`outputs/figures/fig02_volume_vs_arrest_rate.png`](file:///M:/Third%20Year/PEC%20Exploratory%20Data%20Analytics%20LAB/EDA%20Project/chicago-crime-dw/outputs/figures/fig02_volume_vs_arrest_rate.png) and table [`outputs/tables/crosstab_category_arrest.csv`](file:///M:/Third%20Year/PEC%20Exploratory%20Data%20Analytics%20LAB/EDA%20Project/chicago-crime-dw/outputs/tables/crosstab_category_arrest.csv). Property Crime represents **54.38% of all incidents (270,758 crimes)**, but has an arrest clearance rate of only **6.56% (17,766 arrests)**. Conversely, Substance Offenses comprise only 2.77% of volume (13,817 crimes) but yield a **96.48% arrest rate (13,331 arrests)**.
- **Interpretation:** Raw incident volume is heavily decoupled from police enforcement capacity. High property crime (theft, motor vehicle theft) carries near-zero on-scene apprehension rates, inflating public insecurity.
- **Recommendation:** Deploy automated license plate readers (ALPR) and commercial digital evidence collection portals to boost property crime investigative solvability without diverting street patrol officers.

## Finding 3: Severe Spatial Concentration in South and West Side Communities
- **Question:** What degree of spatial concentration characterizes Chicago's crime landscape across municipal community areas?
- **Analysis:** Calculated cumulative volume distributions across all 77 Chicago community areas over 2024–2025.
- **Evidence:** Chart [`outputs/figures/fig07_top20_community_areas.png`](file:///M:/Third%20Year/PEC%20Exploratory%20Data%20Analytics%20LAB/EDA%20Project/chicago-crime-dw/outputs/figures/fig07_top20_community_areas.png) and table [`outputs/tables/community_area_summary.csv`](file:///M:/Third%20Year/PEC%20Exploratory%20Data%20Analytics%20LAB/EDA%20Project/chicago-crime-dw/outputs/tables/community_area_summary.csv). The top 5 community areas (Area 25 - Austin: **30,123 incidents**, Area 8 - Near North Side: **24,191**, Area 32 - Loop: **20,937**, Area 28 - Near West Side: **18,506**, Area 43 - South Shore: **15,901**) account for **22.02% of all citywide crimes** despite covering <7% of municipal land area.
- **Interpretation:** Austin exhibits systemic violent and domestic crime, whereas the Near North Side and Loop suffer high commercial retail and property thefts.
- **Recommendation:** Apply differentiated strategies: deploy community violence interruption and social service co-responders in Austin and South Shore, while focusing on commercial security partnerships in the Loop.

## Finding 4: Summer Seasonal Surge and Mid-Winter Troughs
- **Question:** What is the seasonal volatility of crime and how does weather influence criminal activity?
- **Analysis:** Longitudinal time-series evaluation across 24 consecutive months (January 2024 to December 2025).
- **Evidence:** Chart [`outputs/figures/fig03_monthly_temporal_trend.png`](file:///M:/Third%20Year/PEC%20Exploratory%20Data%20Analytics%20LAB/EDA%20Project/chicago-crime-dw/outputs/figures/fig03_monthly_temporal_trend.png) and table [`outputs/tables/monthly_trends.csv`](file:///M:/Third%20Year/PEC%20Exploratory%20Data%20Analytics%20LAB/EDA%20Project/chicago-crime-dw/outputs/tables/monthly_trends.csv). Monthly crime peaks annually in July (July 2024: **24,354 incidents**; July 2025: **24,118 incidents**) and hits annual lows in February (February 2024: **17,215**; February 2025: **16,344**)—representing a **41.5% summer expansion**.
- **Interpretation:** Elevated temperatures and extended daylight increase outdoor pedestrian density and interpersonal friction, whereas sub-zero winter temperatures suppress street-level activity.
- **Recommendation:** Implement seasonal patrol mobilization: schedule CPD tactical officer leave during winter months (Jan–Feb) and surge outdoor foot and bike patrols between June 1 and Labor Day.

## Finding 5: Domestic Violence Structural Resistance to Arrest
- **Question:** How do domestic violence incidents differ from non-domestic offenses in temporal timing and arrest outcomes?
- **Analysis:** Isolated all 93,093 domestic violence incidents (18.70% of total) and cross-analyzed time of day and arrest rates.
- **Evidence:** Chart [`outputs/figures/fig03_monthly_temporal_trend.png`](file:///M:/Third%20Year/PEC%20Exploratory%20Data%20Analytics%20LAB/EDA%20Project/chicago-crime-dw/outputs/figures/fig03_monthly_temporal_trend.png) and table [`outputs/tables/crosstab_category_arrest.csv`](file:///M:/Third%20Year/PEC%20Exploratory%20Data%20Analytics%20LAB/EDA%20Project/chicago-crime-dw/outputs/tables/crosstab_category_arrest.csv). Domestic incidents yield an arrest in only **15.82% of cases (14,732 arrests)**. Furthermore, **34.21% of domestic incidents occur during night hours (21:00–04:59)**, predominantly inside residential apartments.
- **Interpretation:** Domestic crimes occur inside private spaces where police lack immediate visual access, and victim recantation or offender departure prior to police arrival depresses on-scene arrest rates.
- **Recommendation:** Establish dedicated domestic violence follow-up detective units paired with survivor crisis advocates within 24 hours of dispatch, bypassing reliance on immediate on-scene arrests.

## Finding 6: Street and Outdoor Premises as Primary Crime Generators
- **Question:** What physical environments host the greatest share of criminal activity?
- **Analysis:** Categorized 134 unique location descriptions into standardized environmental operational groups.
- **Evidence:** Chart [`outputs/figures/fig08_location_group_distribution.png`](file:///M:/Third%20Year/PEC%20Exploratory%20Data%20Analytics%20LAB/EDA%20Project/chicago-crime-dw/outputs/figures/fig08_location_group_distribution.png) and table [`outputs/tables/location_group_summary.csv`](file:///M:/Third%20Year/PEC%20Exploratory%20Data%20Analytics%20LAB/EDA%20Project/chicago-crime-dw/outputs/tables/location_group_summary.csv). Street & Outdoor premises account for **44.91% of all reported crimes (223,612 incidents)**, followed by Residential premises at **30.58% (152,284 incidents)** and Commercial & Retail at **14.88% (74,078 incidents)**.
- **Interpretation:** Public thoroughfares, sidewalks, and unmonitored parking lots constitute the primary crime landscape due to high anonymity and rapid vehicular escape corridors.
- **Recommendation:** Implement CPTED (Crime Prevention Through Environmental Design): upgrade LED streetlighting in high-incident alleys and expand municipal high-definition surveillance coverage along arterial roadways.

## Finding 7: Weekend Temporal Displacement of Violent Offenses
- **Question:** How do crime patterns shift between standard weekdays and weekend days?
- **Analysis:** Evaluated day-of-week distributions, comparing Monday–Thursday baseline with Friday–Sunday volumes.
- **Evidence:** Heatmap [`outputs/figures/fig05_hour_day_heatmap.png`](file:///M:/Third%20Year/PEC%20Exploratory%20Data%20Analytics%20LAB/EDA%20Project/chicago-crime-dw/outputs/figures/fig05_hour_day_heatmap.png). Weekend days (Saturday and Sunday) host **29.74% of all crime (148,091 incidents)**, representing a **6.1% elevation over expected uniform distribution**. Violent crimes specifically jump by **14.2% on weekends**, concentrated between 21:00 Friday and 03:00 Sunday.
- **Interpretation:** Nightlife activity, alcohol consumption, and diminished structured daytime routines on weekends elevate interpersonal conflicts.
- **Recommendation:** Implement tactical weekend curfew enforcement for minors, intensify tavern/bar security inspections, and deploy dedicated DUI/weapons saturation patrols on Friday and Saturday nights.

## Finding 8: High Clearance Rates in Police-Initiated Offenses vs. Low Public-Reported Clearance
- **Question:** Why do certain crime types exhibit near-100% arrest rates while others languish below 10%?
- **Analysis:** Evaluated arrest clearance across police-initiated vs victim-reported offenses.
- **Evidence:** Table [`outputs/tables/crime_type_volume_and_rates.csv`](file:///M:/Third%20Year/PEC%20Exploratory%20Data%20Analytics%20LAB/EDA%20Project/chicago-crime-dw/outputs/tables/crime_type_volume_and_rates.csv). Narcotics (**96.48% arrest rate**, 13,331 arrests), Weapons Violations (**78.12% arrest rate**, 11,245 arrests), and Prostitution (**98.15% arrest rate**) contrast sharply with Motor Vehicle Theft (**3.42% arrest rate**, 1,621 arrests from 47,402 incidents) and Deceptive Practice (**2.91% arrest rate**).
- **Interpretation:** Offenses detected directly by officer proactive intervention (traffic stops, weapon frisks) intrinsically yield an immediate arrest, creating a misleading optical boost to overall police clearance metrics.
- **Recommendation:** Rebalance performance metrics: evaluate police district performance on victim-reported property and violent crime closure rates rather than proactive narcotics volume.

## Finding 9: Transit System Crime Clustering in Downtown Stations
- **Question:** What is the spatial profile of crime across Chicago's public transit network (CTA buses and trains)?
- **Analysis:** Filtered incidents occurring on CTA train platforms, rail cars, and bus routes across the 2-year window.
- **Evidence:** Table [`outputs/tables/location_group_summary.csv`](file:///M:/Third%20Year/PEC%20Exploratory%20Data%20Analytics%20LAB/EDA%20Project/chicago-crime-dw/outputs/tables/location_group_summary.csv). Transit-related crime accounts for **16,842 incidents (3.38% of citywide crime)**, with over 62% concentrated within District 001 (Central) and District 018 (Near North) along the Red and Blue subway lines.
- **Interpretation:** High passenger density on subway platforms facilitates pickpocketing and mobile device thefts, while late-night trains experience isolated robberies.
- **Recommendation:** Deploy uniformed transit security officers inside rail cars and at turnstile entrances, combined with high-visibility surveillance signage.

## Finding 10: Stability of Multi-Year Public Safety Trends (2024 vs. 2025)
- **Question:** Did Chicago's overall public safety landscape experience significant structural shifts between 2024 and 2025?
- **Analysis:** Comparative annual roll-up of total incidents, violent crime share, arrest volumes, and homicide counts.
- **Evidence:** Table [`outputs/tables/monthly_trends.csv`](file:///M:/Third%20Year/PEC%20Exploratory%20Data%20Analytics%20LAB/EDA%20Project/chicago-crime-dw/outputs/tables/monthly_trends.csv). Total crime contracted slightly by **1.99%** from 2024 (**251,467 incidents**) to 2025 (**246,452 incidents**). Overall arrest clearance rate held virtually constant at **14.88% in 2024 vs. 15.01% in 2025**.
- **Interpretation:** Chicago's crime trends reflect macroeconomic and demographic equilibrium rather than sudden policy-induced swings, validating the reliability of historical predictive models for future period forecasting.
- **Recommendation:** Maintain steady-state resource allocations while utilizing the batch data warehouse for long-term multi-year trend monitoring and machine learning feature extraction.
