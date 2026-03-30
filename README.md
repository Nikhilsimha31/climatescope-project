# 🌍 ClimateScope — Climate Intelligence Dashboard

ClimateScope is an interactive data visualization dashboard designed to analyze global climate conditions including temperature, humidity, air quality, and extreme weather events.

The dashboard allows users to explore climate data through dynamic visualizations, geographic maps, and analytical tools. It helps identify environmental trends, compare countries, and understand extreme climate patterns.

This project was developed as part of the **Infosys Internship Climate Analytics Project**.

---

# 🚀 Project Overview

ClimateScope provides a centralized platform to analyze environmental and climate-related datasets.  

The dashboard processes climate data and converts it into meaningful insights using interactive charts and visual analytics.

Users can explore:

- Weather conditions
- Air quality trends
- Climate correlations
- Country comparisons
- Extreme weather events
- Global climate patterns

The interface allows filtering by **country and date range**, enabling deeper analysis of environmental changes.

---

# 🧠 Key Features

### 🌡️ Weather Overview
Visualize temperature distribution and relationships between temperature and humidity.

### 🌬️ Air Quality Analysis
Compare air quality indicators across different countries using grouped bar charts.

### 📊 Correlation Analysis
Heatmaps reveal relationships between climate variables such as temperature, humidity, and air pollution.

### 🗺️ Geographic Climate Map
Global maps visualize environmental metrics geographically using latitude and longitude data.

### 📈 Global Climate Trends
Track climate variables over time with trend lines and moving averages.

### 🌎 Country Comparison
Compare climate indicators across multiple countries.

### 🏆 Climate Rankings
Rank countries based on environmental metrics such as temperature, humidity, or pollution levels.

### 🌺 Flower Growth Advisor
Suggests optimal growing conditions for different flowers based on the current climate conditions in selected countries.

### 🌪️ Extreme Events Analysis
Detect and visualize extreme environmental events such as:

- High temperature
- Poor air quality
- Low humidity
- Heavy precipitation
- Strong winds

These events can be analyzed by **month or year**.

---

# 📂 Project Structure

```
Infosys_Internship_2025_ClimateScope/
│
├── climatescope_app.py
├── climatescope_app3.py
├── df_clean.csv
├── Climate_scope.ipynb
└── README.md
```

**climatescope_app3.py**  
Main Streamlit application containing the dashboard logic and visualizations.

**df_clean.csv**  
Cleaned dataset containing climate variables such as temperature, humidity, air quality, and geographic coordinates.

**Climate_scope.ipynb**  
Notebook used for dataset exploration and preprocessing.

---

# ⚙️ Technologies Used

### Programming Language
Python

### Data Processing
- Pandas
- NumPy

### Visualization
- Plotly
- Matplotlib
- Seaborn

### Web Dashboard Framework
Streamlit

### Data Source
Processed climate dataset stored as **df_clean.csv**

---

# 🖥️ How to Run the Project

### 1️⃣ Install Required Libraries

```bash
pip install streamlit pandas numpy plotly matplotlib seaborn
```

---

### 2️⃣ Navigate to Project Folder

```bash
cd Infosys_Internship_2025_ClimateScope
```

---

### 3️⃣ Run the Streamlit Dashboard

```bash
streamlit run climatescope_app3.py
```

---

### 4️⃣ Open in Browser

After running the command, Streamlit will generate a local URL:

```
http://localhost:8501
```

Open this link in your browser to access the dashboard.

---

# 📊 Dataset Requirements

The dashboard expects a CSV file containing climate data with columns such as:

- country
- temperature_celsius
- humidity
- air_quality_PM2.5
- latitude
- longitude
- last_updated
- precipitation_mm
- wind_speed_kmh

The dataset is loaded using the **sidebar file uploader**.

---

# 🎯 Applications

ClimateScope can be useful for:

- Climate trend analysis
- Environmental research
- Weather pattern monitoring
- Climate data visualization
- Educational climate analytics

---

# ⚠️ Disclaimer

This project is intended for **educational and analytical purposes**.

The predictions and insights generated are based solely on the provided dataset and should not be used for official meteorological forecasting.

---

# 👨‍💻 Author

Developed by **Nikhil Simha**

Infosys Internship — Climate Analytics Project
