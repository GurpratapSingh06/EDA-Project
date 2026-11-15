"""
ERD Generator for Dimensional Models
Generates publication-quality ERD diagram PNGs:
- docs/erd/star_schema_erd.png
- docs/erd/snowflake_schema_erd.png
- docs/erd/constellation_schema_erd.png
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_box(ax, x, y, width, height, title, fields, color="#e6f2ff", border="#3182ce"):
    # Main box
    rect = patches.FancyBboxPatch((x, y), width, height,
                                  boxstyle="round,pad=0.02,rounding_size=0.03",
                                  linewidth=1.5, edgecolor=border, facecolor=color)
    ax.add_patch(rect)
    # Header box
    header_height = 0.08
    header_rect = patches.FancyBboxPatch((x, y + height - header_height), width, header_height,
                                         boxstyle="round,pad=0.01,rounding_size=0.02",
                                         linewidth=1, edgecolor=border, facecolor=border)
    ax.add_patch(header_rect)
    ax.text(x + width/2, y + height - header_height/2, title,
            ha='center', va='center', fontsize=9.5, fontweight='bold', color='white')
    
    # Text fields
    line_spacing = (height - header_height) / (len(fields) + 1)
    for i, field in enumerate(fields):
        field_y = y + height - header_height - (i + 1) * line_spacing
        is_pk = "PK" in field
        is_fk = "FK" in field
        fcolor = '#990000' if is_pk else ('#0055aa' if is_fk else '#333333')
        fweight = 'bold' if (is_pk or is_fk) else 'normal'
        ax.text(x + 0.02, field_y, field, ha='left', va='center', fontsize=8, color=fcolor, fontweight=fweight)

def generate_star_erd(save_path):
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    plt.title("Chicago Crime Data Warehouse: Star Schema ERD", fontsize=14, fontweight='bold', pad=15)

    # Center Fact
    draw_box(ax, 0.36, 0.28, 0.28, 0.44, "FactCrimeIncident", [
        "[PK] IncidentKey (Identity)",
        "[FK] DateKey",
        "[FK] TimeKey",
        "[FK] CrimeTypeKey",
        "[FK] LocationKey",
        "[FK] ContextKey",
        "IncidentID (Degenerate)",
        "CaseNumber (Degenerate)",
        "IncidentCount (Measure: 1)",
        "ArrestCount (Measure: 0/1)",
        "DomesticCount (Measure: 0/1)",
        "NightCount (Measure: 0/1)",
        "BatchID, LoadTimestamp"
    ], color="#fff9db", border="#f59f00")

    # Dimensions around fact
    # DimDate (Top Left)
    draw_box(ax, 0.05, 0.65, 0.24, 0.28, "DimDate", [
        "[PK] DateKey (YYYYMMDD)",
        "FullDate (DATE)",
        "Day, DayName",
        "Week, Month, MonthName",
        "Quarter, Year",
        "IsWeekend (0/1)"
    ], color="#e7f5ff", border="#1c7ed6")

    # DimTime (Top Right)
    draw_box(ax, 0.71, 0.65, 0.24, 0.24, "DimTime", [
        "[PK] TimeKey (HHMM)",
        "Hour (0-23)",
        "Minute (0-59)",
        "TimeBand (Night/Morn/Aft/Eve)"
    ], color="#e7f5ff", border="#1c7ed6")

    # DimCrimeType (Bottom Left)
    draw_box(ax, 0.05, 0.08, 0.24, 0.28, "DimCrimeType", [
        "[PK] CrimeTypeKey",
        "IUCR (Code)",
        "PrimaryType",
        "Description",
        "FBICode",
        "CrimeCategoryGroup"
    ], color="#e7f5ff", border="#1c7ed6")

    # DimLocation (Bottom Right)
    draw_box(ax, 0.71, 0.08, 0.25, 0.36, "DimLocation", [
        "[PK] LocationKey",
        "Block, Beat",
        "District, Ward",
        "CommunityArea",
        "LocationDescription",
        "LocationGroup",
        "LatitudeBand, LongitudeBand"
    ], color="#e7f5ff", border="#1c7ed6")

    # DimIncidentContext (Top Center)
    draw_box(ax, 0.38, 0.78, 0.24, 0.18, "DimIncidentContext", [
        "[PK] ContextKey",
        "ArrestFlag (0/1)",
        "DomesticFlag (0/1)",
        "NightFlag (0/1)"
    ], color="#e7f5ff", border="#1c7ed6")

    # Connecting arrows (Dimensions -> Fact)
    arrows = [
        ((0.29, 0.75), (0.36, 0.60)), # Date -> Fact
        ((0.71, 0.75), (0.64, 0.60)), # Time -> Fact
        ((0.29, 0.25), (0.36, 0.40)), # Crime -> Fact
        ((0.71, 0.25), (0.64, 0.40)), # Location -> Fact
        ((0.50, 0.78), (0.50, 0.72))  # Context -> Fact
    ]
    for start, end in arrows:
        ax.annotate("", xy=end, xytext=start,
                    arrowprops=dict(arrowstyle="->", lw=1.8, color="#495057"))

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

def generate_snowflake_erd(save_path):
    fig, ax = plt.subplots(figsize=(13, 8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    plt.title("Chicago Crime Data Warehouse: Snowflake Schema ERD (Normalized Hierarchies)", fontsize=14, fontweight='bold', pad=15)

    # Center Fact
    draw_box(ax, 0.38, 0.34, 0.24, 0.34, "FactCrimeIncident", [
        "[PK] IncidentKey",
        "[FK] DateKey",
        "[FK] TimeKey",
        "[FK] CrimeTypeKey",
        "[FK] LocationKey",
        "[FK] ContextKey",
        "IncidentCount (1)",
        "ArrestCount, DomesticCount"
    ], color="#fff9db", border="#f59f00")

    # Normalized Geography: Location -> Beat -> District -> CommunityArea
    draw_box(ax, 0.68, 0.36, 0.15, 0.22, "DimLocation", [
        "[PK] LocationKey",
        "LocationDesc",
        "[FK] BeatKey"
    ], color="#ebfbee", border="#2b8a3e")
    draw_box(ax, 0.85, 0.36, 0.14, 0.22, "DimBeat", [
        "[PK] BeatKey",
        "BeatNumber",
        "[FK] DistrictKey"
    ], color="#ebfbee", border="#2b8a3e")
    draw_box(ax, 0.85, 0.65, 0.14, 0.22, "DimDistrict", [
        "[PK] DistrictKey",
        "DistrictNumber",
        "[FK] CommAreaKey"
    ], color="#ebfbee", border="#2b8a3e")
    draw_box(ax, 0.85, 0.08, 0.14, 0.20, "DimCommArea", [
        "[PK] CommAreaKey",
        "CommunityAreaNum",
        "AreaName"
    ], color="#ebfbee", border="#2b8a3e")

    # Normalized Crime: CrimeType -> FBICategory
    draw_box(ax, 0.18, 0.12, 0.16, 0.24, "DimCrimeType", [
        "[PK] CrimeTypeKey",
        "IUCR, PrimaryType",
        "[FK] FBICategoryKey"
    ], color="#f3f0ff", border="#6741d9")
    draw_box(ax, 0.02, 0.12, 0.14, 0.20, "DimFBICategory", [
        "[PK] FBICatKey",
        "FBICode",
        "FBIDescription"
    ], color="#f3f0ff", border="#6741d9")

    # Normalized Date: Date -> Month -> Quarter -> Year
    draw_box(ax, 0.18, 0.58, 0.16, 0.24, "DimDate", [
        "[PK] DateKey",
        "FullDate, Day",
        "[FK] MonthKey"
    ], color="#e7f5ff", border="#1c7ed6")
    draw_box(ax, 0.02, 0.58, 0.14, 0.22, "DimMonth", [
        "[PK] MonthKey",
        "MonthNumber",
        "Quarter, Year"
    ], color="#e7f5ff", border="#1c7ed6")

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

def generate_constellation_erd(save_path):
    fig, ax = plt.subplots(figsize=(13, 8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    plt.title("Final Selected Model: Fact Constellation (Galaxy Schema)", fontsize=14, fontweight='bold', pad=15)

    # Shared Conformed Dimension: DimDate
    draw_box(ax, 0.38, 0.72, 0.24, 0.22, "DimDate (Conformed)", [
        "[PK] DateKey",
        "FullDate, Day, Week",
        "Month, Quarter, Year",
        "IsWeekend"
    ], color="#e7f5ff", border="#1c7ed6")

    # Shared Conformed Dimension: DimLocation
    draw_box(ax, 0.38, 0.06, 0.24, 0.26, "DimLocation (Conformed)", [
        "[PK] LocationKey",
        "District, Beat, Ward",
        "CommunityArea",
        "LocationDescription, LocationGroup"
    ], color="#e7f5ff", border="#1c7ed6")

    # Fact 1: FactCrimeIncident (Left) - Incident Grain
    draw_box(ax, 0.06, 0.30, 0.27, 0.42, "FactCrimeIncident\n(Grain: 1 Reported Incident)", [
        "[PK] IncidentKey",
        "[FK] DateKey (Conformed)",
        "[FK] TimeKey",
        "[FK] CrimeTypeKey",
        "[FK] LocationKey (Conformed)",
        "[FK] ContextKey",
        "IncidentCount (1)",
        "ArrestCount (0/1)",
        "DomesticCount (0/1)",
        "NightCount (0/1)",
        "Audit: BatchID, LoadTimestamp"
    ], color="#fff9db", border="#f59f00")

    # Fact 2: FactAreaDailyPublicSafety (Right) - Area x Date Grain
    draw_box(ax, 0.67, 0.30, 0.27, 0.42, "FactAreaDailyPublicSafety\n(Grain: CommunityArea x Date)", [
        "[PK] AreaDailyKey",
        "[FK] DateKey (Conformed)",
        "CommunityArea (Area ID)",
        "[FK] LocationKey (Representative)",
        "TotalIncidentCount (Sum)",
        "TotalArrestCount (Sum)",
        "TotalDomesticCount (Sum)",
        "TotalNightCount (Sum)",
        "DistinctCrimeTypes (Count Distinct)",
        "ArrestRate (Measure: %)",
        "Audit: BatchID, LoadTimestamp"
    ], color="#ffe8cc", border="#d9480f")

    # Exclusive Dimensions for Fact 1
    draw_box(ax, 0.02, 0.75, 0.18, 0.18, "DimTime", [
        "[PK] TimeKey",
        "Hour, Minute",
        "TimeBand"
    ], color="#f1f3f5", border="#495057")

    draw_box(ax, 0.02, 0.08, 0.18, 0.18, "DimCrimeType", [
        "[PK] CrimeTypeKey",
        "IUCR, PrimaryType",
        "FBICode"
    ], color="#f1f3f5", border="#495057")

    # Arrows from conformed dimensions
    ax.annotate("", xy=(0.20, 0.72), xytext=(0.38, 0.82), arrowprops=dict(arrowstyle="->", lw=1.6, color="#1c7ed6"))
    ax.annotate("", xy=(0.80, 0.72), xytext=(0.62, 0.82), arrowprops=dict(arrowstyle="->", lw=1.6, color="#1c7ed6"))
    ax.annotate("", xy=(0.20, 0.30), xytext=(0.38, 0.18), arrowprops=dict(arrowstyle="->", lw=1.6, color="#1c7ed6"))
    ax.annotate("", xy=(0.80, 0.30), xytext=(0.62, 0.18), arrowprops=dict(arrowstyle="->", lw=1.6, color="#1c7ed6"))

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    erd_dir = os.path.join(base_dir, "docs", "erd")
    os.makedirs(erd_dir, exist_ok=True)
    generate_star_erd(os.path.join(erd_dir, "star_schema_erd.png"))
    generate_snowflake_erd(os.path.join(erd_dir, "snowflake_schema_erd.png"))
    generate_constellation_erd(os.path.join(erd_dir, "constellation_schema_erd.png"))
    print("Generated all three ERD diagrams in docs/erd/")
