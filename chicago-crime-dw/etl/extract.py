"""
Extract module for Chicago Crimes (2024-2025)
Fetches official crime records from the City of Chicago Socrata Open Data Portal API (ijzp-q8t2).
Preserves raw extract, logs download metadata to docs/source_log.md.
"""

import os
import sys
import time
import datetime
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd

API_ENDPOINT = "https://data.cityofchicago.org/resource/ijzp-q8t2.csv"
WHERE_CLAUSE = "date >= '2024-01-01T00:00:00.000' and date <= '2025-12-31T23:59:59.000'"
COLUMNS = (
    "id,case_number,date,block,iucr,primary_type,description,"
    "location_description,arrest,domestic,beat,district,ward,"
    "community_area,fbi_code,x_coordinate,y_coordinate,year,"
    "updated_on,latitude,longitude"
)
BATCH_SIZE = 50000
MAX_WORKERS = 6

def get_total_count():
    count_url = (
        "https://data.cityofchicago.org/resource/ijzp-q8t2.json?"
        + "$select=count(*)&"
        + f"$where={urllib.parse.quote(WHERE_CLAUSE)}"
    )
    req = urllib.request.Request(count_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        import json
        data = json.loads(resp.read().decode("utf-8"))
        return int(data[0]["count"])

def fetch_chunk(offset, limit):
    params = {
        "$select": COLUMNS,
        "$where": WHERE_CLAUSE,
        "$order": "id",
        "$limit": str(limit),
        "$offset": str(offset)
    }
    query_str = urllib.parse.urlencode(params)
    url = f"{API_ENDPOINT}?{query_str}"
    
    max_retries = 5
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                df = pd.read_csv(resp)
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Fetched offset {offset} ({len(df)} rows)")
                return offset, df
        except Exception as e:
            print(f"Warning: Retry {attempt+1}/{max_retries} for offset {offset} due to error: {e}")
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"Failed to fetch offset {offset} after {max_retries} retries")

def extract_crimes(raw_csv_path, source_log_path):
    print("=== Starting Chicago Crimes Data Extraction (2024-2025) ===")
    t_start = time.time()
    total_expected = get_total_count()
    print(f"Total expected rows from Socrata: {total_expected:,}")

    offsets = list(range(0, total_expected, BATCH_SIZE))
    results = {}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_offset = {executor.submit(fetch_chunk, off, BATCH_SIZE): off for off in offsets}
        for future in as_completed(future_to_offset):
            off, df = future.result()
            results[off] = df

    # Combine in sorted offset order
    ordered_dfs = [results[off] for off in sorted(results.keys())]
    combined_df = pd.concat(ordered_dfs, ignore_index=True)
    actual_rows = len(combined_df)
    print(f"Extraction complete: {actual_rows:,} rows retrieved in {time.time() - t_start:.2f} seconds")

    os.makedirs(os.path.dirname(raw_csv_path), exist_ok=True)
    combined_df.to_csv(raw_csv_path, index=False)
    print(f"Saved raw dataset to: {raw_csv_path} ({os.path.getsize(raw_csv_path) / (1024*1024):.2f} MB)")

    # Write docs/source_log.md
    os.makedirs(os.path.dirname(source_log_path), exist_ok=True)
    with open(source_log_path, "w", encoding="utf-8") as f:
        f.write("# Data Source and Extraction Log\n\n")
        f.write("## 1. Dataset Provenance\n")
        f.write("- **Dataset Name:** Crimes - 2001 to Present\n")
        f.write("- **Publisher:** City of Chicago / Chicago Police Department (CPD)\n")
        f.write("- **Portal Identifier:** `ijzp-q8t2`\n")
        f.write("- **Authoritative URL:** [Chicago Data Portal](https://data.cityofchicago.org/Public-Safety/Crimes-2001-to-Present/ijzp-q8t2)\n")
        f.write(f"- **Download Timestamp:** {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
        f.write("## 2. Extraction Scope and Query Parameters\n")
        f.write(f"- **Temporal Filter ($where):** `{WHERE_CLAUSE}`\n")
        f.write(f"- **Total Rows Extracted:** {actual_rows:,}\n")
        f.write(f"- **Total Columns:** {len(combined_df.columns)}\n")
        f.write(f"- **Selected Fields:** {', '.join(combined_df.columns)}\n")
        f.write(f"- **Pagination Method:** Socrata SoQL `$limit=50000`, `$offset` with multi-threaded chunking\n")
        f.write(f"- **Raw File Location:** `{raw_csv_path}`\n")
        f.write(f"- **Raw File Size:** {os.path.getsize(raw_csv_path) / (1024*1024):.2f} MB\n\n")
        f.write("## 3. Extraction Verification\n")
        f.write(f"- Server total report: {total_expected:,} rows\n")
        f.write(f"- Local CSV row count: {actual_rows:,} rows\n")
        f.write(f"- Status: {'PASSED - Row counts match exactly' if actual_rows == total_expected else 'DIFFERENCE DETECTED'}\n")

    print(f"Logged extraction metadata to: {source_log_path}")
    return combined_df

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_path = os.path.join(base_dir, "data", "raw", "crimes_2024_2025.csv")
    log_path = os.path.join(base_dir, "docs", "source_log.md")
    extract_crimes(raw_path, log_path)
