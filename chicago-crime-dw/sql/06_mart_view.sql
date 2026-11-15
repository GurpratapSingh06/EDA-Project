-- ====================================================================
-- Script 06: Analytical Mart View DDL
-- Creates mart.PublicSafetyAnalyticsMart as a certified SQL view over the DW facts and dimensions.
-- All machine learning models (Regression, Association, Decision Tree) query exclusively from this view.
-- ====================================================================

CREATE OR REPLACE VIEW mart.PublicSafetyAnalyticsMart AS
SELECT 
    f.IncidentKey,
    f.IncidentID,
    f.CaseNumber,
    d.FullDate AS Date,
    d.Year,
    d.Quarter,
    d.Month,
    d.MonthName,
    d.Day,
    d.DayName,
    d.DayOfWeek,
    d.IsWeekend,
    t.Hour,
    t.Minute,
    t.TimeBand,
    c.CrimeTypeKey,
    c.IUCR,
    c.PrimaryType,
    c.Description,
    c.FBICode,
    c.CrimeCategoryGroup,
    l.LocationKey,
    l.District,
    l.Beat,
    l.Ward,
    l.CommunityArea,
    l.LocationDescription,
    l.LocationGroup,
    l.LatitudeBand,
    l.LongitudeBand,
    f.ArrestCount AS ArrestFlag,
    f.DomesticCount AS DomesticFlag,
    f.NightCount AS IsNightIncident,
    f.IncidentCount
FROM dw.FactCrimeIncident f
JOIN dw.DimDate d ON f.DateKey = d.DateKey
JOIN dw.DimTime t ON f.TimeKey = t.TimeKey
JOIN dw.DimCrimeType c ON f.CrimeTypeKey = c.CrimeTypeKey
JOIN dw.DimLocation l ON f.LocationKey = l.LocationKey
JOIN dw.DimIncidentContext ctx ON f.ContextKey = ctx.ContextKey;

COMMENT ON VIEW mart.PublicSafetyAnalyticsMart IS 'Certified Analytical Mart view joining atomic incident facts with conformed dimensions for BI reporting and predictive ML modeling';
