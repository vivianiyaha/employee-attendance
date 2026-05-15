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

# =====================================================
# DATA FOLDER
# =====================================================

DATA_FOLDER = "performance_data"
os.makedirs(DATA_FOLDER, exist_ok=True)

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

# =====================================================
# LOAD DATA
# =====================================================
def load_data(file):
    if os.path.exists(file):
        return pd.read_csv(file).to_dict("records")
    return []

# =====================================================
# SAVE DATA
# =====================================================
def save_data(data, file):
    pd.DataFrame(data).to_csv(file, index=False)

# =====================================================
# SAVE DAILY ATTENDANCE FILE
# =====================================================
def save_daily_upload(df):
    os.makedirs(DATA_FOLDER, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"attendance_{timestamp}.csv"
    path = os.path.join(DATA_FOLDER, filename)

    df.to_csv(path, index=False)
    return path

# =====================================================
# LOAD ALL ATTENDANCE FILES
# =====================================================
def load_all_attendance():
    files = [f for f in os.listdir(DATA_FOLDER) if f.startswith("attendance_")]
    all_data = []

    for file in files:
        path = os.path.join(DATA_FOLDER, file)
        try:
            df = pd.read_csv(path)
            all_data.append(df)
        except:
            pass

    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        combined = combined.drop_duplicates()
        return combined.to_dict("records")

    return []

# =====================================================
# SESSION STATE DATA
# =====================================================
if "employees" not in st.session_state:
    st.session_state.employees = load_data(EMP_FILE)

st.session_state.attendance = load_all_attendance()

if "leaves" not in st.session_state:
    st.session_state.leaves = load_data(LEV_FILE)


# =====================================================
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

# =====================================================
# EMPLOYEE MANAGEMENT
# =====================================================
elif menu == "Employee Management":

    st.subheader("Employee List")

    if st.session_state.employees:
        df = pd.DataFrame(st.session_state.employees)
        df.index = range(1, len(df) + 1)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No employees added yet")


# =====================================================
# ATTENDANCE REPORTS
# =====================================================
elif menu == "Attendance Reports":

    st.subheader("Daily Attendance")

    attendance_folder = "daily-attendance"

    if os.path.exists(attendance_folder):

        csv_files = [f for f in os.listdir(attendance_folder) if f.endswith(".csv")]

        if len(csv_files) > 0:

            selected_file = st.selectbox("Select Attendance File", csv_files)

            file_path = os.path.join(attendance_folder, selected_file)

            df = pd.read_csv(file_path)

            df.index = range(1, len(df) + 1)

            st.success(f"Showing: {selected_file}")
            st.dataframe(df, use_container_width=True)

        else:
            st.warning("No CSV files in daily-attendance folder")

    else:
        st.error("Folder 'daily-attendance' not found")
# =====================================================
# LEAVE MANAGEMENT
# =====================================================
elif menu == "Leave Management":
    st.subheader("Leave Management")
    st.write("Leave system coming soon")

# =====================================================
# HR ANALYTICS
# =====================================================
elif menu == "HR Analytics":

    st.subheader("HR Analytics")

    if st.session_state.attendance:
        df = pd.DataFrame(st.session_state.attendance)
        st.dataframe(df.describe(include="all"))
    else:
        st.info("No attendance data available")
