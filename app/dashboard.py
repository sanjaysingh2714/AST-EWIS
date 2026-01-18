# =====================================================
# AST-EWIS : Interactive Dashboard
# =====================================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# -----------------------------------------------------
# Resolve paths
# -----------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "processed")

STATE_PATH = os.path.join(DATA_DIR, "monthly_bio_state.csv")
DISTRICT_PATH = os.path.join(DATA_DIR, "anomaly_scored_data.csv")
WARNING_PATH = os.path.join(DATA_DIR, "top_early_warnings.csv")

# -----------------------------------------------------
# Page config
# -----------------------------------------------------
st.set_page_config(page_title="AST-EWIS Dashboard", layout="wide")

# -----------------------------------------------------
# Custom Styling (Theme)
# -----------------------------------------------------
st.markdown("""
<style>
body { background-color: #f9fbfd; }

.card {
    background-color: white;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #e6eef9;
    box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    margin-bottom: 10px;
}

.metric {
    text-align: center;
    font-size: 22px;
}

.small {
    color: #6c757d;
    font-size: 14px;
}

.sidebar .sidebar-content {
    background-color: #f3f7ff;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------
# Title
# -----------------------------------------------------
st.title("📊 Aadhaar Societal Trends & Early-Warning Intelligence System (AST-EWIS)")
st.markdown("A data-driven dashboard to identify societal trends and early-warning signals using Aadhaar biometric update data.")

# -----------------------------------------------------
# Load Data
# -----------------------------------------------------
if not (os.path.exists(STATE_PATH) and os.path.exists(DISTRICT_PATH) and os.path.exists(WARNING_PATH)):
    st.error("Processed data files not found. Please run notebooks first.")
    st.stop()

state_df = pd.read_csv(STATE_PATH)
district_df = pd.read_csv(DISTRICT_PATH)
warnings_df = pd.read_csv(WARNING_PATH)

state_df['date'] = pd.to_datetime(state_df['date'])
district_df['date'] = pd.to_datetime(district_df['date'])
warnings_df['date'] = pd.to_datetime(warnings_df['date'])

# -----------------------------------------------------
# Sidebar
# -----------------------------------------------------
st.sidebar.title("Filters")
states = sorted(state_df['state'].unique())
selected_state = st.sidebar.selectbox("Select State", states)

# -----------------------------------------------------
# KPI Cards
# -----------------------------------------------------
total_updates = int(state_df['total_bio_updates'].sum())
total_warnings = int(warnings_df.shape[0])
latest_month = state_df['date'].max().strftime("%B %Y")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"<div class='card metric'>📊 {total_updates:,}<div class='small'>Total Updates</div></div>", unsafe_allow_html=True)

with col2:
    st.markdown(f"<div class='card metric'>🚨 {total_warnings}<div class='small'>Warnings Detected</div></div>", unsafe_allow_html=True)

with col3:
    st.markdown(f"<div class='card metric'>📅 {latest_month}<div class='small'>Latest Month</div></div>", unsafe_allow_html=True)

# -----------------------------------------------------
# Trend Chart
# -----------------------------------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader(f"📈 Monthly Trend – {selected_state}")

state_trend = state_df[state_df['state'] == selected_state]

plt.figure(figsize=(11, 4))
plt.plot(state_trend['date'], state_trend['total_bio_updates'], marker='o')
plt.xticks(rotation=90)
plt.grid(True, linestyle="--", alpha=0.4)
plt.xlabel("Date")
plt.ylabel("Updates")
plt.title("Biometric Updates Over Time")
st.pyplot(plt)

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------
# Warning Table
# -----------------------------------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("🚨 Top Early-Warning Signals")

st.dataframe(
    warnings_df.rename(columns={
        "total_bio_updates": "Observed",
        "avg_updates": "Average",
        "upper_threshold": "Threshold",
        "severity_score": "Severity"
    }),
    use_container_width=True
)

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------
# District Severity Chart
# -----------------------------------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader(f"📍 District Risk Levels – {selected_state}")

state_districts = district_df[
    (district_df['state'] == selected_state) &
    (district_df['early_warning'] == 1)
]

district_severity = (
    state_districts.groupby('district')['severity_score']
    .mean()
    .sort_values(ascending=False)
    .head(10)
)

if district_severity.empty:
    st.info("No warning districts for this state.")
else:
    values = district_severity.values
    colors = []

    for v in values:
        if v < 2:
            colors.append("#2ecc71")   # Green
        elif 2 <= v <= 2.5:
            colors.append("#f39c12")   # Orange
        else:
            colors.append("#e74c3c")   # Red

    plt.figure(figsize=(11, 4))
    district_severity.plot(kind='bar', color=colors, edgecolor="black")
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Severity Score")
    plt.title("Risk Level by District")
    plt.grid(axis="y", linestyle="--", alpha=0.4)

    for i, v in enumerate(values):
        plt.text(i, v + 0.02, f"{v:.2f}", ha='center', fontsize=9)

    st.pyplot(plt)

    st.markdown("""
    **Risk Levels**  
    🟢 Low (< 2)  
    🟠 Medium (2 – 2.5)  
    🔴 High (> 2.5)
    """)

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------
# Interpretation
# -----------------------------------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("🧠 How to Interpret This Dashboard")

st.markdown("""
- Spikes indicate abnormal Aadhaar activity patterns  
- Higher severity means stronger deviation from normal behavior  
- Red districts should be prioritized for attention  
- Policymakers can use this for proactive intervention  
""")

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("— AST-EWIS | UIDAI Data Hackathon 2026")