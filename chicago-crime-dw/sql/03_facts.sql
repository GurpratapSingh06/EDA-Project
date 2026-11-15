-- ====================================================================
-- Script 03: Fact Tables DDL (Fact Constellation)
-- Implements FactCrimeIncident (atomic incident grain) and 
-- FactAreaDailyPublicSafety (Community Area x Date grain)
-- ====================================================================

-- 1. Primary Fact: FactCrimeIncident
DROP TABLE IF EXISTS dw.FactCrimeIncident CASCADE;

CREATE TABLE dw.FactCrimeIncident (
    IncidentKey BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    -- Conformed Foreign Keys
    DateKey INTEGER NOT NULL REFERENCES dw.DimDate(DateKey),
    TimeKey INTEGER NOT NULL REFERENCES dw.DimTime(TimeKey),
    CrimeTypeKey INTEGER NOT NULL REFERENCES dw.DimCrimeType(CrimeTypeKey),
    LocationKey INTEGER NOT NULL REFERENCES dw.DimLocation(LocationKey),
    ContextKey INTEGER NOT NULL REFERENCES dw.DimIncidentContext(ContextKey),
    -- Degenerate Dimensions
    IncidentID BIGINT NOT NULL,
    CaseNumber VARCHAR(20) NOT NULL,
    -- Additive Measures
    IncidentCount INTEGER DEFAULT 1 NOT NULL,
    ArrestCount INTEGER DEFAULT 0 NOT NULL,
    DomesticCount INTEGER DEFAULT 0 NOT NULL,
    NightCount INTEGER DEFAULT 0 NOT NULL,
    -- Audit Tracking
    batch_id VARCHAR(50) DEFAULT 'INITIAL_LOAD',
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Constellation Fact: FactAreaDailyPublicSafety
DROP TABLE IF EXISTS dw.FactAreaDailyPublicSafety CASCADE;

CREATE TABLE dw.FactAreaDailyPublicSafety (
    AreaDailyKey BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    -- Conformed Foreign Keys
    DateKey INTEGER NOT NULL REFERENCES dw.DimDate(DateKey),
    CommunityArea INTEGER NOT NULL,
    -- Aggregated Measures
    TotalIncidentCount INTEGER NOT NULL,
    TotalArrestCount INTEGER NOT NULL,
    TotalDomesticCount INTEGER NOT NULL,
    TotalNightCount INTEGER NOT NULL,
    DistinctCrimeTypes INTEGER NOT NULL,
    ArrestRate NUMERIC(5, 2) NOT NULL,
    DomesticRate NUMERIC(5, 2) NOT NULL,
    -- Audit Tracking
    batch_id VARCHAR(50) DEFAULT 'INITIAL_LOAD',
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_area_date UNIQUE (DateKey, CommunityArea)
);

COMMENT ON TABLE dw.FactCrimeIncident IS 'Atomic transaction fact table storing one row per reported crime incident';
COMMENT ON TABLE dw.FactAreaDailyPublicSafety IS 'Aggregated periodic snapshot fact table storing daily public safety metrics per Community Area';
