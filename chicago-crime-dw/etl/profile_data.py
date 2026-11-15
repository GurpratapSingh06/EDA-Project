"""
Data Profiling Script for Raw Chicago Crime Dataset (2024-2025)
Profiles before cleaning:
- Total rows, columns, memory usage
- Missing value counts & percentages across all columns
- Exact duplicates vs Logical duplicates (by Case Number, or ID)
- Invalid IUCR codes (non-conforming format or missing)
- Invalid FBI codes (missing or malformed)
- Coordinate validation: (0,0), nulls, Chicago bounding box [41.60 to 42.05 N, -87.95 to -87.50 W]
- Timestamp analysis: min, max, unparseable timestamps, out-of-scope dates
- Categorical cardinality & malformed values
- Saves summary tables to outputs/tables/raw_profiling_summary.csv and outputs/tables/missing_profile.csv
"""

import os
import pandas as pd
import numpy as np

def run_profiling():
    raw_path = "chicago-crime-dw/data/raw/crimes_2024_2025.csv"
    print(f"Loading raw dataset from {raw_path}...")
    df = pd.read_csv(raw_path, low_memory=False)
    
    total_rows = len(df)
    total_cols = len(df.columns)
    print(f"Loaded {total_rows:,} rows across {total_cols} columns.")

    # 1. Missing values
    missing_counts = df.isnull().sum()
    missing_pct = (missing_counts / total_rows) * 100
    missing_df = pd.DataFrame({
        "Column": df.columns,
        "MissingCount": missing_counts.values,
        "MissingPct": missing_pct.round(4).values,
        "Dtype": [str(t) for t in df.dtypes.values]
    })
    os.makedirs("chicago-crime-dw/outputs/tables", exist_ok=True)
    missing_df.to_csv("chicago-crime-dw/outputs/tables/missing_profile.csv", index=False)
    print("\n--- Missing Value Profile ---")
    print(missing_df[missing_df["MissingCount"] > 0])

    # 2. Duplicates
    exact_dups = df.duplicated().sum()
    id_dups = df.duplicated(subset=["id"]).sum()
    # Logical duplicates: same case_number
    # Note: Case numbers can legitimately have multiple rows if multiple offenses/victims occurred in one incident,
    # but exact duplicate rows or repeat case numbers with identical time and crime type need distinct tracking.
    case_dups = df.duplicated(subset=["case_number"]).sum()
    case_and_iucr_dups = df.duplicated(subset=["case_number", "iucr"]).sum()
    
    print("\n--- Duplicate Analysis ---")
    print(f"Exact row duplicates: {exact_dups}")
    print(f"Duplicate Primary Key 'id': {id_dups}")
    print(f"Rows sharing Case Number: {case_dups}")
    print(f"Rows sharing Case Number + IUCR: {case_and_iucr_dups}")

    # 3. Timestamp analysis
    print("\n--- Timestamp Analysis ---")
    df["dt"] = pd.to_datetime(df["date"], errors="coerce")
    invalid_dt_count = df["dt"].isnull().sum()
    min_date = df["dt"].min()
    max_date = df["dt"].max()
    out_of_scope = ((df["dt"] < "2024-01-01") | (df["dt"] > "2025-12-31 23:59:59")).sum()
    print(f"Unparseable timestamps: {invalid_dt_count}")
    print(f"Date range: {min_date} to {max_date}")
    print(f"Rows out of scope (not 2024-2025): {out_of_scope}")

    # 4. Geographic & Coordinate Validation
    # Chicago approximate bounding box: Lat 41.60 to 42.06, Lon -87.95 to -87.50
    print("\n--- Coordinate Validation ---")
    lat_null = df["latitude"].isnull().sum()
    lon_null = df["longitude"].isnull().sum()
    coord_zero = ((df["latitude"] == 0) | (df["longitude"] == 0)).sum()
    
    # Valid coordinates mask
    valid_coords = df["latitude"].notnull() & df["longitude"].notnull()
    out_of_bounds = (
        valid_coords &
        ((df["latitude"] < 41.60) | (df["latitude"] > 42.06) |
         (df["longitude"] < -87.95) | (df["longitude"] > -87.50))
    ).sum()
    
    print(f"Latitude nulls: {lat_null} ({lat_null/total_rows*100:.2f}%)")
    print(f"Longitude nulls: {lon_null} ({lon_null/total_rows*100:.2f}%)")
    print(f"Coordinates at (0,0): {coord_zero}")
    print(f"Coordinates outside Chicago bounding box: {out_of_bounds}")

    # 5. Administrative Geography
    district_null = df["district"].isnull().sum()
    ward_null = df["ward"].isnull().sum()
    comm_area_null = df["community_area"].isnull().sum()
    beat_null = df["beat"].isnull().sum()
    print(f"District nulls: {district_null}")
    print(f"Ward nulls: {ward_null}")
    print(f"Community Area nulls: {comm_area_null}")
    print(f"Beat nulls: {beat_null}")

    # 6. Crime Codes & Categories
    print("\n--- Categorical & Code Validation ---")
    iucr_null = df["iucr"].isnull().sum()
    fbi_null = df["fbi_code"].isnull().sum()
    primary_null = df["primary_type"].isnull().sum()
    loc_desc_null = df["location_description"].isnull().sum()
    
    # Check IUCR format: standard is 4 characters (digits or letters, often 3-4 digits padded)
    invalid_iucr_format = df["iucr"].astype(str).str.len().apply(lambda x: x < 3 or x > 5).sum()
    print(f"IUCR nulls: {iucr_null}, Non-standard lengths: {invalid_iucr_format}")
    print(f"FBI Code nulls: {fbi_null}")
    print(f"Primary Type nulls: {primary_null}, Unique values: {df['primary_type'].nunique()}")
    print(f"Location Description nulls: {loc_desc_null}, Unique values: {df['location_description'].nunique()}")
    print(f"Arrest boolean nulls: {df['arrest'].isnull().sum()}, True count: {(df['arrest']==True).sum()}")
    print(f"Domestic boolean nulls: {df['domestic'].isnull().sum()}, True count: {(df['domestic']==True).sum()}")

    # Save summary dictionary to a file
    summary_data = {
        "Metric": [
            "Total Raw Records",
            "Total Attributes",
            "Exact Row Duplicates",
            "Duplicate IDs",
            "Shared Case Numbers",
            "Invalid/Unparseable Timestamps",
            "Date Range Min",
            "Date Range Max",
            "Out-of-Scope Dates (<2024 or >2025)",
            "Missing Latitude/Longitude",
            "Coordinates (0,0)",
            "Coordinates Out of Chicago Bounds",
            "Missing District",
            "Missing Ward",
            "Missing Community Area",
            "Missing Location Description",
            "Missing FBI Code",
            "Unique Primary Crime Types",
            "Unique Location Descriptions",
            "Total Arrests Recorded",
            "Overall Arrest Rate (%)",
            "Total Domestic Incidents",
            "Overall Domestic Rate (%)"
        ],
        "Value": [
            total_rows,
            total_cols,
            exact_dups,
            id_dups,
            case_dups,
            invalid_dt_count,
            str(min_date),
            str(max_date),
            out_of_scope,
            lat_null,
            coord_zero,
            out_of_bounds,
            district_null,
            ward_null,
            comm_area_null,
            loc_desc_null,
            fbi_null,
            df["primary_type"].nunique(),
            df["location_description"].nunique(),
            int((df["arrest"] == True).sum()),
            round((df["arrest"] == True).sum() / total_rows * 100, 2),
            int((df["domestic"] == True).sum()),
            round((df["domestic"] == True).sum() / total_rows * 100, 2)
        ]
    }
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv("chicago-crime-dw/outputs/tables/raw_profiling_summary.csv", index=False)
    print("\nSaved profiling summary to chicago-crime-dw/outputs/tables/raw_profiling_summary.csv")

if __name__ == "__main__":
    run_profiling()
