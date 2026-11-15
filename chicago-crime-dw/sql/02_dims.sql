-- ====================================================================
-- Script 02: Dimension Tables DDL
-- Implements conforming dimensions with surrogate keys, Unknown members (-1),
-- and audit columns across all dimension entities.
-- ====================================================================

-- 1. DimDate
DROP TABLE IF EXISTS dw.DimDate CASCADE;
CREATE TABLE dw.DimDate (
    DateKey INTEGER PRIMARY KEY, -- YYYYMMDD or -1
    FullDate DATE,
    Day INTEGER,
    DayName VARCHAR(15),
    DayOfWeek INTEGER, -- 1=Monday, 7=Sunday
    Week INTEGER,
    Month INTEGER,
    MonthName VARCHAR(15),
    Quarter INTEGER,
    Year INTEGER,
    IsWeekend INTEGER, -- 1=Weekend, 0=Weekday
    batch_id VARCHAR(50) DEFAULT 'INITIAL_LOAD',
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert Unknown Member for DimDate
INSERT INTO dw.DimDate (DateKey, FullDate, Day, DayName, DayOfWeek, Week, Month, MonthName, Quarter, Year, IsWeekend, batch_id)
VALUES (-1, '1900-01-01', -1, 'Unknown', -1, -1, -1, 'Unknown', -1, -1, 0, 'SYSTEM_INIT')
ON CONFLICT (DateKey) DO NOTHING;


-- 2. DimTime
DROP TABLE IF EXISTS dw.DimTime CASCADE;
CREATE TABLE dw.DimTime (
    TimeKey INTEGER PRIMARY KEY, -- HHMM format (0 to 2359) or -1
    Hour INTEGER,
    Minute INTEGER,
    TimeBand VARCHAR(20), -- Night (21-05), Morning (05-12), Afternoon (12-17), Evening (17-21)
    batch_id VARCHAR(50) DEFAULT 'INITIAL_LOAD',
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert Unknown Member for DimTime
INSERT INTO dw.DimTime (TimeKey, Hour, Minute, TimeBand, batch_id)
VALUES (-1, -1, -1, 'Unknown', 'SYSTEM_INIT')
ON CONFLICT (TimeKey) DO NOTHING;


-- 3. DimCrimeType
DROP TABLE IF EXISTS dw.DimCrimeType CASCADE;
CREATE TABLE dw.DimCrimeType (
    CrimeTypeKey INTEGER PRIMARY KEY,
    IUCR VARCHAR(10) NOT NULL,
    PrimaryType VARCHAR(60) NOT NULL,
    Description VARCHAR(100) NOT NULL,
    FBICode VARCHAR(10),
    CrimeCategoryGroup VARCHAR(40),
    batch_id VARCHAR(50) DEFAULT 'INITIAL_LOAD',
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_dim_crimetype_nat ON dw.DimCrimeType(IUCR, PrimaryType, Description, FBICode);

-- Insert Unknown Member for DimCrimeType
INSERT INTO dw.DimCrimeType (CrimeTypeKey, IUCR, PrimaryType, Description, FBICode, CrimeCategoryGroup, batch_id)
VALUES (-1, 'UNKNOWN', 'UNKNOWN', 'UNKNOWN OFFENSE', 'UNKNOWN', 'Other Offenses', 'SYSTEM_INIT')
ON CONFLICT (CrimeTypeKey) DO NOTHING;


-- 4. DimLocation
DROP TABLE IF EXISTS dw.DimLocation CASCADE;
CREATE TABLE dw.DimLocation (
    LocationKey INTEGER PRIMARY KEY,
    District VARCHAR(10) NOT NULL,
    Beat VARCHAR(10) NOT NULL,
    Ward INTEGER NOT NULL,
    CommunityArea INTEGER NOT NULL,
    LocationDescription VARCHAR(100) NOT NULL,
    LocationGroup VARCHAR(40),
    LatitudeBand VARCHAR(40),
    LongitudeBand VARCHAR(40),
    batch_id VARCHAR(50) DEFAULT 'INITIAL_LOAD',
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_dim_location_nat ON dw.DimLocation(District, Beat, Ward, CommunityArea, LocationDescription, LatitudeBand, LongitudeBand);

-- Insert Unknown Member for DimLocation
INSERT INTO dw.DimLocation (LocationKey, District, Beat, Ward, CommunityArea, LocationDescription, LocationGroup, LatitudeBand, LongitudeBand, batch_id)
VALUES (-1, 'UNKNOWN', 'UNKNOWN', -1, -1, 'UNKNOWN LOCATION', 'Other/Unknown', 'Unknown', 'Unknown', 'SYSTEM_INIT')
ON CONFLICT (LocationKey) DO NOTHING;


-- 5. DimIncidentContext
DROP TABLE IF EXISTS dw.DimIncidentContext CASCADE;
CREATE TABLE dw.DimIncidentContext (
    ContextKey INTEGER PRIMARY KEY,
    ArrestFlag INTEGER NOT NULL, -- 0 or 1
    DomesticFlag INTEGER NOT NULL, -- 0 or 1
    NightFlag INTEGER NOT NULL, -- 0 or 1
    ArrestDescription VARCHAR(20),
    DomesticDescription VARCHAR(20),
    NightDescription VARCHAR(20),
    batch_id VARCHAR(50) DEFAULT 'INITIAL_LOAD',
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Pre-populate all 8 valid combinations plus Unknown (-1)
INSERT INTO dw.DimIncidentContext (ContextKey, ArrestFlag, DomesticFlag, NightFlag, ArrestDescription, DomesticDescription, NightDescription, batch_id)
VALUES 
    (-1, -1, -1, -1, 'Unknown', 'Unknown', 'Unknown', 'SYSTEM_INIT'),
    (1,  0, 0, 0, 'No Arrest', 'Non-Domestic', 'Day Incident', 'SYSTEM_INIT'),
    (2,  1, 0, 0, 'Arrest Made', 'Non-Domestic', 'Day Incident', 'SYSTEM_INIT'),
    (3,  0, 1, 0, 'No Arrest', 'Domestic Related', 'Day Incident', 'SYSTEM_INIT'),
    (4,  1, 1, 0, 'Arrest Made', 'Domestic Related', 'Day Incident', 'SYSTEM_INIT'),
    (5,  0, 0, 1, 'No Arrest', 'Non-Domestic', 'Night Incident', 'SYSTEM_INIT'),
    (6,  1, 0, 1, 'Arrest Made', 'Non-Domestic', 'Night Incident', 'SYSTEM_INIT'),
    (7,  0, 1, 1, 'No Arrest', 'Domestic Related', 'Night Incident', 'SYSTEM_INIT'),
    (8,  1, 1, 1, 'Arrest Made', 'Domestic Related', 'Night Incident', 'SYSTEM_INIT')
ON CONFLICT (ContextKey) DO NOTHING;

COMMENT ON TABLE dw.DimDate IS 'Conformed Date Dimension covering the 2024-2025 analytical period';
COMMENT ON TABLE dw.DimTime IS 'Time-of-day dimension with 1-minute granularity and defined operational TimeBands';
COMMENT ON TABLE dw.DimCrimeType IS 'Crime classification dimension covering IUCR codes, Primary Offenses, and FBI codes';
COMMENT ON TABLE dw.DimLocation IS 'Administrative and spatial location dimension covering Beat, District, Ward, and Community Area';
COMMENT ON TABLE dw.DimIncidentContext IS 'Contextual flag dimension capturing Arrest, Domestic, and Night status combinations';
