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

st.sidebar.title("Navigation")

menu = st.sidebar.selectbox(
    "Menu",
    [
        "Dashboard",
        "Employee Management",
        "Attendance Reports",
        "Leave Management",
        "HR Analytics"
    ]
)
# =====================================================
# MAIN TITLE
# =====================================================
st.title("Attendance System")

# =====================================================
# DASHBOARD
# =====================================================
if menu == "Dashboard":

    st.subheader("Dashboard")

    c1, c2 = st.columns(2)

    c1.metric("Employees", len(st.session_state.employees))
    c2.metric("Attendance Records", len(st.session_state.attendance))
LATE_TIME = "08:30:00"
OVERTIME_TIME = "18:00:00"
