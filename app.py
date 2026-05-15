import streamlit as st
import pandas as pd
import os
from datetime import datetime

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(layout="wide")

# =====================================================
# DATA FOLDER
# =====================================================

DATA_FOLDER = "data"
os.makedirs(DATA_FOLDER, exist_ok=True)
data_folder = "weekly_report"
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
        st.image("logo.png", width=200)

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
# SIDEBAR (REMOVED LOGIN)
# =====================================================
st.sidebar.title("Navigation")

menu = st.sidebar.selectbox(
    "Menu",
    [
        "Dashboard",
        "Employee Management",
        "Clock In/Out",
        "Daily Upload",
        "Attendance Reports",
        "Leave Management",
        "HR Analytics"
    ]
)

# =====================================================
# MAIN TITLE
# =====================================================
st.title("HR Attendance System")

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

    st.subheader("Employee Management")

    st.subheader("Employee List")

    if st.session_state.employees:
        df = pd.DataFrame(st.session_state.employees)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No employees added yet")

# =====================================================
# CLOCK IN / OUT
# =====================================================
elif menu == "Clock In/Out":

    if not st.session_state.employees:
        st.warning("Add employees first")
        st.stop()

    names = [e["Name"] for e in st.session_state.employees]
    employee = st.selectbox("Employee", names)

    today = pd.Timestamp.now()

    if today.weekday() == 6:
        st.warning("Attendance only Monday - Saturday")
        st.stop()

    action = st.radio("Action", ["Clock In", "Clock Out"])

    if st.button("Submit Attendance"):

        date = str(today.date())
        time_now = today.strftime("%H:%M:%S")

        attendance = st.session_state.attendance
        df = pd.DataFrame(attendance)

        if action == "Clock In":

            if not df.empty:
                exists = df[(df["Name"] == employee) & (df["Date"] == date)]
                if not exists.empty:
                    st.error("Already clocked in")
                    st.stop()

            late = time_now > LATE_TIME

            new_record = {
                "Name": employee,
                "Date": date,
                "Time In": time_now,
                "Time Out": ""
            }

            attendance.append(new_record)
            save_daily_upload(pd.DataFrame([new_record]))

            if late:
                st.warning("Employee is late")
            else:
                st.success("Clock In recorded")

        else:

            updated = False

            for rec in attendance:
                if rec["Name"] == employee and rec["Date"] == date:
                    rec["Time Out"] = time_now
                    updated = True
                    save_daily_upload(pd.DataFrame([rec]))
                    break

            if updated:
                st.success("Clock Out recorded")
            else:
                st.error("No clock-in found")

# =====================================================
# DAILY UPLOAD
# =====================================================
elif menu == "Daily Upload":

    st.subheader("Upload Daily Attendance CSVs")

    uploaded_files = st.file_uploader(
        "Upload Attendance CSVs",
        type=["csv"],
        accept_multiple_files=True
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            try:
                df = pd.read_csv(uploaded_file)

                required_columns = ["Name", "Date", "Time In", "Time Out"]
                missing = [col for col in required_columns if col not in df.columns]

                if missing:
                    st.error(f"{uploaded_file.name} missing: {', '.join(missing)}")
                else:
                    save_daily_upload(df)
                    st.success(f"Uploaded: {uploaded_file.name}")

            except Exception as e:
                st.error(f"Error: {e}")

        st.session_state.attendance = load_all_attendance()

# =====================================================
# ATTENDANCE REPORTS
# =====================================================
elif menu == "Attendance Reports":

    if not st.session_state.attendance:
        st.info("No attendance records")
        st.stop()

    df = pd.DataFrame(st.session_state.attendance)

    st.subheader("Daily Attendance")
    st.dataframe(df, use_container_width=True)

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
