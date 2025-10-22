import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from scipy.stats import skew, kurtosis, zscore
import requests


# ---------------------------
# PAGE CONFIG & STYLING
# ---------------------------
st.set_page_config(page_title="ClimateScope: Weather & Air Quality Dashboard",
                   page_icon="🌍",
                   layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #000000, #434343); /* dark gradient */
        color: #FFFFFF; /* white text */
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    h1 { color: #00e676; text-align:center; }
    .stDownloadButton>button { background-color: #00e676; color: white; }
    </style>
    """,
    unsafe_allow_html=True,
)


st.title("🌦️ ClimateScope: Unified Weather & Air Quality Dashboard")


# ---------------------------
# SIDEBAR: OPTIONS
# ---------------------------
st.sidebar.header("Input Options & Settings")
input_mode = st.sidebar.radio("Data source:", ["Upload Dataset", "Live API"]) 


dark_mode = st.sidebar.checkbox("Enable Dark Mode")
if dark_mode:
    st.markdown(
        """
        <style>
        .stApp { background-color: #0b1020 !important; color: #e6eef8 !important; }
        .css-1d391kg { color: #e6eef8; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------
# DATA LOADING
# ---------------------------
@st.cache_data
def load_csv_from_upload(uploaded_file):
    df = pd.read_csv(uploaded_file, parse_dates=["last_updated"]) if uploaded_file is not None else None
    return df


@st.cache_data
def load_df_from_path(path):
    df = pd.read_csv(path, parse_dates=["last_updated"]) if path else None
    return df


# DataFrame placeholder
df_clean = None


if input_mode == "Upload Dataset":
    uploaded_file = st.sidebar.file_uploader("Upload your cleaned dataset (.csv)", type=["csv"])
    if uploaded_file is not None:
        try:
            df_clean = load_csv_from_upload(uploaded_file)
            st.sidebar.success(f"Loaded {df_clean.shape[0]:,} rows, {df_clean.shape[1]} cols")
        except Exception as e:
            st.sidebar.error("Failed to read CSV. Ensure `last_updated` is a datetime column.")
            st.stop()
    else:
        st.info("Please upload a CSV to continue.")
        st.stop()


else:  # Live API
    st.sidebar.info("Fetch current weather + air pollution for a single city using OpenWeatherMap")
    city = st.sidebar.text_input("City (for live data)", "New Delhi")
    api_key = st.sidebar.text_input("OpenWeatherMap API Key", type="password")
    if not api_key:
        st.warning("Enter API key to fetch live data")
        st.stop()


    # Query current weather and air pollution and create a single-row dataframe
    try:
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        w = requests.get(weather_url, timeout=10).json()
        if "coord" not in w:
            st.error("City not found or API key invalid.")
            st.stop()
        lat, lon = w["coord"]["lat"], w["coord"]["lon"]
        air_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
        a = requests.get(air_url, timeout=10).json()


        # Build a small DataFrame with consistent columns so visualizations work (single record)
        rec = {
            "country": w.get("sys", {}).get("country", city),
            "location_name": w.get("name", city),
            "last_updated": pd.to_datetime(w.get("dt", pd.Timestamp.now()), unit="s"),
            "temperature_celsius": w.get("main", {}).get("temp"),
            "feels_like_celsius": w.get("main", {}).get("feels_like"),
            "humidity": w.get("main", {}).get("humidity"),
            "wind_kph": w.get("wind", {}).get("speed") * 3.6 if w.get("wind", {}).get("speed") is not None else None,
            "pressure_mb": w.get("main", {}).get("pressure"),
            "precip_mm": 0.0,
            "cloud": w.get("clouds", {}).get("all"),
            "visibility_km": (w.get("visibility") or 0) / 1000,
            "uv_index": None,
            "air_quality_PM2.5": a.get("list", [{}])[0].get("components", {}).get("pm2_5") if a.get("list") else None,
            "air_quality_PM10": a.get("list", [{}])[0].get("components", {}).get("pm10") if a.get("list") else None,
        }
        df_clean = pd.DataFrame([rec])
        st.sidebar.success("Live data fetched — dashboard will work with a single-record DataFrame")


    except Exception as e:
        st.sidebar.error(f"Live fetch failed: {e}")
        st.stop()


# ---------------------------
# STANDARDIZE COLUMNS LIST
# ---------------------------
numeric_cols = [
    "temperature_celsius", "feels_like_celsius", "humidity", "wind_kph", "gust_kph",
    "pressure_mb", "precip_mm", "cloud", "visibility_km", "uv_index",
    "air_quality_Carbon_Monoxide", "air_quality_Ozone", "air_quality_Nitrogen_dioxide",
    "air_quality_Sulphur_dioxide", "air_quality_PM2.5", "air_quality_PM10",
    "air_quality_us-epa-index", "air_quality_gb-defra-index"
]


# Warn if expected columns missing — but continue with available ones
existing_numeric_cols = [c for c in numeric_cols if c in df_clean.columns]
missing_cols = list(set(numeric_cols) - set(existing_numeric_cols))
if missing_cols:
    st.warning(f"Missing expected numeric columns (will skip these): {sorted(missing_cols)}")


# ---------------------------
# OUTLIER REMOVAL: z-score on selected columns
# ---------------------------
cols_to_clean = [c for c in ["pressure_mb", "air_quality_Sulphur_dioxide"] if c in df_clean.columns]


# Work on a copy and remove extreme z-score outliers (replace with NaN)
df_cleaned = df_clean.copy()
for col in cols_to_clean:
    valid_idx = df_cleaned[col].dropna().index
    if len(valid_idx) > 0:
        z_scores = zscore(df_cleaned.loc[valid_idx, col])
        mask = abs(z_scores) < 3
        df_cleaned.loc[valid_idx, col] = df_cleaned.loc[valid_idx, col].where(mask, np.nan)


# ---------------------------
# DERIVED COLUMNS: month, season
# ---------------------------
if "last_updated" in df_cleaned.columns:
    try:
        df_cleaned["last_updated"] = pd.to_datetime(df_cleaned["last_updated"])
    except Exception:
        pass
    df_cleaned["month"] = df_cleaned["last_updated"].dt.month
else:
    df_cleaned["month"] = 1


def month_to_season(m):
    if m in [4, 5, 6]:
        return "Summer"
    elif m in [7, 8, 9]:
        return "Rainy"
    elif m in [10, 11]:
        return "Light Season"
    else:
        return "Winter"


if "month" in df_cleaned.columns:
    df_cleaned["season"] = df_cleaned["month"].apply(month_to_season)
else:
    df_cleaned["season"] = "Unknown"


# ---------------------------
# DOWNLOAD HELPER
# ---------------------------
def download_csv(df, filename):
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(label=f"Download {filename}", data=csv_bytes, file_name=filename, mime="text/csv")


# ---------------------------
# KPIs
# ---------------------------
st.markdown("### Key Climate KPIs")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Temperature (°C)", f"{df_cleaned['temperature_celsius'].mean():.2f}" if 'temperature_celsius' in df_cleaned.columns else "N/A")
col2.metric("Max Wind Speed (kph)", f"{df_cleaned['wind_kph'].max():.2f}" if 'wind_kph' in df_cleaned.columns else "N/A")
col3.metric("Avg PM2.5 (µg/m³)", f"{df_cleaned['air_quality_PM2.5'].mean():.2f}" if 'air_quality_PM2.5' in df_cleaned.columns else "N/A")
col4.metric("Total Records", f"{len(df_cleaned):,}")


# Option to download cleaned dataset
with st.expander("Download cleaned dataset"):
    download_csv(df_cleaned, "df_cleaned.csv")


# ---------------------------
# DESCRIPTIVE STATS
# ---------------------------
st.header("📊 Exploratory Data Analysis")
with st.expander("Basic Statistics (numeric columns)"):
    if existing_numeric_cols:
        st.dataframe(df_cleaned[existing_numeric_cols].describe().T.style.format("{:.2f}"), use_container_width=True)
    else:
        st.info("No numeric columns found for descriptive stats.")


# ---------------------------
# HISTOGRAM GRID (first 9 numeric)
# ---------------------------
st.subheader("Variable Distributions: First 9 Numeric Features")
plot_cols = existing_numeric_cols[:9]
if plot_cols:
    fig_hist = plt.figure(figsize=(16, 12))
    for i, col in enumerate(plot_cols, 1):
        ax = fig_hist.add_subplot(3, 3, i)
        sns.histplot(df_cleaned[col].dropna(), kde=True, bins=30, ax=ax)
        ax.set_title(f"Distribution of {col}")
    plt.tight_layout()
    st.pyplot(fig_hist)
else:
    st.info("No numeric columns available to show distributions.")


# ---------------------------
# SKEWNESS & KURTOSIS BEFORE/AFTER
# ---------------------------
st.subheader("Distribution Shape: Skewness & Kurtosis (Before & After Outlier Removal)")


# compute only for existing numeric columns
stats_before = []
stats_after = []
for col in existing_numeric_cols:
    before_data = df_clean[col].dropna() if col in df_clean.columns else pd.Series(dtype=float)
    after_data = df_cleaned[col].dropna() if col in df_cleaned.columns else pd.Series(dtype=float)
    stats_before.append([col, float(skew(before_data)) if len(before_data)>0 else np.nan, float(kurtosis(before_data)) if len(before_data)>0 else np.nan])
    stats_after.append([col, float(skew(after_data)) if len(after_data)>0 else np.nan, float(kurtosis(after_data)) if len(after_data)>0 else np.nan])


if stats_before:
    df_stats_before = pd.DataFrame(stats_before, columns=["Variable","Skewness","Kurtosis"]).set_index("Variable")
    df_stats_after = pd.DataFrame(stats_after, columns=["Variable","Skewness","Kurtosis"]).set_index("Variable")


    fig_skew, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))
    sns.heatmap(df_stats_before, annot=True, cmap="RdYlGn", center=0, fmt='.1f', ax=ax1)
    ax1.set_title("Before Outlier Removal")
    sns.heatmap(df_stats_after, annot=True, cmap="RdYlGn", center=0, fmt='.1f', ax=ax2)
    ax2.set_title("After Outlier Removal")
    plt.tight_layout()
    st.pyplot(fig_skew)
else:
    st.info("Insufficient numeric data to compute skewness/kurtosis.")


# ---------------------------
# CORRELATION HEATMAP
# ---------------------------
st.subheader("Correlation Heatmap of Weather & Air Quality")
if len(existing_numeric_cols) >= 2:
    fig_corr, ax = plt.subplots(figsize=(12, 8))
    corr = df_cleaned[existing_numeric_cols].corr()
    sns.heatmap(corr, annot=True, cmap="coolwarm", center=0, ax=ax)
    ax.set_title("Correlation Heatmap")
    st.pyplot(fig_corr)
else:
    st.info("Need at least 2 numeric columns for correlation heatmap.")


# ---------------------------
# SEASONAL TRENDS
# ---------------------------
st.subheader("Seasonal Patterns: Monthly Averages of Key Indicators")
cols_to_analyze = [c for c in ["temperature_celsius","precip_mm","humidity","wind_kph","air_quality_PM2.5","air_quality_PM10","uv_index"] if c in df_cleaned.columns]
if "month" in df_cleaned.columns and cols_to_analyze:
    monthly_avg = df_cleaned.groupby("month")[cols_to_analyze].mean()
    fig_season = plt.figure(figsize=(12, 7))
    monthly_avg.plot(kind="line", marker="o", ax=fig_season.gca())
    plt.title("Monthly Average Indicators")
    plt.xlabel("Month")
    plt.ylabel("Average Value")
    plt.grid(True, linestyle='--', alpha=0.6)
    st.pyplot(fig_season)
else:
    st.info("Not enough data/columns to show seasonal patterns.")


# ---------------------------
# CHOROPLETH: Monthly Average Temperature by Country
# ---------------------------
st.subheader("🌡️ Monthly Average Temperature by Country (Animated)")
if "country" in df_cleaned.columns and "temperature_celsius" in df_cleaned.columns and "last_updated" in df_cleaned.columns:
    monthly_temp = (
        df_cleaned
        .groupby([df_cleaned['country'], df_cleaned['last_updated'].dt.month])['temperature_celsius']
        .mean()
        .reset_index()
    )
    monthly_temp.rename(columns={'last_updated':'month'}, inplace=True)
    try:
        fig_chor = px.choropleth(
            monthly_temp,
            locations='country',
            locationmode='country names',
            color='temperature_celsius',
            hover_name='country',
            animation_frame='month',
            color_continuous_scale='RdBu_r',
            title='Monthly Average Temperature by Country'
        )
        st.plotly_chart(fig_chor, use_container_width=True)
    except Exception as e:
        st.error(f"Choropleth failed: {e}")
else:
    st.info("Country or temperature data missing for choropleth.")


# ---------------------------
# EXTREME EVENTS DETECTION & VISUALS
# ---------------------------
st.header("⚠️ Extreme Weather Events")
extreme_conditions = {
    "Heatwave (>40°C)": df_cleaned['temperature_celsius'] > 40 if 'temperature_celsius' in df_cleaned.columns else pd.Series([False]*len(df_cleaned)),
    "Cold Wave (<0°C)": df_cleaned['temperature_celsius'] < 0 if 'temperature_celsius' in df_cleaned.columns else pd.Series([False]*len(df_cleaned)),
    "Heavy Rain (>100mm)": df_cleaned['precip_mm'] > 100 if 'precip_mm' in df_cleaned.columns else pd.Series([False]*len(df_cleaned)),
    "Storm (>80kph)": df_cleaned['wind_kph'] > 80 if 'wind_kph' in df_cleaned.columns else pd.Series([False]*len(df_cleaned)),
    "High Pollution (PM2.5 >150)": df_cleaned['air_quality_PM2.5'] > 150 if 'air_quality_PM2.5' in df_cleaned.columns else pd.Series([False]*len(df_cleaned)),
}


extreme_events = {}
for name, cond in extreme_conditions.items():
    df_e = df_cleaned[cond].copy()
    if not df_e.empty and 'last_updated' in df_e.columns:
        df_e['month'] = df_e['last_updated'].dt.month
    extreme_events[name] = df_e


selected_event = st.selectbox("Select Extreme Event Type", list(extreme_events.keys()))
sel_df = extreme_events[selected_event]
if not sel_df.empty:
    st.dataframe(sel_df[[c for c in ['country','location_name','last_updated','temperature_celsius','precip_mm','wind_kph','air_quality_PM2.5'] if c in sel_df.columns]].head(15))
    download_csv(sel_df, f"{selected_event.replace(' ','_').replace('>','').replace('<','')}_events.csv")
else:
    st.info("No records for this event type.")


# Monthly counts plot
if any(not d.empty for d in extreme_events.values()):
    fig_ev, ax = plt.subplots(figsize=(12,6))
    for name, d in extreme_events.items():
        if not d.empty and 'last_updated' in d.columns:
            counts = d['last_updated'].dt.month.value_counts().sort_index()
            ax.plot(counts.index, counts.values, marker='o', label=name)
    ax.set_title('Extreme Weather Events - Monthly Counts')
    ax.set_xlabel('Month')
    ax.set_ylabel('Number of Events')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.6)
    st.pyplot(fig_ev)
else:
    st.info("No extreme events detected in dataset.")


# ---------------------------
# TOP COUNTRIES WITH EXTREME EVENTS
# ---------------------------
all_events_concat = pd.concat([d for d in extreme_events.values()]) if any(not d.empty for d in extreme_events.values()) else pd.DataFrame()
if not all_events_concat.empty and 'country' in all_events_concat.columns:
    top_countries = all_events_concat['country'].value_counts().head(10)
    fig_top = plt.figure(figsize=(14,6))
    sns.barplot(x=top_countries.index, y=top_countries.values, palette='viridis')
    plt.xticks(rotation=45, ha='right')
    plt.title('Top Countries with Most Extreme Events')
    plt.ylabel('Number of Events')
    st.pyplot(fig_top)


# ---------------------------
# MAP OF EXTREME EVENTS (if lat/lon exist)
# ---------------------------
if 'latitude' in df_cleaned.columns and 'longitude' in df_cleaned.columns and not all_events_concat.empty:
    latlon = all_events_concat.dropna(subset=['latitude','longitude'])
    if not latlon.empty:
        st.subheader('Map: Extreme Event Locations')
        st.map(latlon[['latitude','longitude']])


# ---------------------------
# COUNTRY-COMPARISON: temperature trends
# ---------------------------
st.header('🌍 Country Comparison: Temperature Trends')
if 'country' in df_cleaned.columns and 'temperature_celsius' in df_cleaned.columns:
    countries = st.multiselect('Choose countries (max 8)', options=df_cleaned['country'].unique().tolist(), default=[df_cleaned['country'].unique().tolist()[0]] if len(df_cleaned)>0 else [])
    if countries:
        fig_cc, ax = plt.subplots(figsize=(12,6))
        for c in countries[:8]:
            cd = df_cleaned[df_cleaned['country']==c]
            if 'month' in cd.columns:
                monthly = cd.groupby('month')['temperature_celsius'].mean().reindex(range(1,13), fill_value=np.nan)
                ax.plot(monthly.index, monthly.values, marker='o', label=c)
        ax.set_xlabel('Month')
        ax.set_ylabel('Avg Temp (°C)')
        ax.set_title('Monthly Avg Temperature by Country')
        ax.legend()
        st.pyplot(fig_cc)
else:
    st.info('Country or temperature data not present for comparison.')


st.success('Dashboard loaded — use the sidebar to change data source or options.')