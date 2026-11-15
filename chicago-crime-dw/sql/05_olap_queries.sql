-- ====================================================================
-- Script 05: Dimensional OLAP Queries and Mandatory Business Analysis
-- Implements Roll-Up, Drill-Down, Slice, Dice, Pivot, CUBE / GROUPING SETS,
-- and queries answering all 10 mandatory business analysis questions.
-- ====================================================================

-- 1. ROLL-UP: Multi-Level Temporal Roll-up (Month -> Quarter -> Year -> Grand Total)
SELECT 
        d.Year,
        d.Quarter,
        d.Month,
        COUNT(f.IncidentKey) AS TotalIncidents,
        SUM(f.ArrestCount) AS TotalArrests,
        ROUND((SUM(f.ArrestCount)::NUMERIC / COUNT(f.IncidentKey)::NUMERIC) * 100.0, 2) AS ArrestRate
    FROM dw.FactCrimeIncident f
    JOIN dw.DimDate d ON f.DateKey = d.DateKey
    GROUP BY ROLLUP (d.Year, d.Quarter, d.Month)
    ORDER BY d.Year NULLS LAST, d.Quarter NULLS LAST, d.Month NULLS LAST;;

-- 2. DRILL-DOWN: Temporal Drill-down (Month -> Day -> Hour during July 4th Peak Window)
SELECT 
        d.Month,
        d.Day,
        t.Hour,
        COUNT(f.IncidentKey) AS IncidentVolume,
        SUM(f.ArrestCount) AS Arrests,
        SUM(f.DomesticCount) AS DomesticCrimes
    FROM dw.FactCrimeIncident f
    JOIN dw.DimDate d ON f.DateKey = d.DateKey
    JOIN dw.DimTime t ON f.TimeKey = t.TimeKey
    WHERE d.Year = 2024 AND d.Month = 7 AND d.Day IN (4, 5) -- July 4th Holiday Drill-Down
    GROUP BY d.Month, d.Day, t.Hour
    ORDER BY d.Month, d.Day, t.Hour;;

-- 3. SLICE: Single-Dimension Filter (Harrison District 011 Crime Breakdown)
SELECT 
        c.CrimeCategoryGroup,
        c.PrimaryType,
        COUNT(f.IncidentKey) AS IncidentsInDistrict11,
        SUM(f.ArrestCount) AS Arrests,
        ROUND((SUM(f.ArrestCount)::NUMERIC / COUNT(f.IncidentKey)::NUMERIC) * 100.0, 2) AS ArrestRate
    FROM dw.FactCrimeIncident f
    JOIN dw.DimLocation l ON f.LocationKey = l.LocationKey
    JOIN dw.DimCrimeType c ON f.CrimeTypeKey = c.CrimeTypeKey
    WHERE l.District = '011' -- Harrison District Slice
    GROUP BY c.CrimeCategoryGroup, c.PrimaryType
    ORDER BY IncidentsInDistrict11 DESC
    LIMIT 10;;

-- 4. DICE: Multi-Dimensional Sub-Cube (Districts 007, 011, 015 x Night/Evening x Violent/Property)
SELECT 
        l.District,
        c.CrimeCategoryGroup,
        t.TimeBand,
        COUNT(f.IncidentKey) AS IncidentCount,
        SUM(f.ArrestCount) AS Arrests,
        ROUND((SUM(f.ArrestCount)::NUMERIC / COUNT(f.IncidentKey)::NUMERIC) * 100.0, 2) AS ArrestRate
    FROM dw.FactCrimeIncident f
    JOIN dw.DimLocation l ON f.LocationKey = l.LocationKey
    JOIN dw.DimCrimeType c ON f.CrimeTypeKey = c.CrimeTypeKey
    JOIN dw.DimTime t ON f.TimeKey = t.TimeKey
    WHERE l.District IN ('007', '011', '015') 
      AND t.TimeBand IN ('Night', 'Evening')
      AND c.CrimeCategoryGroup IN ('Violent Crime', 'Property Crime')
    GROUP BY l.District, c.CrimeCategoryGroup, t.TimeBand
    ORDER BY l.District, IncidentCount DESC;;

-- 5. PIVOT: 2D Matrix Cross-Tabulation (Hour of Day x Day of Week)
SELECT 
        t.Hour,
        COUNT(f.IncidentKey) FILTER (WHERE d.DayOfWeek = 1) AS Mon,
        COUNT(f.IncidentKey) FILTER (WHERE d.DayOfWeek = 2) AS Tue,
        COUNT(f.IncidentKey) FILTER (WHERE d.DayOfWeek = 3) AS Wed,
        COUNT(f.IncidentKey) FILTER (WHERE d.DayOfWeek = 4) AS Thu,
        COUNT(f.IncidentKey) FILTER (WHERE d.DayOfWeek = 5) AS Fri,
        COUNT(f.IncidentKey) FILTER (WHERE d.DayOfWeek = 6) AS Sat,
        COUNT(f.IncidentKey) FILTER (WHERE d.DayOfWeek = 7) AS Sun,
        COUNT(f.IncidentKey) AS TotalHourlyVolume
    FROM dw.FactCrimeIncident f
    JOIN dw.DimDate d ON f.DateKey = d.DateKey
    JOIN dw.DimTime t ON f.TimeKey = t.TimeKey
    GROUP BY t.Hour
    ORDER BY t.Hour;;

