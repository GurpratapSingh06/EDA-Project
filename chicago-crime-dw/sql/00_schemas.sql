-- ====================================================================
-- Script 00: Schema Initialization
-- Defines isolated schemas for staging, dimensional warehouse, and analytical marts
-- ====================================================================

CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS dw;
CREATE SCHEMA IF NOT EXISTS mart;

COMMENT ON SCHEMA staging IS 'Staging layer for landing raw source crime records and performing initial ingestion';
COMMENT ON SCHEMA dw IS 'Core dimensional data warehouse layer containing star and constellation facts and dimensions';
COMMENT ON SCHEMA mart IS 'Analytical data mart views and pre-aggregated structures feeding BI and ML';
