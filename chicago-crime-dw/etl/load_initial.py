"""
Initial Warehouse ETL Loading Script
Period: January 1, 2024 to November 30, 2025 (480,310 records)
Holds back December 2025 for incremental demonstration.

Execution Flow:
1. Initialize schemas, staging, dimension, and fact DDLs.
2. Populate DimDate (2024-01-01 to 2025-12-31).
3. Populate DimTime (00:00 to 23:59).
4. Stage initial data into staging.stg_crimes.
5. Populate DimCrimeType from initial staging.
6. Populate DimLocation from initial staging.
7. Load dw.FactCrimeIncident with surrogate key lookups.
8. Load dw.FactAreaDailyPublicSafety aggregated fact.
9. Verify initial load counts and integrity.
"""

import os
import sys
import time
import io
import datetime
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

DB_PARAMS = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "root",
    "dbname": "chicago_crime_dw"
}

def execute_sql_file(conn, filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        sql = f.read()
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    print(f"Executed SQL: {os.path.basename(filepath)}")

def populate_dim_date(conn):
    print("Populating DimDate for 2024–2025...")
    start_date = datetime.date(2024, 1, 1)
    end_date = datetime.date(2025, 12, 31)
    delta = datetime.timedelta(days=1)
    
    cur_date = start_date
    rows = []
    while cur_date <= end_date:
        date_key = int(cur_date.strftime("%Y%m%d"))
        day = cur_date.day
        day_name = cur_date.strftime("%A")
        day_of_week = cur_date.isoweekday() # 1=Mon, 7=Sun
        week = cur_date.isocalendar()[1]
        month = cur_date.month
        month_name = cur_date.strftime("%B")
        quarter = (month - 1) // 3 + 1
        year = cur_date.year
        is_weekend = 1 if day_of_week in [6, 7] else 0
        rows.append((date_key, cur_date, day, day_name, day_of_week, week, month, month_name, quarter, year, is_weekend, "INITIAL_LOAD"))
        cur_date += delta
        
    insert_sql = """
    INSERT INTO dw.DimDate (DateKey, FullDate, Day, DayName, DayOfWeek, Week, Month, MonthName, Quarter, Year, IsWeekend, batch_id)
    VALUES %s
    ON CONFLICT (DateKey) DO NOTHING;
    """
    with conn.cursor() as cur:
        execute_values(cur, insert_sql, rows)
    conn.commit()
    print(f"DimDate populated with {len(rows)} calendar dates.")

def populate_dim_time(conn):
    print("Populating DimTime (1440 minutes)...")
    rows = []
    for h in range(24):
        for m in range(60):
            time_key = h * 100 + m
            if h in [21, 22, 23, 0, 1, 2, 3, 4]:
                tb = "Night"
            elif h in [5, 6, 7, 8, 9, 10, 11]:
                tb = "Morning"
            elif h in [12, 13, 14, 15, 16]:
                tb = "Afternoon"
            else:
                tb = "Evening"
            rows.append((time_key, h, m, tb, "INITIAL_LOAD"))
            
    insert_sql = """
    INSERT INTO dw.DimTime (TimeKey, Hour, Minute, TimeBand, batch_id)
    VALUES %s
    ON CONFLICT (TimeKey) DO NOTHING;
    """
    with conn.cursor() as cur:
        execute_values(cur, insert_sql, rows)
    conn.commit()
    print(f"DimTime populated with {len(rows)} minutes.")

def run_initial_load():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    curated_path = os.path.join(base_dir, "data", "curated", "crimes_curated.csv")
    sql_dir = os.path.join(base_dir, "sql")

    print("=== Starting Initial Warehouse Bulk Load (Jan 2024 to Nov 2025) ===")
    t0 = time.time()
    conn = psycopg2.connect(**DB_PARAMS)

    # 1. Execute DDLs
    execute_sql_file(conn, os.path.join(sql_dir, "00_schemas.sql"))
    execute_sql_file(conn, os.path.join(sql_dir, "01_staging.sql"))
    execute_sql_file(conn, os.path.join(sql_dir, "02_dims.sql"))
    execute_sql_file(conn, os.path.join(sql_dir, "03_facts.sql"))

    # 2. Populate Static Dimensions
    populate_dim_date(conn)
    populate_dim_time(conn)

    # 3. Read Curated Data & Filter Initial Period (Exclude Dec 2025)
    print("Loading curated dataset...")
    df = pd.read_csv(curated_path, low_memory=False)
    initial_mask = (df["year"] == 2024) | ((df["year"] == 2025) & (df["month"] <= 11))
    df_init = df[initial_mask].copy()
    print(f"Filtered Initial Load dataset: {len(df_init):,} rows (held back {len(df) - len(df_init):,} rows for Dec 2025 incremental load).")

    # 4. Fast Load into staging.stg_crimes via COPY
    print("Loading staging.stg_crimes via PostgreSQL COPY...")
    stg_cols = [
        "id", "case_number", "date", "block", "iucr", "primary_type", "description",
        "location_description", "arrest", "domestic", "beat", "district", "ward",
        "community_area", "fbi_code", "x_coordinate", "y_coordinate", "year",
        "updated_on", "latitude", "longitude"
    ]
    df_stg = df_init[stg_cols].copy()
    df_stg["batch_id"] = "INITIAL_LOAD_2024_NOV2025"
    
    s_buf = io.StringIO()
    df_stg.to_csv(s_buf, index=False, header=False, sep="\t", na_rep="\\N")
    s_buf.seek(0)
    
    with conn.cursor() as cur:
        cur.copy_expert(
            f"COPY staging.stg_crimes ({', '.join(stg_cols + ['batch_id'])}) FROM STDIN WITH (FORMAT csv, DELIMITER E'\\t', NULL E'\\\\N');",
            s_buf
        )
    conn.commit()
    print(f"Staged {len(df_stg):,} initial rows.")

    # 5. Populate DimCrimeType from Staging
    print("Populating DimCrimeType from initial staging...")
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO dw.DimCrimeType (CrimeTypeKey, IUCR, PrimaryType, Description, FBICode, CrimeCategoryGroup, batch_id)
        SELECT 
            ROW_NUMBER() OVER (ORDER BY iucr, primary_type, description, fbi_code) AS CrimeTypeKey,
            iucr, primary_type, description, fbi_code,
            CASE 
                WHEN primary_type IN ('HOMICIDE', 'CRIMINAL SEXUAL ASSAULT', 'ROBBERY', 'ASSAULT', 'BATTERY', 'KIDNAPPING', 'INTIMIDATION', 'STALKING') THEN 'Violent Crime'
                WHEN primary_type IN ('THEFT', 'BURGLARY', 'MOTOR VEHICLE THEFT', 'ARSON', 'DECEPTIVE PRACTICE', 'CRIMINAL DAMAGE', 'CRIMINAL TRESPASS') THEN 'Property Crime'
                WHEN primary_type IN ('NARCOTICS', 'OTHER NARCOTIC VIOLATION', 'LIQUOR LAW VIOLATION') THEN 'Substance Offense'
                WHEN primary_type IN ('WEAPONS VIOLATION', 'PUBLIC PEACE VIOLATION', 'INTERFERENCE WITH PUBLIC OFFICER', 'CONCEALED CARRY LICENSE VIOLATION', 'PROSTITUTION', 'GAMBLING', 'PUBLIC INDECENCY', 'OBSCENITY') THEN 'Public Order & Weapons'
                ELSE 'Other Offenses'
            END AS CrimeCategoryGroup,
            'INITIAL_LOAD'
        FROM (
            SELECT DISTINCT iucr, primary_type, description, fbi_code 
            FROM staging.stg_crimes 
            WHERE batch_id = 'INITIAL_LOAD_2024_NOV2025'
        ) sub
        ON CONFLICT (IUCR, PrimaryType, Description, FBICode) DO NOTHING;
        """)
        cur.execute("SELECT COUNT(*) FROM dw.DimCrimeType WHERE CrimeTypeKey > 0;")
        ct_count = cur.fetchone()[0]
    conn.commit()
    print(f"DimCrimeType loaded: {ct_count} distinct crime classifications.")

    # 6. Populate DimLocation from Staging
    print("Populating DimLocation from initial staging...")
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO dw.DimLocation (LocationKey, District, Beat, Ward, CommunityArea, LocationDescription, LocationGroup, LatitudeBand, LongitudeBand, batch_id)
        SELECT 
            ROW_NUMBER() OVER (ORDER BY district, beat, ward, community_area, location_description) AS LocationKey,
            district, beat, ward, community_area, location_description,
            CASE 
                WHEN location_description ILIKE ANY(ARRAY['%STREET%', '%SIDEWALK%', '%ALLEY%', '%PARK%', '%HIGHWAY%', '%EXPRESSWAY%', '%LOT%', '%DRIVEWAY%']) THEN 'Street & Outdoor'
                WHEN location_description ILIKE ANY(ARRAY['%RESIDENCE%', '%APARTMENT%', '%PORCH%', '%HALLWAY%', '%HOUSE%']) THEN 'Residential'
                WHEN location_description ILIKE ANY(ARRAY['%STORE%', '%COMMERCIAL%', '%RESTAURANT%', '%BAR%', '%TAVERN%', '%GAS STATION%', '%BANK%', '%HOTEL%', '%MALL%', '%GROCERY%']) THEN 'Commercial & Retail'
                WHEN location_description ILIKE ANY(ARRAY['%CTA%', '%BUS%', '%TRAIN%', '%PLATFORM%', '%AIRPORT%', '%VEHICLE%', '%TAXI%']) THEN 'Transit & Vehicles'
                WHEN location_description ILIKE ANY(ARRAY['%SCHOOL%', '%HOSPITAL%', '%POLICE%', '%GOVERNMENT%', '%CHURCH%', '%LIBRARY%', '%COLLEGE%', '%JAIL%']) THEN 'Public Facility / Institution'
                ELSE 'Other/Unknown'
            END AS LocationGroup,
            CASE 
                WHEN latitude IS NULL THEN 'Unknown'
                WHEN latitude < 41.78 THEN 'South Chicago (< 41.78 N)'
                WHEN latitude <= 41.88 THEN 'Central Chicago (41.78 - 41.88 N)'
                ELSE 'North Chicago (> 41.88 N)'
            END AS LatitudeBand,
            CASE 
                WHEN longitude IS NULL THEN 'Unknown'
                WHEN longitude < -87.72 THEN 'West Chicago (< -87.72 W)'
                WHEN longitude <= -87.64 THEN 'Central Chicago (-87.72 - -87.64 W)'
                ELSE 'East / Lakefront (> -87.64 W)'
            END AS LongitudeBand,
            'INITIAL_LOAD'
        FROM (
            SELECT DISTINCT district, beat, ward, community_area, location_description,
                   AVG(latitude) AS latitude, AVG(longitude) AS longitude
            FROM staging.stg_crimes 
            WHERE batch_id = 'INITIAL_LOAD_2024_NOV2025'
            GROUP BY district, beat, ward, community_area, location_description
        ) sub
        ON CONFLICT (District, Beat, Ward, CommunityArea, LocationDescription, LatitudeBand, LongitudeBand) DO NOTHING;
        """)
        cur.execute("SELECT COUNT(*) FROM dw.DimLocation WHERE LocationKey > 0;")
        loc_count = cur.fetchone()[0]
    conn.commit()
    print(f"DimLocation loaded: {loc_count} distinct geographic location points.")

    # 7. Load FactCrimeIncident from Staging with Dimension Lookups
    print("Loading FactCrimeIncident via SQL join lookups...")
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO dw.FactCrimeIncident (
            DateKey, TimeKey, CrimeTypeKey, LocationKey, ContextKey,
            IncidentID, CaseNumber, IncidentCount, ArrestCount, DomesticCount, NightCount, batch_id
        )
        SELECT 
            COALESCE(d.DateKey, -1) AS DateKey,
            COALESCE(t.TimeKey, -1) AS TimeKey,
            COALESCE(c.CrimeTypeKey, -1) AS CrimeTypeKey,
            COALESCE(l.LocationKey, -1) AS LocationKey,
            COALESCE(ctx.ContextKey, -1) AS ContextKey,
            s.id AS IncidentID,
            s.case_number AS CaseNumber,
            1 AS IncidentCount,
            CASE WHEN s.arrest = true THEN 1 ELSE 0 END AS ArrestCount,
            CASE WHEN s.domestic = true THEN 1 ELSE 0 END AS DomesticCount,
            CASE WHEN EXTRACT(HOUR FROM s.date) IN (21,22,23,0,1,2,3,4) THEN 1 ELSE 0 END AS NightCount,
            'INITIAL_LOAD_2024_NOV2025' AS batch_id
        FROM staging.stg_crimes s
        LEFT JOIN dw.DimDate d ON (TO_CHAR(s.date, 'YYYYMMDD')::INTEGER = d.DateKey)
        LEFT JOIN dw.DimTime t ON (EXTRACT(HOUR FROM s.date)::INTEGER * 100 + EXTRACT(MINUTE FROM s.date)::INTEGER = t.TimeKey)
        LEFT JOIN dw.DimCrimeType c ON (s.iucr = c.IUCR AND s.primary_type = c.PrimaryType AND s.description = c.Description AND s.fbi_code = c.FBICode)
        LEFT JOIN dw.DimLocation l ON (
            s.district = l.District AND s.beat = l.Beat AND s.ward = l.Ward AND s.community_area = l.CommunityArea AND s.location_description = l.LocationDescription
        )
        LEFT JOIN dw.DimIncidentContext ctx ON (
            (CASE WHEN s.arrest = true THEN 1 ELSE 0 END = ctx.ArrestFlag) AND
            (CASE WHEN s.domestic = true THEN 1 ELSE 0 END = ctx.DomesticFlag) AND
            (CASE WHEN EXTRACT(HOUR FROM s.date) IN (21,22,23,0,1,2,3,4) THEN 1 ELSE 0 END = ctx.NightFlag)
        )
        WHERE s.batch_id = 'INITIAL_LOAD_2024_NOV2025';
        """)
        cur.execute("SELECT COUNT(*) FROM dw.FactCrimeIncident;")
        fact_count = cur.fetchone()[0]
    conn.commit()
    print(f"FactCrimeIncident loaded: {fact_count:,} incident facts.")

    # 8. Load FactAreaDailyPublicSafety (Constellation Aggregate)
    print("Populating FactAreaDailyPublicSafety aggregated fact...")
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO dw.FactAreaDailyPublicSafety (
            DateKey, CommunityArea, TotalIncidentCount, TotalArrestCount,
            TotalDomesticCount, TotalNightCount, DistinctCrimeTypes, ArrestRate, DomesticRate, batch_id
        )
        SELECT 
            f.DateKey,
            l.CommunityArea,
            SUM(f.IncidentCount) AS TotalIncidentCount,
            SUM(f.ArrestCount) AS TotalArrestCount,
            SUM(f.DomesticCount) AS TotalDomesticCount,
            SUM(f.NightCount) AS TotalNightCount,
            COUNT(DISTINCT f.CrimeTypeKey) AS DistinctCrimeTypes,
            ROUND((SUM(f.ArrestCount)::NUMERIC / SUM(f.IncidentCount)::NUMERIC) * 100.0, 2) AS ArrestRate,
            ROUND((SUM(f.DomesticCount)::NUMERIC / SUM(f.IncidentCount)::NUMERIC) * 100.0, 2) AS DomesticRate,
            'INITIAL_LOAD_2024_NOV2025' AS batch_id
        FROM dw.FactCrimeIncident f
        JOIN dw.DimLocation l ON f.LocationKey = l.LocationKey
        WHERE l.CommunityArea > 0
        GROUP BY f.DateKey, l.CommunityArea
        ON CONFLICT (DateKey, CommunityArea) DO NOTHING;
        """)
        cur.execute("SELECT COUNT(*) FROM dw.FactAreaDailyPublicSafety;")
        fact2_count = cur.fetchone()[0]
    conn.commit()
    print(f"FactAreaDailyPublicSafety loaded: {fact2_count:,} area-daily aggregate rows.")

    conn.close()
    duration = time.time() - t0
    print(f"=== Initial Load Completed Successfully in {duration:.2f} seconds ===")

if __name__ == "__main__":
    run_initial_load()