-- 6. CUBE / GROUPING SETS: Multi-Grain Subtotal Exploration
SELECT 
        d.Year,
        l.District,
        c.CrimeCategoryGroup,
        COUNT(f.IncidentKey) AS IncidentCount,
        SUM(f.ArrestCount) AS ArrestCount
    FROM dw.FactCrimeIncident f
    JOIN dw.DimDate d ON f.DateKey = d.DateKey
    JOIN dw.DimLocation l ON f.LocationKey = l.LocationKey
    JOIN dw.DimCrimeType c ON f.CrimeTypeKey = c.CrimeTypeKey
    WHERE l.District IN ('001', '011') AND d.Year = 2024
    GROUP BY GROUPING SETS (
        (d.Year, l.District, c.CrimeCategoryGroup),
        (d.Year, l.District),
        (d.Year, c.CrimeCategoryGroup),
        (d.Year),
        ()
    )
    ORDER BY d.Year NULLS LAST, l.District NULLS LAST, c.CrimeCategoryGroup NULLS LAST;;

-- --------------------------------------------------------------------
-- 10 MANDATORY BUSINESS QUESTIONS (FROM SPECIFICATION)
-- --------------------------------------------------------------------

-- BQ1: Incident Volume Analysis
SELECT 
        'Temporal Volumes' AS MetricLevel,
        (SELECT COUNT(DISTINCT DateKey) FROM dw.FactCrimeIncident) AS TotalDays,
        (SELECT ROUND(AVG(cnt), 2) FROM (SELECT COUNT(*) AS cnt FROM dw.FactCrimeIncident GROUP BY DateKey) d) AS AvgDailyIncidents,
        (SELECT ROUND(AVG(cnt), 2) FROM (SELECT COUNT(*) AS cnt FROM dw.FactCrimeIncident GROUP BY DateKey, TimeKey) h) AS AvgHourlyIncidents,
        (SELECT MAX(cnt) FROM (SELECT COUNT(*) AS cnt FROM dw.FactCrimeIncident GROUP BY DateKey) d) AS MaxDayIncidents,
        (SELECT MIN(cnt) FROM (SELECT COUNT(*) AS cnt FROM dw.FactCrimeIncident GROUP BY DateKey) d) AS MinDayIncidents;;

-- BQ2: Most Common Primary Crime Types
SELECT 
        c.PrimaryType,
        c.CrimeCategoryGroup,
        COUNT(f.IncidentKey) AS TotalCount,
        ROUND((COUNT(f.IncidentKey)::NUMERIC / 497919.0) * 100.0, 2) AS PctShare,
        SUM(f.ArrestCount) AS Arrests,
        ROUND((SUM(f.ArrestCount)::NUMERIC / COUNT(f.IncidentKey)::NUMERIC) * 100.0, 2) AS ArrestRate
    FROM dw.FactCrimeIncident f
    JOIN dw.DimCrimeType c ON f.CrimeTypeKey = c.CrimeTypeKey
    GROUP BY c.PrimaryType, c.CrimeCategoryGroup
    ORDER BY TotalCount DESC
    LIMIT 10;;

-- BQ3: Districts and Community Areas with Highest Incident Volume
SELECT 
        l.District,
        COUNT(f.IncidentKey) AS TotalIncidents,
        SUM(f.ArrestCount) AS Arrests,
        ROUND((SUM(f.ArrestCount)::NUMERIC / COUNT(f.IncidentKey)::NUMERIC) * 100.0, 2) AS ArrestRate,
        SUM(f.DomesticCount) AS DomesticCount
    FROM dw.FactCrimeIncident f
    JOIN dw.DimLocation l ON f.LocationKey = l.LocationKey
    GROUP BY l.District
    ORDER BY TotalIncidents DESC
    LIMIT 5;;

SELECT 
        l.CommunityArea,
        COUNT(f.IncidentKey) AS TotalIncidents,
        SUM(f.ArrestCount) AS Arrests,
        ROUND((SUM(f.ArrestCount)::NUMERIC / COUNT(f.IncidentKey)::NUMERIC) * 100.0, 2) AS ArrestRate
    FROM dw.FactCrimeIncident f
    JOIN dw.DimLocation l ON f.LocationKey = l.LocationKey
    WHERE l.CommunityArea > 0
    GROUP BY l.CommunityArea
    ORDER BY TotalIncidents DESC
    LIMIT 5;;

-- BQ4: Incident Breakdown by Location Description
SELECT 
        l.LocationGroup,
        l.LocationDescription,
        COUNT(f.IncidentKey) AS IncidentVolume,
        ROUND((COUNT(f.IncidentKey)::NUMERIC / 497919.0) * 100.0, 2) AS PctShare,
        SUM(f.ArrestCount) AS Arrests,
        ROUND((SUM(f.ArrestCount)::NUMERIC / COUNT(f.IncidentKey)::NUMERIC) * 100.0, 2) AS ArrestRate
    FROM dw.FactCrimeIncident f
    JOIN dw.DimLocation l ON f.LocationKey = l.LocationKey
    GROUP BY l.LocationGroup, l.LocationDescription
    ORDER BY IncidentVolume DESC
    LIMIT 10;;

