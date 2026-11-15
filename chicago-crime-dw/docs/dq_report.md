# Data Quality and Curation Audit Report

## 1. Executive Summary
A comprehensive attribute-by-attribute data quality audit was conducted on the raw Chicago Police Department crime incident dataset for 2024–2025 (497,919 raw records). Following strict dimensional warehousing practices, **no blanket record deletions were performed**. Instead, records with missing administrative or geographic fields were retained and mapped to standardized `'UNKNOWN'` or surrogate key `-1` dimension members. This approach preserves 100% of incident records for aggregate temporal, crime-type, and rate analytics while preventing foreign-key violations.

## 2. Data Quality Problem & Treatment Table

| Quality Problem | Affected Attribute | Count | Treatment | Justification |
| :--- | :--- | :--- | :--- | :--- |
| Missing Location Description | `location_description` | 2,424 | Imputed with 'UNKNOWN' | Preserves incident event records while routing unrecorded venues to the standard 'UNKNOWN' dimension member. |
| Missing Administrative Ward | `ward` | 1 | Imputed with -1 (Unknown Ward) | Maintains referential integrity with DimLocation without dropping records lacking municipal legislative boundary tags. |
| Missing Community Area Number | `community_area` | 16 | Imputed with -1 (Unknown Community Area) | Retains valid incidents; isolates missing spatial neighborhood assignments to surrogate key -1. |
| Missing / Null Geocoordinates | `latitude, longitude, x_coordinate, y_coordinate` | 4,904 | Retained row; assigned LatitudeBand='Unknown', LongitudeBand='Unknown', has_valid_coordinates=0 | Address-level privacy masking or unindexed locations. Records are valid for temporal, district, and offense analytics. |
| Coordinates Outside Chicago Bounds | `latitude, longitude` | 0 | Validated - All coordinates lie within [41.60, 42.06] N and [-87.95, -87.50] W | Bounding box verification ensures accurate GIS boundary integrity. |
| Exact Row Duplicates | `All columns` | 0 | Validated - 0 exact duplicates found | Each row represents a distinct reported crime incident. |
| Shared CPD Case Numbers (Logical Multi-Charge Records) | `case_number` | 51 | Retained all rows with unique 'id' as primary surrogate/natural key | CPD files multi-victim or multi-offense occurrences under one case number; each row represents a distinct charge line. |

## 3. Pre- and Post-Curation Reconciliation

| Metric | Raw Source Value | Curated Warehouse Value | Reconciliation Status |
| :--- | :--- | :--- | :--- |
| Total Record Count | 497,919 | 497,919 | **EXACT MATCH (0 dropped)** |
| Total Recorded Arrests | 74,379 | 74,379 | **EXACT MATCH** |
| Total Domestic Incidents | 93,093 | 93,093 | **EXACT MATCH** |
| Total Night Incidents | 152,810 | 152,810 | **EXACT MATCH** |
| Earliest Incident Date | 2024-01-01 | 2024-01-01 | **EXACT MATCH** |
| Latest Incident Date | 2025-12-31 | 2025-12-31 | **EXACT MATCH** |
