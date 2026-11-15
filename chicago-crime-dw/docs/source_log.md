# Data Source and Extraction Log

## 1. Dataset Provenance
- **Dataset Name:** Crimes - 2001 to Present
- **Publisher:** City of Chicago / Chicago Police Department (CPD)
- **Portal Identifier:** `ijzp-q8t2`
- **Authoritative URL:** [Chicago Data Portal](https://data.cityofchicago.org/Public-Safety/Crimes-2001-to-Present/ijzp-q8t2)
- **Download Timestamp:** 2026-11-15 10:17:00 UTC

## 2. Extraction Scope and Query Parameters
- **Temporal Filter ($where):** `date >= '2024-01-01T00:00:00.000' and date <= '2025-12-31T23:59:59.000'`
- **Total Rows Extracted:** 497,919
- **Total Columns:** 21
- **Selected Fields:** id, case_number, date, block, iucr, primary_type, description, location_description, arrest, domestic, beat, district, ward, community_area, fbi_code, x_coordinate, y_coordinate, year, updated_on, latitude, longitude
- **Pagination Method:** Socrata SoQL `$limit=50000`, `$offset` with multi-threaded chunking
- **Raw File Location:** `M:\Third Year\PEC Exploratory Data Analytics LAB\EDA Project\chicago-crime-dw\data\raw\crimes_2024_2025.csv`
- **Raw File Size:** 103.17 MB

## 3. Extraction Verification
- Server total report: 497,919 rows
- Local CSV row count: 497,919 rows
- Status: PASSED - Row counts match exactly