-- BQ5: Arrest vs. Non-Arrest Pattern Comparison
SELECT 
        ctx.ArrestDescription,
        COUNT(f.IncidentKey) AS IncidentCount,
        ROUND((COUNT(f.IncidentKey)::NUMERIC / 497919.0) * 100.0, 2) AS PctShare,
        SUM(f.DomesticCount) AS DomesticIncidents,
        ROUND((SUM(f.DomesticCount)::NUMERIC / COUNT(f.IncidentKey)::NUMERIC) * 100.0, 2) AS DomesticPct,
        SUM(f.NightCount) AS NightIncidents,
        ROUND((SUM(f.NightCount)::NUMERIC / COUNT(f.IncidentKey)::NUMERIC) * 100.0, 2) AS NightPct
    FROM dw.FactCrimeIncident f
    JOIN dw.DimIncidentContext ctx ON f.ContextKey = ctx.ContextKey
    GROUP BY ctx.ArrestDescription;;

-- BQ6: Domestic vs. Non-Domestic Incident Comparison
SELECT 
        ctx.DomesticDescription,
        COUNT(f.IncidentKey) AS TotalCount,
        ROUND((COUNT(f.IncidentKey)::NUMERIC / 497919.0) * 100.0, 2) AS PctShare,
        SUM(f.ArrestCount) AS ArrestCount,
        ROUND((SUM(f.ArrestCount)::NUMERIC / COUNT(f.IncidentKey)::NUMERIC) * 100.0, 2) AS ArrestRate,
        SUM(f.NightCount) AS NightIncidents,
        ROUND((SUM(f.NightCount)::NUMERIC / COUNT(f.IncidentKey)::NUMERIC) * 100.0, 2) AS NightPct
    FROM dw.FactCrimeIncident f
    JOIN dw.DimIncidentContext ctx ON f.ContextKey = ctx.ContextKey
    GROUP BY ctx.DomesticDescription;;

-- BQ7: Peak Incident Operational TimeBands
SELECT 
        t.TimeBand,
        COUNT(f.IncidentKey) AS Incidents,
        ROUND((COUNT(f.IncidentKey)::NUMERIC / 497919.0) * 100.0, 2) AS PctShare,
        SUM(f.ArrestCount) AS Arrests,
        ROUND((SUM(f.ArrestCount)::NUMERIC / COUNT(f.IncidentKey)::NUMERIC) * 100.0, 2) AS ArrestRate
    FROM dw.FactCrimeIncident f
    JOIN dw.DimTime t ON f.TimeKey = t.TimeKey
    GROUP BY t.TimeBand
    ORDER BY Incidents DESC;;

-- BQ8: Spatio-Temporal Crime Concentrations (District x TimeBand)
SELECT 
        l.District,
        t.TimeBand,
        COUNT(f.IncidentKey) AS IncidentVolume,
        SUM(f.ArrestCount) AS Arrests
    FROM dw.FactCrimeIncident f
    JOIN dw.DimLocation l ON f.LocationKey = l.LocationKey
    JOIN dw.DimTime t ON f.TimeKey = t.TimeKey
    GROUP BY l.District, t.TimeBand
    ORDER BY IncidentVolume DESC
    LIMIT 10;;

-- BQ9: Frequent Combinations of Incident Characteristics
SELECT 
        c.CrimeCategoryGroup,
        l.LocationGroup,
        t.TimeBand,
        ctx.ArrestDescription,
        COUNT(f.IncidentKey) AS PatternCount,
        ROUND((COUNT(f.IncidentKey)::NUMERIC / 497919.0) * 100.0, 2) AS PctOfTotal
    FROM dw.FactCrimeIncident f
    JOIN dw.DimCrimeType c ON f.CrimeTypeKey = c.CrimeTypeKey
    JOIN dw.DimLocation l ON f.LocationKey = l.LocationKey
    JOIN dw.DimTime t ON f.TimeKey = t.TimeKey
    JOIN dw.DimIncidentContext ctx ON f.ContextKey = ctx.ContextKey
    GROUP BY c.CrimeCategoryGroup, l.LocationGroup, t.TimeBand, ctx.ArrestDescription
    ORDER BY PatternCount DESC
    LIMIT 10;;

-- BQ10: Daily Area Incident Prediction Target Profile
SELECT 
        'Regression Target (AreaDailyIncidentCount)' AS ModelProblem,
        COUNT(*) AS TotalSampleObservations,
        ROUND(AVG(TotalIncidentCount), 2) AS MeanDailyIncidents,
        MIN(TotalIncidentCount) AS MinIncidents,
        MAX(TotalIncidentCount) AS MaxIncidents,
        ROUND(STDDEV(TotalIncidentCount), 2) AS StdDevIncidents
    FROM dw.FactAreaDailyPublicSafety;;

