# Power BI Public Safety Analytics Dashboard: Build & Implementation Guide

## 1. Data Connection Architecture
Power BI connects directly to the PostgreSQL 16 Data Warehouse or imports pre-exported star schema tables from `outputs/powerbi_exports/`.

### Direct PostgreSQL Connection Settings:
- **Server:** `localhost:5432`
- **Database:** `chicago_crime_dw`
- **Data Connectivity Mode:** `Import` (Recommended for VertiPaq compression) or `DirectQuery`
- **Authentication:** Database Credentials (`User: postgres`, `Password: root`)

### Alternative CSV Import Path:
Import all CSV files located in `outputs/powerbi_exports/`:
1. `dim_date.csv` (Conformed Date Dimension)
2. `dim_time.csv` (Conformed Time Dimension)
3. `dim_crime_type.csv` (Offense Classification Dimension)
4. `dim_location.csv` (Administrative Geography Dimension)
5. `fact_crime_incident_summary.csv` (Aggregated Fact Table, 187k rows)
6. `fact_area_daily.csv` (Area-Daily Constellation Fact Table, 53k rows)

## 2. Power BI Data Model Relationships (Star Schema Topology)
- `DimDate[DateKey]` 1 --- * `FactCrimeIncident[DateKey]` (Single direction)
- `DimTime[TimeKey]` 1 --- * `FactCrimeIncident[TimeKey]` (Single direction)
- `DimCrimeType[CrimeTypeKey]` 1 --- * `FactCrimeIncident[CrimeTypeKey]` (Single direction)
- `DimLocation[LocationKey]` 1 --- * `FactCrimeIncident[LocationKey]` (Single direction)
- `DimDate[DateKey]` 1 --- * `FactAreaDailyPublicSafety[DateKey]` (Single direction)

## 3. Mandatory DAX Measures

```dax
// Measure 1: Total Incidents
Total Incidents = SUM(FactCrimeIncident[IncidentCount])

// Measure 2: Total Recorded Arrests
Total Arrests = SUM(FactCrimeIncident[ArrestCount])

// Measure 3: Arrest Clearance Rate (%)
Arrest Rate = DIVIDE([Total Arrests], [Total Incidents], 0) * 100

// Measure 4: Total Domestic Violence Incidents
Domestic Incidents = SUM(FactCrimeIncident[DomesticCount])

// Measure 5: Domestic Incident Rate (%)
Domestic Rate = DIVIDE([Domestic Incidents], [Total Incidents], 0) * 100

// Measure 6: Total Night Incidents (21:00 - 04:59)
Night Incidents = SUM(FactCrimeIncident[NightCount])

// Measure 7: Night Incident Percentage (%)
Night Incident Pct = DIVIDE([Night Incidents], [Total Incidents], 0) * 100

// Measure 8: Distinct Statutory Crime Types
Distinct Crime Types = DISTINCTCOUNT(FactCrimeIncident[CrimeTypeKey])
```

## 4. Dashboard Canvas Layout & Page Specifications

### Page 1: Executive Public Safety Overview
- **Header KPI Cards (Top Row):**
  - Card 1: `Total Incidents` (497,919)
  - Card 2: `Total Arrests` (74,379)
  - Card 3: `Arrest Rate` (14.94%)
  - Card 4: `Domestic Incidents` (93,093)
  - Card 5: `Night Incidents` (152,810)
  - Card 6: `Distinct Crime Types` (353)
- **Visual 1 (Line & Clustered Column Chart):** Monthly Incident Volume & Arrest Clearance Rate (`YearMonth` on X-axis, `Total Incidents` on Column Y-axis, `Arrest Rate` on Line Y-axis).
- **Visual 2 (Donut Chart):** Incident Distribution by `CrimeCategoryGroup` (Violent, Property, Substance, Public Order).
- **Visual 3 (Bar Chart):** Incident Volume by `TimeBand` (Afternoon, Evening, Night, Morning).
- **Interactive Slicers:** `Year` (2024, 2025), `Quarter` (Q1–Q4), `IsWeekend` (Weekday vs Weekend).

### Page 2: Crime Type & Offense Analytics
- **Visual 1 (Clustered Bar Chart):** Top 15 `PrimaryType` categories ranked by incident volume.
- **Visual 2 (Scatter Chart):** Offense Clearance Matrix (`Total Incidents` on X-axis, `Arrest Rate` on Y-axis, Bubble Size = `Domestic Incidents`, Category = `PrimaryType`).
- **Visual 3 (Tree Map):** Hierarchical Crime Classification (`CrimeCategoryGroup` -> `PrimaryType` -> `Description`).
- **Visual 4 (Table Matrix):** Primary Offense vs. Arrest Status and Domestic Violence flag.

### Page 3: Geographic & Spatial Hotspot Analytics
- **Visual 1 (Filled Map / Shape Map):** Chicago Community Areas colored by `Total Incidents`.
- **Visual 2 (Horizontal Bar Chart):** Top 10 Police Districts by Crime Volume with colored data bars for `Arrest Rate`.
- **Visual 3 (Matrix Grid):** Police District vs. `LocationGroup` (Street, Residential, Commercial, Transit).
- **Visual 4 (Card):** Top Risk Area KPI (Community Area 25 - Austin: 30,123 incidents).

### Page 4: Temporal & Diurnal Heatmap Analytics
- **Visual 1 (Matrix Visual Heatmap):** Day of Week (`Monday` to `Sunday`) on Rows, Hour of Day (`0` to `23`) on Columns, Values = `Total Incidents`, Conditional Formatting = 3-color gradient (Green-Yellow-Red).
- **Visual 2 (Area Chart):** Hourly Trend comparing Weekday vs. Weekend incident volume.
- **Visual 3 (Column Chart):** Day of Week Volume with Arrest Rate overlay.
