"""
Chicago Crime Incident and Public Safety Analytics Dashboard
Interactive BI Application matching the 4-Page Power BI Architecture:
- Page 1: Executive Public Safety Overview
- Page 2: Crime Type & Offense Analytics
- Page 3: Geographic & Spatial Hotspots
- Page 4: Temporal & Diurnal Heatmap
"""

import os
import psycopg2
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Configure Page
st.set_page_config(
    page_title="Chicago Crime & Public Safety BI Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid #2b5c8f;
    }
    .metric-value {
        font-size: 26px;
        font-weight: bold;
        color: #1f2937;
    }
    .metric-label {
        font-size: 13px;
        color: #6b7280;
        text-transform: uppercase;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner="Loading data from certified Analytical Mart...")
def load_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Try PostgreSQL first
    try:
        conn = psycopg2.connect(host='localhost', port=5432, user='postgres', password='root', dbname='chicago_crime_dw', connect_timeout=3)
        sql = """
        SELECT 
            year, quarter, month, monthname, dayname, dayofweek, isweekend,
            hour, timeband, crimecategorygroup, primarytype,
            district, communityarea, locationgroup,
            arrestflag, domesticflag, isnightincident, incidentcount
        FROM mart.PublicSafetyAnalyticsMart;
        """
        cur = conn.cursor()
        cur.execute(sql)
        cols = [desc[0].lower() for desc in cur.description]
        df = pd.DataFrame(cur.fetchall(), columns=cols)
        cur.close()
        conn.close()
        return df
    except Exception as e:
        # Fallback to curated CSV
        csv_path = os.path.join(base_dir, "data", "curated", "crimes_curated.csv")
        cols = [
            "year", "quarter", "month", "day_name", "day_of_week", "is_weekend",
            "hour", "time_band", "crime_category_group", "primary_type",
            "district", "community_area", "location_group",
            "arrest_flag", "domestic_flag", "is_night_incident"
        ]
        df = pd.read_csv(csv_path, usecols=cols, low_memory=False)
        df.columns = [c.replace("_", "") for c in df.columns]
        df["incidentcount"] = 1
        return df

df_all = load_data()

# ==========================================
# SIDEBAR FILTERS (SLICERS)
# ==========================================
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/9/9b/Flag_of_Chicago%2C_Illinois.svg", width=120)
st.sidebar.title("Dashboard Slicers")

# Year filter
selected_years = st.sidebar.multiselect("Incident Year", options=[2024, 2025], default=[2024, 2025])
if not selected_years:
    selected_years = [2024, 2025]

# Quarter filter
all_quarters = sorted(df_all["quarter"].unique())
selected_quarters = st.sidebar.multiselect("Quarter", options=all_quarters, default=all_quarters)

# Weekend filter
period_options = {"All Days": [0, 1], "Weekdays Only (Mon-Fri)": [0], "Weekends Only (Sat-Sun)": [1]}
selected_period_label = st.sidebar.radio("Day of Week Period", options=list(period_options.keys()))
selected_weekends = period_options[selected_period_label]

# Crime Category filter
all_categories = sorted(df_all["crimecategorygroup"].unique())
selected_categories = st.sidebar.multiselect("Crime Category", options=all_categories, default=all_categories)

# TimeBand filter
all_timebands = ["Morning", "Afternoon", "Evening", "Night"]
selected_timebands = st.sidebar.multiselect("Operational TimeBand", options=all_timebands, default=all_timebands)

# Apply filters
mask = (
    df_all["year"].isin(selected_years) &
    df_all["quarter"].isin(selected_quarters) &
    df_all["isweekend"].isin(selected_weekends) &
    df_all["crimecategorygroup"].isin(selected_categories) &
    df_all["timeband"].isin(selected_timebands)
)
df = df_all[mask]

# ==========================================
# TOP KPI METRICS BAR
# ==========================================
st.title("🛡️ City of Chicago Public Safety Analytics Platform")
st.markdown("**Batch Data Warehouse & Business Intelligence Dashboard** | *Scope: 2024–2025 Reported Incidents*")

total_incidents = len(df)
total_arrests = int(df["arrestflag"].sum())
arrest_rate = (total_arrests / total_incidents * 100) if total_incidents > 0 else 0.0
total_domestic = int(df["domesticflag"].sum())
domestic_rate = (total_domestic / total_incidents * 100) if total_incidents > 0 else 0.0
total_night = int(df["isnightincident"].sum())
night_rate = (total_night / total_incidents * 100) if total_incidents > 0 else 0.0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Incidents", f"{total_incidents:,}")
col2.metric("Recorded Arrests", f"{total_arrests:,}", f"{arrest_rate:.1f}% Clearance", delta_color="off")
col3.metric("Domestic Violence", f"{total_domestic:,}", f"{domestic_rate:.1f}% Share", delta_color="off")
col4.metric("Night Incidents", f"{total_night:,}", f"{night_rate:.1f}% Share", delta_color="off")
col5.metric("Distinct Offenses", f"{df['primarytype'].nunique():,}")

