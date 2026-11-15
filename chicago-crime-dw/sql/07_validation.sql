-- ====================================================================
-- Script 07: Data Warehouse Reconciliation and Integrity Validation
-- Executes reconciliation audits, orphan foreign key checks, and measure totals.
-- ====================================================================

-- 1. Source vs Staging vs Fact Row Count Reconciliation
SELECT 
    'Staging vs Fact Row Count' AS audit_check,
    (SELECT COUNT(*) FROM staging.stg_crimes) AS staging_rows,
    (SELECT COUNT(*) FROM dw.FactCrimeIncident) AS fact_rows,
    CASE 
        WHEN (SELECT COUNT(*) FROM staging.stg_crimes) = (SELECT COUNT(*) FROM dw.FactCrimeIncident)
        THEN 'PASSED: Exact Match'
        ELSE 'FAILED: Discrepancy Detected'
    END AS reconciliation_status;

-- 2. Measure Totals Reconciliation
SELECT 
    'Measure Totals Verification' AS audit_check,
    (SELECT SUM(IncidentCount) FROM dw.FactCrimeIncident) AS total_incidents,
    (SELECT SUM(ArrestCount) FROM dw.FactCrimeIncident) AS total_arrests,
    (SELECT SUM(DomesticCount) FROM dw.FactCrimeIncident) AS total_domestic,
    (SELECT SUM(NightCount) FROM dw.FactCrimeIncident) AS total_night_incidents;

-- 3. Referential Integrity: Orphan Foreign Key Checks
SELECT 
    'Orphan Foreign Keys Audit' AS audit_check,
    (SELECT COUNT(*) FROM dw.FactCrimeIncident f LEFT JOIN dw.DimDate d ON f.DateKey = d.DateKey WHERE d.DateKey IS NULL) AS orphan_date_keys,
    (SELECT COUNT(*) FROM dw.FactCrimeIncident f LEFT JOIN dw.DimTime t ON f.TimeKey = t.TimeKey WHERE t.TimeKey IS NULL) AS orphan_time_keys,
    (SELECT COUNT(*) FROM dw.FactCrimeIncident f LEFT JOIN dw.DimCrimeType c ON f.CrimeTypeKey = c.CrimeTypeKey WHERE c.CrimeTypeKey IS NULL) AS orphan_crime_keys,
    (SELECT COUNT(*) FROM dw.FactCrimeIncident f LEFT JOIN dw.DimLocation l ON f.LocationKey = l.LocationKey WHERE l.LocationKey IS NULL) AS orphan_location_keys,
    (SELECT COUNT(*) FROM dw.FactCrimeIncident f LEFT JOIN dw.DimIncidentContext ctx ON f.ContextKey = ctx.ContextKey WHERE ctx.ContextKey IS NULL) AS orphan_context_keys;

-- 4. Unknown Member (-1) Usage Audit
SELECT 
    'Unknown Member Usage Audit' AS audit_check,
    (SELECT COUNT(*) FROM dw.FactCrimeIncident WHERE DateKey = -1) AS unknown_dates,
    (SELECT COUNT(*) FROM dw.FactCrimeIncident WHERE TimeKey = -1) AS unknown_times,
    (SELECT COUNT(*) FROM dw.FactCrimeIncident WHERE CrimeTypeKey = -1) AS unknown_crimes,
    (SELECT COUNT(*) FROM dw.FactCrimeIncident WHERE LocationKey = -1) AS unknown_locations,
    (SELECT COUNT(*) FROM dw.FactCrimeIncident WHERE ContextKey = -1) AS unknown_contexts;

-- 5. Fact Constellation (Fact 1 vs Fact 2) Consistency
SELECT 
    'Fact 1 vs Fact 2 Consistency (Valid Community Areas)' AS audit_check,
    (SELECT SUM(IncidentCount) FROM dw.FactCrimeIncident f JOIN dw.DimLocation l ON f.LocationKey = l.LocationKey WHERE l.CommunityArea > 0) AS fact1_valid_ca_incidents,
    (SELECT SUM(TotalIncidentCount) FROM dw.FactAreaDailyPublicSafety) AS fact2_total_incidents,
    CASE 
        WHEN (SELECT SUM(IncidentCount) FROM dw.FactCrimeIncident f JOIN dw.DimLocation l ON f.LocationKey = l.LocationKey WHERE l.CommunityArea > 0) =
             (SELECT SUM(TotalIncidentCount) FROM dw.FactAreaDailyPublicSafety)
        THEN 'PASSED: Constellation Facts Reconciled Exactly'
        ELSE 'FAILED: Discrepancy Detected'
    END AS constellation_status;
