
# climate_dashboard_final.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns


# PAGE CONFIG
st.set_page_config(page_title="🌍 Infosys Climate Dashboard", page_icon="🌎", layout="wide")


# STYLING

st.markdown("""
<style>
.stApp { background-color: #000; color: white; font-family: 'Helvetica Neue', sans-serif; }
[data-testid="stSidebar"] { background-color: #000; }
[data-testid="stSidebar"] * { color: white !important; }
.metric-card {
    background-color: #111; 
    padding: 18px; 
    border-radius: 12px; 
    text-align: center;
    box-shadow: 0 0 8px rgba(0,191,255,0.4);
}
.metric-card h3 { font-size: 18px; color: #00BFFF; margin-bottom: 4px; }
.metric-card p { font-size: 22px; font-weight: bold; color: white; }
</style>
""", unsafe_allow_html=True)

# FILE UPLOAD
st.sidebar.header("📂 Upload Dataset")
uploaded_file = st.sidebar.file_uploader("Upload your dataset (df_clean.csv)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if "last_updated" in df.columns:
        df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce")
else:
    st.warning("⚠️ Please upload your `df_clean.csv` file to continue.")
    st.stop()


# SIDEBAR FILTERS

st.sidebar.header("🔍 Filters")
if "country" in df.columns:
    countries = st.sidebar.multiselect("🌎 Select Country", sorted(df["country"].dropna().unique()))
    if countries:
        df = df[df["country"].isin(countries)]

if "last_updated" in df.columns:
    min_date, max_date = df["last_updated"].min().date(), df["last_updated"].max().date()
    date_range = st.sidebar.date_input("🗓 Date Range", [min_date, max_date])
    if len(date_range) == 2:
        start, end = date_range
        df = df[(df["last_updated"].dt.date >= start) & (df["last_updated"].dt.date <= end)]

# NAVIGATION

st.sidebar.title("🌐 Navigation")
page = st.sidebar.radio(
    "Navigate",
    [
        "🏠 Home",
        "🌡️ Weather Overview",
        "🌬️ Air Quality",
        "📊 Correlation & Map",
        "📈 Global Trends",
        "🌎 Country Comparison",
        "🏆 Rankings",
        "🌺 Flower Growth Advisor",
        "🌪️ Extreme Events Analysis"
    ]
)


# 🏠 HOME

if page == "🏠 Home":
    st.title("🌍 Infosys Climate Intelligence Dashboard")
    st.markdown("Welcome to your **interactive climate analytics hub** — visualize weather, air quality, and trends.")
    st.image("https://images.unsplash.com/photo-1506744038136-46273834b3fb", use_container_width=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><h3>🌡️ Avg Temp (°C)</h3><p>{df["temperature_celsius"].mean():.1f}</p></div>', unsafe_allow_html=True)
    with col2:
        if "humidity" in df.columns:
            st.markdown(f'<div class="metric-card"><h3>💧 Avg Humidity (%)</h3><p>{df["humidity"].mean():.1f}</p></div>', unsafe_allow_html=True)
    with col3:
        aq_cols = [c for c in df.columns if "PM2.5" in c]
        if aq_cols:
            st.markdown(f'<div class="metric-card"><h3>🌫️ Avg PM2.5</h3><p>{df[aq_cols[0]].mean():.1f}</p></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><h3>🧾 Total Records</h3><p>{len(df):,}</p></div>', unsafe_allow_html=True)
    st.dataframe(df.head(10), use_container_width=True)


# 🌡️ WEATHER OVERVIEW

elif page == "🌡️ Weather Overview":
    st.title("🌡️ Weather Overview")
    fig = px.histogram(df, x="temperature_celsius", nbins=40, color_discrete_sequence=["red"])
    fig.update_layout(template="plotly_dark", paper_bgcolor="#000")
    st.plotly_chart(fig, use_container_width=True)

    if "humidity" in df.columns:
        fig2 = px.scatter(df, x="temperature_celsius", y="humidity", color="country", opacity=0.7)
        fig2.update_layout(template="plotly_dark", paper_bgcolor="#000")
        st.plotly_chart(fig2, use_container_width=True)

# 🌬️ AIR QUALITY

elif page == "🌬️ Air Quality":
    st.title("🌬️ Air Quality Overview")
    aq_cols = [c for c in df.columns if "air_quality" in c]
    if aq_cols:
        mean_aq = df.groupby("country")[aq_cols].mean().reset_index()
        fig = px.bar(mean_aq, x="country", y=aq_cols, barmode="group", color_discrete_sequence=px.colors.sequential.Plasma)
        fig.update_layout(template="plotly_dark", paper_bgcolor="#000")
        st.plotly_chart(fig, use_container_width=True)


# 📊 CORRELATION & MAP
elif page == "📊 Correlation & Map":
    st.title("📊 Correlation & Geographic Insights")
    num_df = df.select_dtypes(include=["float64", "int64"])
    if not num_df.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(num_df.corr(), cmap="coolwarm", center=0)
        st.pyplot(fig)

    if {"latitude", "longitude"}.issubset(df.columns):
        metric = st.selectbox("Select Metric", ["temperature_celsius", "humidity", "air_quality_PM2.5"])
        fig_map = px.scatter_geo(df, lat="latitude", lon="longitude", color=metric,
                                 color_continuous_scale=["blue", "red"], hover_name="country",
                                 projection="natural earth")
        fig_map.update_layout(template="plotly_dark", paper_bgcolor="#000")
        st.plotly_chart(fig_map, use_container_width=True)


# 📈 GLOBAL TRENDS

elif page == "📈 Global Trends":
    st.title("📈 Global Climate Trends")
    if "last_updated" in df.columns:
        metric = st.selectbox("Select Metric", ["temperature_celsius", "humidity", "air_quality_PM2.5"])
        trend_df = df.groupby("last_updated")[metric].mean().reset_index()
        trend_df["MA7"] = trend_df[metric].rolling(7).mean()
        fig = px.line(trend_df, x="last_updated", y=["MA7", metric])
        fig.update_layout(template="plotly_dark", paper_bgcolor="#000")
        st.plotly_chart(fig, use_container_width=True)


# 🌎 COUNTRY COMPARISON (with Cool/Hot Rankings)

elif page == "🌎 Country Comparison":
    st.title("🌎 Country Comparison Dashboard")

    metrics = ["temperature_celsius", "humidity", "air_quality_PM2.5"]
    selected_metric = st.selectbox("Select Metric", metrics)

    comp_df = df.groupby("country")[selected_metric].mean().reset_index().sort_values(selected_metric, ascending=False)

    fig = px.bar(comp_df, x="country", y=selected_metric, color=selected_metric, color_continuous_scale="Viridis")
    fig.update_layout(template="plotly_dark", paper_bgcolor="#000")
    st.plotly_chart(fig, use_container_width=True)

    # ---- Cooler & Hotter Places Ranking ----
    st.subheader("🌡️ Temperature Rankings by Country")
    if "temperature_celsius" in df.columns:
        temp_df = df.groupby("country")["temperature_celsius"].mean().reset_index().dropna()
        hottest = temp_df.sort_values("temperature_celsius", ascending=False).head(5)
        coolest = temp_df.sort_values("temperature_celsius", ascending=True).head(5)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("🔥 **Top 5 Hottest Countries**")
            fig_hot = px.bar(hottest, x="country", y="temperature_celsius", color="temperature_celsius",
                             color_continuous_scale="reds")
            fig_hot.update_layout(template="plotly_dark", paper_bgcolor="#000", showlegend=False)
            st.plotly_chart(fig_hot, use_container_width=True)

        with col2:
            st.markdown("❄️ **Top 5 Coolest Countries**")
            fig_cool = px.bar(coolest, x="country", y="temperature_celsius", color="temperature_celsius",
                              color_continuous_scale="blues_r")
            fig_cool.update_layout(template="plotly_dark", paper_bgcolor="#000", showlegend=False)
            st.plotly_chart(fig_cool, use_container_width=True)


# 🏆 RANKINGS

elif page == "🏆 Rankings":
    st.title("🏆 Country Rankings")
    col = st.selectbox("Select Metric", ["temperature_celsius", "humidity", "air_quality_PM2.5"])
    rank_df = df.groupby("country")[col].mean().reset_index().sort_values(col, ascending=False)
    st.dataframe(rank_df.reset_index(drop=True), use_container_width=True)
    fig = px.bar(rank_df.head(10), x="country", y=col, color="country")
    fig.update_layout(template="plotly_dark", paper_bgcolor="#000")
    st.plotly_chart(fig, use_container_width=True)

# 🌺 FLOWER GROWTH ADVISOR

elif page == "🌺 Flower Growth Advisor":
    st.title("🌺 Flower Growth Advisor")
    flower = st.selectbox("Select Flower", ["Rose", "Tulip", "Lily", "Sunflower", "Orchid", "Marigold"])
    country = st.selectbox("Select Country", sorted(df["country"].dropna().unique()))

    flower_data = {
        "Rose": {"temp": (15, 28), "weather": "Moderate", "start_month": 10},
        "Tulip": {"temp": (10, 18), "weather": "Cool", "start_month": 12},
        "Lily": {"temp": (16, 25), "weather": "Mild", "start_month": 9},
        "Sunflower": {"temp": (20, 30), "weather": "Sunny", "start_month": 6},
        "Orchid": {"temp": (18, 28), "weather": "Humid", "start_month": 3},
        "Marigold": {"temp": (17, 27), "weather": "Warm", "start_month": 7}
    }

    if st.button("Check Growth Advice"):
        if country not in df["country"].unique():
            st.error("❌ Invalid country. Please choose from the list.")
        else:
            info = flower_data[flower]
            st.success(f"✅ {flower} grows well in {country}")
            st.write(f"🌡️ Ideal Temperature: {info['temp'][0]}°C - {info['temp'][1]}°C")
            st.write(f"☀️ Preferred Weather: {info['weather']}")
            st.write(f"📅 Best Month to Start: {pd.Timestamp(info['start_month'], 1, 1).month_name()}")
# 🌪️ EXTREME EVENTS ANALYSIS
elif page == "🌪️ Extreme Events Analysis":
    st.title("🌪️ Extreme Events Analysis")

    if "last_updated" in df.columns:
        df["year"] = df["last_updated"].dt.year
        df["month"] = df["last_updated"].dt.month

        country_sel = st.selectbox("Select Country", ["All"] + sorted(df["country"].dropna().unique()))
        df_sel = df if country_sel == "All" else df[df["country"] == country_sel]

        agg_type = st.radio("Aggregate By", ["Month", "Year"], horizontal=True)
        if agg_type == "Month":
            agg_df = df_sel.groupby("month").size().reset_index(name="Event Count")
            x_col = "month"
        else:
            agg_df = df_sel.groupby("year").size().reset_index(name="Event Count")
            x_col = "year"

        fig = px.bar(agg_df, x=x_col, y="Event Count", color="Event Count", color_continuous_scale="Viridis")
        fig.update_layout(template="plotly_dark", paper_bgcolor="#000")
        st.plotly_chart(fig, use_container_width=True)

        if {"latitude", "longitude"}.issubset(df_sel.columns):
            df_latlon = df_sel.dropna(subset=["latitude", "longitude"])
            if not df_latlon.empty:
                st.subheader("🗺️ Extreme Events Map")
                fig_map = px.scatter_geo(df_latlon, lat="latitude", lon="longitude",
                                         color="temperature_celsius",
                                         hover_name="country",
                                         color_continuous_scale=["blue", "red"],
                                         projection="natural earth")
                fig_map.update_layout(template="plotly_dark", paper_bgcolor="#000")
                st.plotly_chart(fig_map, use_container_width=True)
