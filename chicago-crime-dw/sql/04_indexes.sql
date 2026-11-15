-- ====================================================================
-- Script 04: Analytical Indexes
-- B-Tree indexes on all dimension foreign keys, high-cardinality analytical attributes,
-- and composite indexes for multi-dimensional roll-up queries.
-- ====================================================================

-- Foreign Key Indexes on FactCrimeIncident
CREATE INDEX IF NOT EXISTS idx_fact_datekey ON dw.FactCrimeIncident(DateKey);
CREATE INDEX IF NOT EXISTS idx_fact_timekey ON dw.FactCrimeIncident(TimeKey);
CREATE INDEX IF NOT EXISTS idx_fact_crimetypekey ON dw.FactCrimeIncident(CrimeTypeKey);
CREATE INDEX IF NOT EXISTS idx_fact_locationkey ON dw.FactCrimeIncident(LocationKey);
CREATE INDEX IF NOT EXISTS idx_fact_contextkey ON dw.FactCrimeIncident(ContextKey);
CREATE INDEX IF NOT EXISTS idx_fact_incidentid ON dw.FactCrimeIncident(IncidentID);

-- Composite Index for Common Analytical Slices
CREATE INDEX IF NOT EXISTS idx_fact_date_crime ON dw.FactCrimeIncident(DateKey, CrimeTypeKey);
CREATE INDEX IF NOT EXISTS idx_fact_date_location ON dw.FactCrimeIncident(DateKey, LocationKey);

-- Dimension Lookup Indexes
CREATE INDEX IF NOT EXISTS idx_dimdate_ym ON dw.DimDate(Year, Month);
CREATE INDEX IF NOT EXISTS idx_dimdate_quarter ON dw.DimDate(Quarter);
CREATE INDEX IF NOT EXISTS idx_dimcrime_primary ON dw.DimCrimeType(PrimaryType);
CREATE INDEX IF NOT EXISTS idx_dimcrime_category ON dw.DimCrimeType(CrimeCategoryGroup);
CREATE INDEX IF NOT EXISTS idx_dimloc_district ON dw.DimLocation(District);
CREATE INDEX IF NOT EXISTS idx_dimloc_community ON dw.DimLocation(CommunityArea);
CREATE INDEX IF NOT EXISTS idx_dimloc_group ON dw.DimLocation(LocationGroup);

-- FactAreaDailyPublicSafety Indexes
CREATE INDEX IF NOT EXISTS idx_factarea_comm_date ON dw.FactAreaDailyPublicSafety(CommunityArea, DateKey);
CREATE INDEX IF NOT EXISTS idx_factarea_date ON dw.FactAreaDailyPublicSafety(DateKey);
