# =====================================================
# AST-EWIS : Interactive Dashboard
# File: app/dashboard.py
# Purpose: Visualize trends & early-warning signals
# =====================================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------------------------------
# Page Config
# -----------------------------------------------------
st.set_page_config(
    page_title="AST-EWIS Dashboard",
    layout="wide"
)

st.title("Aadhaar Societal Trends & Early-Warning Intelligence System (AST-EWIS)")
st.markdown(
    "This dashboard analyzes Aadhaar biometric update data to detect societal trends "
    "and generate early-warning signals for proactive governance."
)

# -----------------------------------------------------
# Load Data
# -----------------------------------------------------
state_df = pd.read_csv("../data/processed/monthly_bio_state.csv")
district_df = pd.read_csv("../data/processed/anomaly_scored_data.csv")
warnings_df = pd.read_csv("../data/processed/top_early_warnings.csv")

state_df['date'] = pd.to_datetime(state_df['date'])
district_df['date'] = pd.to_datetime(district_df['date'])
warnings_df['date'] = pd.to_datetime(warnings_df['date'])

# -----------------------------------------------------
# Sidebar Filters
# -----------------------------------------------------
st.sidebar.header("Filters")

states = sorted(state_df['state'].unique())
selected_state = st.sidebar.selectbox("Select State", states)

# -----------------------------------------------------
# KPI Section
# -----------------------------------------------------
st.subheader("Key Indicators")

col1, col2, col3 = st.columns(3)

total_updates = int(state_df['total_bio_updates'].sum())
total_warnings = int(warnings_df.shape[0])
latest_month = state_df['date'].max().strftime("%B %Y")

col1.metric("Total Biometric Updates", f"{total_updates:,}")
col2.metric("Early-Warning Events Detected", total_warnings)
col3.metric("Latest Data Month", latest_month)

# -----------------------------------------------------
# State Trend Visualization
# -----------------------------------------------------
st.subheader(f"Monthly Biometric Update Trend – {selected_state}")

state_trend = state_df[state_df['state'] == selected_state]

plt.figure()
plt.plot(state_trend['date'], state_trend['total_bio_updates'])
plt.xlabel("Date")
plt.ylabel("Biometric Updates")
plt.title(f"Trend for {selected_state}")
st.pyplot(plt)

# -----------------------------------------------------
# Early-Warning Signals Table
# -----------------------------------------------------
st.subheader("Top Early-Warning Signals")

st.dataframe(
    warnings_df.rename(columns={
        "total_bio_updates": "Observed Updates",
        "avg_updates": "Historical Average",
        "upper_threshold": "Warning Threshold",
        "severity_score": "Severity Score"
    }),
    use_container_width=True
)

# -----------------------------------------------------
# District-Level Warning Count (Selected State)
# -----------------------------------------------------
st.subheader(f"District-Level Warning Frequency – {selected_state}")

state_districts = district_df[
    (district_df['state'] == selected_state) &
    (district_df['early_warning'] == 1)
]

district_counts = (
    state_districts.groupby('district')
    .size()
    .sort_values(ascending=False)
    .head(10)
)

plt.figure()
district_counts.plot(kind='bar')
plt.xlabel("District")
plt.ylabel("Warning Count")
plt.title("Top Districts by Warning Frequency")
st.pyplot(plt)

# -----------------------------------------------------
# Interpretation Panel
# -----------------------------------------------------
st.subheader("How to Interpret These Signals")

st.markdown("""
- **Sudden spikes** in biometric updates may indicate population movement or migration.
- **Repeated warnings** in a district suggest sustained demographic or service-demand changes.
- **High severity scores** indicate abnormal deviations from historical behavior.
- Policymakers can use these insights for targeted interventions and resource planning.
""")

st.markdown("---")
st.markdown("**AST-EWIS | UIDAI Data Hackathon 2026**")
