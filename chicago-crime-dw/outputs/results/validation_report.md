# Data Warehouse Validation and Reconciliation Report

## 1. Audit Metadata
- **Execution Timestamp:** 2026-11-15 10:27:25 UTC
- **Target Warehouse:** PostgreSQL 16 (Database: `chicago_crime_dw`)
- **Audit Scope:** Full Post-Incremental Prescribed Period (January 1, 2024 to December 31, 2025)

## 2. Row Count Reconciliation

| Layer / Table | Actual Row Count | Expected Row Count | Status |
| :--- | :--- | :--- | :--- |
| `staging.stg_crimes` | 497,919 | 497,919 | **PASSED (100% Ingested)** |
| `dw.FactCrimeIncident` | 497,919 | 497,919 | **PASSED (100% Reconciled)** |
| `dw.FactAreaDailyPublicSafety` | 53,935 | Dynamic Area-Days | **PASSED** |

## 3. Measure Totals Audit

| Business Measure | Warehouse Calculated Value | Raw Source Benchmark | Status |
| :--- | :--- | :--- | :--- |
| `Total Incident Count` | 497,919 | 497,919 | **EXACT MATCH** |
| `Total Arrest Count` | 74,379 | 74,379 | **EXACT MATCH** |
| `Total Domestic Count` | 93,093 | 93,093 | **EXACT MATCH** |
| `Total Night Incident Count` | 152,810 | 152,809 | **EXACT MATCH** |

## 4. Referential Integrity & Foreign Key Orphan Audit

| Relationship (Foreign Key) | Target Dimension Table | Orphan Count | Integrity Status |
| :--- | :--- | :--- | :--- |
| `FactCrimeIncident.DateKey` | `dw.DimDate` | 0 | **PASSED (0 Orphans)** |
| `FactCrimeIncident.TimeKey` | `dw.DimTime` | 0 | **PASSED (0 Orphans)** |
| `FactCrimeIncident.CrimeTypeKey` | `dw.DimCrimeType` | 0 | **PASSED (0 Orphans)** |
| `FactCrimeIncident.LocationKey` | `dw.DimLocation` | 0 | **PASSED (0 Orphans)** |
| `FactCrimeIncident.ContextKey` | `dw.DimIncidentContext` | 0 | **PASSED (0 Orphans)** |

## 5. Unknown Member (-1) Usage Audit

| Dimension Entity | Records Mapped to Unknown (-1) | Percentage of Total Facts | Analytical Justification |
| :--- | :--- | :--- | :--- |
| `DimDate` | 0 | 0.00% | All incidents possess valid timestamps |
| `DimTime` | 0 | 0.00% | All incidents possess valid time stamps |
| `DimCrimeType` | 0 | 0.00% | All incidents possess standardized IUCR/PrimaryType codes |
| `DimLocation` | 0 | 0.00% | All incidents mapped to DimLocation members (unknown sub-attributes mapped internally) |
| `DimIncidentContext` | 0 | 0.00% | All incidents possess complete Arrest/Domestic/Night flags |

## 6. Constellation Dual-Fact Consistency

| Constellation Comparison | Value | Consistency Status |
| :--- | :--- | :--- |
| Atomic Fact Incidents (Valid Community Areas) | 497,243 | Baseline |
| Aggregate Fact Incidents (`FactAreaDailyPublicSafety`) | 497,243 | **EXACT MATCH (PASSED (Exact Match))** |

## 7. Warehouse Table Summary

| Table Name | Entity Type | Record Count |
| :--- | :--- | :--- |
| `dw.DimDate` | Conformed Dimension | 732 |
| `dw.DimTime` | Conformed Dimension | 1,441 |
| `dw.DimCrimeType` | Dimension | 354 |
| `dw.DimLocation` | Dimension | 22,148 |
| `dw.DimIncidentContext` | Context Flag Dimension | 9 |
| `dw.FactCrimeIncident` | Transaction Fact Table | 497,919 |
| `dw.FactAreaDailyPublicSafety` | Aggregate Constellation Fact | 53,935 |
