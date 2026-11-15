-- ====================================================================
-- Script 01: Staging Layer DDL
-- Landing table for raw extracted Chicago Police Department crime records
-- ====================================================================

DROP TABLE IF EXISTS staging.stg_crimes CASCADE;

CREATE TABLE staging.stg_crimes (
    id BIGINT,
    case_number VARCHAR(20),
    date TIMESTAMP,
    block VARCHAR(100),
    iucr VARCHAR(10),
    primary_type VARCHAR(60),
    description VARCHAR(100),
    location_description VARCHAR(100),
    arrest BOOLEAN,
    domestic BOOLEAN,
    beat VARCHAR(10),
    district VARCHAR(10),
    ward INTEGER,
    community_area INTEGER,
    fbi_code VARCHAR(10),
    x_coordinate DOUBLE PRECISION,
    y_coordinate DOUBLE PRECISION,
    year INTEGER,
    updated_on TIMESTAMP,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    -- Audit fields
    batch_id VARCHAR(50) DEFAULT 'INITIAL_LOAD_2024_2025',
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_stg_id ON staging.stg_crimes(id);
CREATE INDEX idx_stg_date ON staging.stg_crimes(date);
CREATE INDEX idx_stg_batch ON staging.stg_crimes(batch_id);

COMMENT ON TABLE staging.stg_crimes IS 'Transient staging table holding raw CPD crime records during ETL phases';