st.markdown("---")

# ==========================================
# MULTI-PAGE TABS
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Page 1: Executive Overview",
    "⚖️ Page 2: Crime Type Analytics",
    "📍 Page 3: Geographic Hotspots",
    "🕒 Page 4: Temporal & Diurnal Heatmap"
])

# ------------------------------------------
# TAB 1: EXECUTIVE OVERVIEW
# ------------------------------------------
with tab1:
    st.subheader("Executive Public Safety Trends and Macro Patterns")
    row1_col1, row1_col2 = st.columns([7, 5])
    
    with row1_col1:
        # Monthly Trend Chart
        monthly_df = df.groupby(["year", "month"]).agg(
            Incidents=("incidentcount", "sum"),
            Arrests=("arrestflag", "sum")
        ).reset_index()
        monthly_df["YearMonth"] = monthly_df["year"].astype(str) + "-" + monthly_df["month"].astype(str).str.zfill(2)
        monthly_df["ArrestRate"] = (monthly_df["Arrests"] / monthly_df["Incidents"] * 100).round(2)
        
        fig_monthly = go.Figure()
        fig_monthly.add_trace(go.Bar(
            x=monthly_df["YearMonth"],
            y=monthly_df["Incidents"],
            name="Monthly Incidents",
            marker_color="#2b5c8f"
        ))
        fig_monthly.add_trace(go.Scatter(
            x=monthly_df["YearMonth"],
            y=monthly_df["ArrestRate"],
            name="Arrest Rate (%)",
            yaxis="y2",
            mode="lines+markers",
            line=dict(color="#d62728", width=2.5)
        ))
        fig_monthly.update_layout(
            title="Monthly Incident Volume vs. Arrest Clearance Rate",
            yaxis=dict(title="Total Incidents"),
            yaxis2=dict(title="Arrest Rate (%)", overlaying="y", side="right", range=[0, 30]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=380
        )
        st.plotly_chart(fig_monthly, use_container_width=True)

    with row1_col2:
        # Donut Chart by Crime Category Group
        cat_df = df["crimecategorygroup"].value_counts().reset_index()
        cat_df.columns = ["Category", "Count"]
        fig_donut = px.pie(
            cat_df, values="Count", names="Category", hole=0.45,
            title="Incident Distribution by Offense Category",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_donut.update_layout(height=380)
        st.plotly_chart(fig_donut, use_container_width=True)

    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        tb_df = df.groupby("timeband").agg(
            Incidents=("incidentcount", "sum"),
            Arrests=("arrestflag", "sum")
        ).reset_index()
        tb_df["ArrestRate"] = (tb_df["Arrests"] / tb_df["Incidents"] * 100).round(2)
        fig_tb = px.bar(
            tb_df, x="timeband", y="Incidents", color="timeband",
            category_orders={"timeband": ["Morning", "Afternoon", "Evening", "Night"]},
            title="Incident Volume Across Operational TimeBands",
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        fig_tb.update_layout(height=340, showlegend=False)
        st.plotly_chart(fig_tb, use_container_width=True)

    with row2_col2:
        weekend_summary = df.groupby("dayname").agg(
            Incidents=("incidentcount", "sum")
        ).reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]).reset_index()
        fig_days = px.bar(
            weekend_summary, x="dayname", y="Incidents",
            title="Incident Volume by Day of Week",
            color_discrete_sequence=["#1f77b4"]
        )
        fig_days.update_layout(height=340)
        st.plotly_chart(fig_days, use_container_width=True)

# ------------------------------------------
# TAB 2: CRIME TYPE ANALYTICS
# ------------------------------------------
with tab2:
    st.subheader("Offense Classification and Clearance Disparity")
    
    col_pt1, col_pt2 = st.columns([7, 5])
    with col_pt1:
        top15_pt = df["primarytype"].value_counts().head(15).reset_index()
        top15_pt.columns = ["PrimaryType", "Count"]
        fig_top_pt = px.bar(
            top15_pt, x="Count", y="PrimaryType", orientation="h",
            title="Top 15 Primary Offenses by Volume",
            color="Count", color_continuous_scale="Blues"
        )
        fig_top_pt.update_layout(yaxis=dict(autorange="reversed"), height=450)
        st.plotly_chart(fig_top_pt, use_container_width=True)

    with col_pt2:
        # Scatter: Volume vs Clearance Rate
        pt_rates = df.groupby("primarytype").agg(
            Incidents=("incidentcount", "sum"),
            Arrests=("arrestflag", "sum"),
            Domestic=("domesticflag", "sum")
        ).reset_index()
        pt_rates["ArrestRate"] = (pt_rates["Arrests"] / pt_rates["Incidents"] * 100).round(2)
        pt_top20_rates = pt_rates.sort_values(by="Incidents", ascending=False).head(20)
        
        fig_scatter = px.scatter(
            pt_top20_rates, x="Incidents", y="ArrestRate", text="primarytype",
            size="Domestic", color="ArrestRate",
            color_continuous_scale="Viridis",
            title="Offense Clearance Matrix (Volume vs. Arrest Rate %)",
            labels={"Incidents": "Total Incident Volume", "ArrestRate": "Arrest Rate (%)"}
        )
        fig_scatter.update_traces(textposition='top center')
        fig_scatter.update_layout(height=450)
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("### Primary Offense Clearance Summary Table")
    st.dataframe(pt_rates.sort_values("Incidents", ascending=False).head(20), use_container_width=True)

# ------------------------------------------
# TAB 3: GEOGRAPHIC HOTSPOTS
# ------------------------------------------
with tab3:
    st.subheader("Geographic & Spatial Distribution Across Chicago Districts")
    
    geo_col1, geo_col2 = st.columns([6, 6])
    with geo_col1:
        dist_df = df.groupby("district").agg(
            Incidents=("incidentcount", "sum"),
            Arrests=("arrestflag", "sum"),
            Domestic=("domesticflag", "sum")
        ).reset_index()
        dist_df["ArrestRate"] = (dist_df["Arrests"] / dist_df["Incidents"] * 100).round(2)
        dist_df = dist_df.sort_values(by="Incidents", ascending=False)
        
        fig_dist = px.bar(
            dist_df, x="district", y="Incidents",
            color="ArrestRate", color_continuous_scale="Reds",
            title="Incidents and Arrest Rate (%) by Police District",
            labels={"district": "CPD District", "Incidents": "Total Incidents"}
        )
        fig_dist.update_layout(height=420)
        st.plotly_chart(fig_dist, use_container_width=True)

    with geo_col2:
        loc_df = df.groupby("locationgroup").agg(
            Incidents=("incidentcount", "sum"),
            Arrests=("arrestflag", "sum")
        ).reset_index()
        loc_df["ArrestRate"] = (loc_df["Arrests"] / loc_df["Incidents"] * 100).round(2)
        fig_loc = px.pie(
            loc_df, values="Incidents", names="locationgroup",
            title="Premise Environmental Location Breakdown",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_loc.update_layout(height=420)
        st.plotly_chart(fig_loc, use_container_width=True)

    st.markdown("### Top Community Areas by Incident Volume")
    ca_df = df[df["communityarea"] > 0].groupby("communityarea").agg(
        TotalIncidents=("incidentcount", "sum"),
        Arrests=("arrestflag", "sum"),
        Domestic=("domesticflag", "sum")
    ).reset_index()
    ca_df["ArrestRate"] = (ca_df["Arrests"] / ca_df["TotalIncidents"] * 100).round(2)
    ca_df["DomesticRate"] = (ca_df["Domestic"] / ca_df["TotalIncidents"] * 100).round(2)
    st.dataframe(ca_df.sort_values(by="TotalIncidents", ascending=False).head(15), use_container_width=True)

# ------------------------------------------
# TAB 4: TEMPORAL & DIURNAL HEATMAP
# ------------------------------------------
with tab4:
    st.subheader("Temporal Concentration: Diurnal Hour x Day of Week Heatmap")
    
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    heat_pivot = df.pivot_table(
        index="dayname", columns="hour", values="incidentcount", aggfunc="sum", fill_value=0
    ).reindex(days_order)
    
    fig_heat = px.imshow(
        heat_pivot,
        labels=dict(x="Hour of Day (0–23)", y="Day of Week", color="Incidents"),
        x=heat_pivot.columns,
        y=heat_pivot.index,
        color_continuous_scale="YlOrRd",
        title="24-Hour Diurnal Crime Concentration Matrix"
    )
    fig_heat.update_layout(height=450)
    st.plotly_chart(fig_heat, use_container_width=True)
    
    st.markdown("#### Hourly Profile: Weekday vs. Weekend")
    hourly_split = df.groupby(["hour", "isweekend"]).agg(Incidents=("incidentcount", "sum")).reset_index()
    hourly_split["Period"] = hourly_split["isweekend"].apply(lambda x: "Weekend (Sat-Sun)" if x == 1 else "Weekday (Mon-Fri)")
    fig_hourly = px.line(
        hourly_split, x="hour", y="Incidents", color="Period",
        title="Hourly Distribution Comparison (Weekday vs. Weekend)",
        labels={"hour": "Hour of Day (0–23)", "Incidents": "Total Incidents"}
    )
    fig_hourly.update_layout(height=350)
    st.plotly_chart(fig_hourly, use_container_width=True)
