import streamlit as st
import pandas as pd
import os
from datetime import datetime
from pathlib import Path

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed"
)
data_folder = "daily-attendance"
Path(data_folder).mkdir(exist_ok=True)


# =====================================================
# STYLING
# =====================================================
st.markdown("""
    <style>
    .stApp {
        background-color: white;
    }

    h1, h2, h3 {
        color: black;
    }

    .metric-box {
        background-color: #f5f5f5;
        padding: 15px;
        border-radius: 10px;
        border-left: 6px solid orange;
    }
    </style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================
col1, col2 = st.columns([1, 6])

with col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=400)

# =====================================================
# SETTINGS
# =====================================================
EMP_FILE = "employee.csv"
LEV_FILE = "leaves.csv"

LATE_TIME = "08:30:00"
OVERTIME_TIME = "18:00:00"
