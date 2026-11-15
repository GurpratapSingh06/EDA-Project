"""
Comprehensive Exploratory Data Analysis Generator
Computes exact statistical metrics (mean, median, min, max, var, std, quartiles, IQR, skew, kurtosis)
Generates publication-grade figures saved to outputs/figures/
Saves statistical tables to outputs/tables/
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

def run_eda():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    curated_path = os.path.join(base_dir, "data", "curated", "crimes_curated.csv")
    fig_dir = os.path.join(base_dir, "outputs", "figures")
    tbl_dir = os.path.join(base_dir, "outputs", "tables")
    os.makedirs(fig_dir, exist_ok=True)
    os.makedirs(tbl_dir, exist_ok=True)

    print("Loading curated dataset for EDA...")
    df = pd.read_csv(curated_path, low_memory=False)
    total_records = len(df)
    print(f"Loaded {total_records:,} records.")

    # ==========================================
    # 1. NUMERICAL STATISTICAL SUMMARY
    # ==========================================
    # Calculate daily incident counts
    daily_series = df.groupby("full_date").size()
    # Calculate hourly incident counts
    df["date_hour"] = df["full_date"].astype(str) + " " + df["hour"].astype(str).str.zfill(2)
    hourly_series = df.groupby("date_hour").size()
    # Valid coordinates
    valid_lat = df[df["has_valid_coordinates"] == 1]["latitude"]
    valid_lon = df[df["has_valid_coordinates"] == 1]["longitude"]

    numeric_vars = {
        "Daily Incident Volume": daily_series,
        "Hourly Incident Volume": hourly_series,
        "Incident Latitude (Valid)": valid_lat,
        "Incident Longitude (Valid)": valid_lon,
        "Arrest Flag (Binary)": df["arrest_flag"],
        "Domestic Flag (Binary)": df["domestic_flag"],
        "Night Incident Flag": df["is_night_incident"]
    }

    num_stats = []
    for name, series in numeric_vars.items():
        s = series.dropna()
        q1 = s.quantile(0.25)
        q3 = s.quantile(0.75)
        iqr = q3 - q1
        num_stats.append({
            "Variable": name,
            "Count": len(s),
            "Mean": round(s.mean(), 4),
            "StdDev": round(s.std(), 4),
            "Variance": round(s.var(), 4),
            "Median": round(s.median(), 4),
            "Min": round(s.min(), 4),
            "Q1 (25%)": round(q1, 4),
            "Q3 (75%)": round(q3, 4),
            "Max": round(s.max(), 4),
            "IQR": round(iqr, 4),
            "Skewness": round(float(stats.skew(s)), 4),
            "Kurtosis": round(float(stats.kurtosis(s)), 4)
        })

    stats_df = pd.DataFrame(num_stats)
    stats_df.to_csv(os.path.join(tbl_dir, "numerical_stats_table.csv"), index=False)
    print("Saved numerical statistics table.")

    # ==========================================
    # 2. CATEGORICAL FREQUENCIES & RARE CATEGORIES
    # ==========================================
    pt_counts = df["primary_type"].value_counts().reset_index()
    pt_counts.columns = ["PrimaryType", "Count"]
    pt_counts["Percentage"] = (pt_counts["Count"] / total_records * 100).round(2)
    pt_counts["CumulativePct"] = pt_counts["Percentage"].cumsum().round(2)
    pt_counts.to_csv(os.path.join(tbl_dir, "primary_type_frequencies.csv"), index=False)

    # Rare categories (< 0.5% threshold)
    rare_types = pt_counts[pt_counts["Percentage"] < 0.5]
    rare_types.to_csv(os.path.join(tbl_dir, "rare_categories.csv"), index=False)
    print(f"Identified {len(rare_types)} rare primary crime types (<0.5% volume).")

    # Cross-tabulation of Crime Category Group vs Arrest
    cat_arrest_ct = pd.crosstab(df["crime_category_group"], df["arrest_flag"], margins=True)
    cat_arrest_ct.columns = ["No Arrest (0)", "Arrest Made (1)", "Total"]
    cat_arrest_ct["Arrest Rate (%)"] = (cat_arrest_ct["Arrest Made (1)"] / cat_arrest_ct["Total"] * 100).round(2)
    cat_arrest_ct.to_csv(os.path.join(tbl_dir, "crosstab_category_arrest.csv"))

    # ==========================================
    # 3. FIGURE 1: TOP 15 PRIMARY CRIME TYPES
    # ==========================================
    plt.figure(figsize=(10, 6))
    top15_pt = pt_counts.head(15)
    ax = sns.barplot(x="Count", y="PrimaryType", data=top15_pt, palette="Blues_r")
    plt.title("Top 15 Reported Primary Crime Types in Chicago (2024–2025)", fontsize=13, fontweight='bold', pad=12)
    plt.xlabel("Total Incident Count", fontsize=11)
    plt.ylabel("Primary Offense Category", fontsize=11)
    for p in ax.patches:
        width = p.get_width()
        pct = (width / total_records) * 100
        ax.annotate(f"{int(width):,} ({pct:.1f}%)",
                    (width + 2000, p.get_y() + p.get_height() / 2.),
                    va='center', fontsize=9, color='#333333')
    plt.xlim(0, top15_pt["Count"].max() * 1.22)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig01_top_crime_types.png"), dpi=300)
    plt.close()

    # ==========================================
    # 4. FIGURE 2: VOLUME VS ARREST RATE BY CRIME TYPE
    # ==========================================
    pt_summary = df.groupby("primary_type").agg(
        TotalIncidents=("id", "count"),
        Arrests=("arrest_flag", "sum"),
        Domestic=("domestic_flag", "sum")
    ).reset_index()
    pt_summary["ArrestRate"] = (pt_summary["Arrests"] / pt_summary["TotalIncidents"] * 100).round(2)
    pt_summary["DomesticRate"] = (pt_summary["Domestic"] / pt_summary["TotalIncidents"] * 100).round(2)
    pt_summary.to_csv(os.path.join(tbl_dir, "crime_type_volume_and_rates.csv"), index=False)

    # Plot top 12 volume types: bar chart for volume, red dots/line for arrest rate
    top12 = pt_summary.sort_values(by="TotalIncidents", ascending=False).head(12)
    fig, ax1 = plt.subplots(figsize=(12, 6))
    color = '#1f77b4'
    ax1.set_xlabel('Primary Crime Type', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Total Incident Volume', color=color, fontsize=11, fontweight='bold')
    bars = ax1.bar(top12["primary_type"], top12["TotalIncidents"], color=color, alpha=0.75, width=0.55)
    ax1.tick_params(axis='y', labelcolor=color)
    plt.xticks(rotation=40, ha='right', fontsize=10)

    ax2 = ax1.twinx()
    color2 = '#d62728'
    ax2.set_ylabel('Arrest Rate (%)', color=color2, fontsize=11, fontweight='bold')
    ax2.plot(top12["primary_type"], top12["ArrestRate"], color=color2, marker='o', linewidth=2, markersize=8)
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.set_ylim(0, 100)

    for i, txt in enumerate(top12["ArrestRate"]):
        ax2.annotate(f"{txt:.1f}%", (i, txt + 3), ha='center', fontsize=9, fontweight='bold', color=color2)

    plt.title('Chicago Crime: Incident Volume vs. Arrest Rate by Top Crime Types (2024–2025)', fontsize=13, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig02_volume_vs_arrest_rate.png"), dpi=300)
    plt.close()

    # ==========================================
    # 5. FIGURE 3: TEMPORAL TRENDS (MONTHLY & YEARLY)
    # ==========================================
    monthly_trend = df.groupby(["year", "month"]).agg(
        Incidents=("id", "count"),
        Arrests=("arrest_flag", "sum"),
        Domestic=("domestic_flag", "sum")
    ).reset_index()
    monthly_trend["YearMonth"] = monthly_trend["year"].astype(str) + "-" + monthly_trend["month"].astype(str).str.zfill(2)
    monthly_trend["ArrestRate"] = (monthly_trend["Arrests"] / monthly_trend["Incidents"] * 100).round(2)
    monthly_trend.to_csv(os.path.join(tbl_dir, "monthly_trends.csv"), index=False)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 8), sharex=True)
    ax1.plot(monthly_trend["YearMonth"], monthly_trend["Incidents"], marker='s', color='#2b5c8f', linewidth=2.5, label='Total Incidents')
    ax1.plot(monthly_trend["YearMonth"], monthly_trend["Arrests"], marker='o', color='#2ca02c', linewidth=2, label='Arrests')
    ax1.plot(monthly_trend["YearMonth"], monthly_trend["Domestic"], marker='^', color='#ff7f0e', linewidth=2, label='Domestic Crimes')
    ax1.set_ylabel('Monthly Count', fontsize=11, fontweight='bold')
    ax1.set_title('Monthly Crime Incident, Arrest, and Domestic Violence Trends (2024–2025)', fontsize=13, fontweight='bold')
    ax1.legend(loc='upper right', frameon=True)
    ax1.grid(True, linestyle='--', alpha=0.6)

    ax2.plot(monthly_trend["YearMonth"], monthly_trend["ArrestRate"], marker='d', color='#d62728', linewidth=2.2, label='Arrest Rate (%)')
    ax2.set_ylabel('Arrest Rate (%)', fontsize=11, fontweight='bold')
    ax2.set_xlabel('Year-Month', fontsize=11, fontweight='bold')
    ax2.set_ylim(10, 22)
    for i, txt in enumerate(monthly_trend["ArrestRate"]):
        ax2.annotate(f"{txt:.1f}%", (i, txt + 0.4), ha='center', fontsize=8, color='#990000')
    ax2.legend(loc='upper right', frameon=True)
    ax2.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig03_monthly_temporal_trend.png"), dpi=300)
    plt.close()

    # ==========================================
    # 6. FIGURE 4: HOURLY DISTRIBUTION & PEAK ANALYSIS
    # ==========================================
    hourly_df = df.groupby("hour").agg(
        TotalIncidents=("id", "count"),
        Arrests=("arrest_flag", "sum"),
        Domestic=("domestic_flag", "sum")
    ).reset_index()
    hourly_df["ArrestRate"] = (hourly_df["Arrests"] / hourly_df["TotalIncidents"] * 100).round(2)
    hourly_df.to_csv(os.path.join(tbl_dir, "hourly_summary.csv"), index=False)

    plt.figure(figsize=(11, 5.5))
    bars = plt.bar(hourly_df["hour"], hourly_df["TotalIncidents"], color='#3a7ebf', width=0.7, edgecolor='#234970', alpha=0.85)
    # Highlight peak hour (e.g. 18:00-22:00) and trough (04:00-06:00)
    max_h = hourly_df.loc[hourly_df["TotalIncidents"].idxmax()]["hour"]
    min_h = hourly_df.loc[hourly_df["TotalIncidents"].idxmin()]["hour"]
    bars[int(max_h)].set_color('#d9534f') # Red for peak
    bars[int(min_h)].set_color('#5cb85c') # Green for trough

    plt.title('Diurnal Hourly Distribution of Reported Crimes in Chicago (2024–2025)', fontsize=13, fontweight='bold', pad=12)
    plt.xlabel('Hour of Day (0–23, 24-Hour Military Time)', fontsize=11, fontweight='bold')
    plt.ylabel('Total Incidents Reported', fontsize=11, fontweight='bold')
    plt.xticks(range(0, 24))
    plt.annotate(f'Peak Hour: {int(max_h)}:00 ({hourly_df.loc[hourly_df["hour"]==max_h, "TotalIncidents"].values[0]:,} crimes)',
                 xy=(max_h, hourly_df.loc[hourly_df["hour"]==max_h, "TotalIncidents"].values[0]),
                 xytext=(max_h - 6, hourly_df["TotalIncidents"].max() * 0.95),
                 arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=6),
                 fontsize=10, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", fc="#ffdddd", ec="#d9534f"))
    plt.annotate(f'Lowest Hour: {int(min_h)}:00 ({hourly_df.loc[hourly_df["hour"]==min_h, "TotalIncidents"].values[0]:,} crimes)',
                 xy=(min_h, hourly_df.loc[hourly_df["hour"]==min_h, "TotalIncidents"].values[0]),
                 xytext=(min_h + 2, hourly_df["TotalIncidents"].min() * 1.6),
                 arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=6),
                 fontsize=10, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", fc="#ddffdd", ec="#5cb85c"))
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig04_hourly_distribution_peaks.png"), dpi=300)
    plt.close()

    # ==========================================
    # 7. FIGURE 5: HOUR X DAY HEATMAP
    # ==========================================
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    heat_data = df.pivot_table(index="day_name", columns="hour", values="id", aggfunc="count").reindex(days_order)
    
    plt.figure(figsize=(14, 6))
    sns.heatmap(heat_data, cmap="YlOrRd", annot=False, fmt="d", cbar_kws={'label': 'Reported Incidents'}, linewidths=0.5)
    plt.title("Chicago Crime Concentration Heatmap: Day of Week vs. Hour of Day (2024–2025)", fontsize=13, fontweight='bold', pad=12)
    plt.xlabel("Hour of Day (0–23)", fontsize=11, fontweight='bold')
    plt.ylabel("Day of Week", fontsize=11, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig05_hour_day_heatmap.png"), dpi=300)
    plt.close()

    # ==========================================
    # 8. FIGURE 6: DISTRICT-LEVEL VOLUME & ARREST RATE
    # ==========================================
    dist_df = df.groupby("district").agg(
        TotalIncidents=("id", "count"),
        Arrests=("arrest_flag", "sum"),
        Domestic=("domestic_flag", "sum")
    ).reset_index()
    dist_df["ArrestRate"] = (dist_df["Arrests"] / dist_df["TotalIncidents"] * 100).round(2)
    dist_df["DomesticRate"] = (dist_df["Domestic"] / dist_df["TotalIncidents"] * 100).round(2)
    dist_df = dist_df.sort_values(by="TotalIncidents", ascending=False)
    dist_df.to_csv(os.path.join(tbl_dir, "district_summary.csv"), index=False)

    fig, ax1 = plt.subplots(figsize=(13, 6))
    color = '#20639b'
    ax1.set_xlabel('Police District (CPD)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Total Incident Count', color=color, fontsize=11, fontweight='bold')
    ax1.bar(dist_df["district"], dist_df["TotalIncidents"], color=color, alpha=0.75, width=0.6)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()
    color2 = '#c0392b'
    ax2.set_ylabel('Arrest Rate (%)', color=color2, fontsize=11, fontweight='bold')
    ax2.plot(dist_df["district"], dist_df["ArrestRate"], color=color2, marker='o', linewidth=2, markersize=7)
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.set_ylim(0, 30)

    for i, row in enumerate(dist_df.itertuples()):
        ax2.annotate(f"{row.ArrestRate:.1f}%", (i, row.ArrestRate + 0.8), ha='center', fontsize=7.5, color=color2)

    plt.title('CPD District Comparison: Incident Volume vs. Arrest Rate (2024–2025)', fontsize=13, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig06_district_volume_vs_arrest_rate.png"), dpi=300)
    plt.close()

    # ==========================================
    # 9. FIGURE 7: TOP 20 COMMUNITY AREAS
    # ==========================================
    ca_df = df[df["community_area"] > 0].groupby("community_area").agg(
        TotalIncidents=("id", "count"),
        Arrests=("arrest_flag", "sum"),
        Domestic=("domestic_flag", "sum")
    ).reset_index()
    ca_df["ArrestRate"] = (ca_df["Arrests"] / ca_df["TotalIncidents"] * 100).round(2)
    ca_df["DomesticRate"] = (ca_df["Domestic"] / ca_df["TotalIncidents"] * 100).round(2)
    ca_df = ca_df.sort_values(by="TotalIncidents", ascending=False)
    ca_df.to_csv(os.path.join(tbl_dir, "community_area_summary.csv"), index=False)

    top20_ca = ca_df.head(20)
    plt.figure(figsize=(11, 6))
    ax = sns.barplot(x="TotalIncidents", y=top20_ca["community_area"].astype(str), data=top20_ca, palette="viridis")
    plt.title("Top 20 Chicago Community Areas by Crime Volume (2024–2025)", fontsize=13, fontweight='bold', pad=12)
    plt.xlabel("Total Incident Count", fontsize=11, fontweight='bold')
    plt.ylabel("Community Area Number", fontsize=11, fontweight='bold')
    for p in ax.patches:
        width = p.get_width()
        pct = (width / total_records) * 100
        ax.annotate(f"{int(width):,} ({pct:.1f}%)",
                    (width + 300, p.get_y() + p.get_height() / 2.),
                    va='center', fontsize=8.5, color='#222222')
    plt.xlim(0, top20_ca["TotalIncidents"].max() * 1.2)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig07_top20_community_areas.png"), dpi=300)
    plt.close()

    # ==========================================
    # 10. FIGURE 8: LOCATION GROUP DISTRIBUTION & ARREST RATE
    # ==========================================
    loc_grp = df.groupby("location_group").agg(
        TotalIncidents=("id", "count"),
        Arrests=("arrest_flag", "sum"),
        Domestic=("domestic_flag", "sum")
    ).reset_index()
    loc_grp["ArrestRate"] = (loc_grp["Arrests"] / loc_grp["TotalIncidents"] * 100).round(2)
    loc_grp["DomesticRate"] = (loc_grp["Domestic"] / loc_grp["TotalIncidents"] * 100).round(2)
    loc_grp = loc_grp.sort_values(by="TotalIncidents", ascending=False)
    loc_grp.to_csv(os.path.join(tbl_dir, "location_group_summary.csv"), index=False)

    plt.figure(figsize=(10, 5))
    ax = sns.barplot(x="TotalIncidents", y="location_group", data=loc_grp, palette="mako")
    plt.title("Incident Distribution Across Major Location Groups (2024–2025)", fontsize=13, fontweight='bold', pad=12)
    plt.xlabel("Total Incidents", fontsize=11, fontweight='bold')
    plt.ylabel("Location Group", fontsize=11, fontweight='bold')
    for p in ax.patches:
        width = p.get_width()
        pct = (width / total_records) * 100
        ax.annotate(f"{int(width):,} ({pct:.1f}%)",
                    (width + 2000, p.get_y() + p.get_height() / 2.),
                    va='center', fontsize=9, color='#222222')
    plt.xlim(0, loc_grp["TotalIncidents"].max() * 1.2)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig08_location_group_distribution.png"), dpi=300)
    plt.close()

    print("All EDA figures and statistical tables generated successfully!")

if __name__ == "__main__":
    run_eda()
