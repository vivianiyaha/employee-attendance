import streamlit as st
import pandas as pd
import numpy as np
import os
from pathlib import Path
from datetime import datetime, time
import plotly.express as px

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="HR Attendance Tracker",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================================
# FOLDERS
# ==========================================================

Path("daily-attendance").mkdir(exist_ok=True)
Path("leave-management").mkdir(exist_ok=True)

employee_file = "employee.csv"

# ==========================================================
# INIT EMPLOYEE FILE (ONLY NAME COLUMN)
# ==========================================================

if not os.path.exists(employee_file):
    pd.DataFrame({"Name": []}).to_csv(employee_file, index=False)

# ==========================================================
# STYLING
# ==========================================================

st.markdown("""
<style>
.stApp { background-color: white; }

section[data-testid="stSidebar"] {
    background-color: black;
}
section[data-testid="stSidebar"] * {
    color: white !important;
}

.main-title {
    color: #ff6b00;
    font-size: 36px;
    font-weight: bold;
}

.metric-card {
    background-color: #ff6b00;
    padding: 18px;
    border-radius: 12px;
    color: white;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.title("HR SYSTEM")

menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Employee Management", "Attendance Reports", "Leave Management", "HR Analytics"]
)

# ==========================================================
# HELPERS (FIXED FOR YOUR DATA STRUCTURE)
# ==========================================================

def load_employees():
    df = pd.read_csv(employee_file)
    df.columns = df.columns.str.strip()
    return df


def save_employee(name):
    df = load_employees()
    new = pd.DataFrame({"Name": [name]})
    df = pd.concat([df, new], ignore_index=True)
    df.to_csv(employee_file, index=False)


def get_attendance_files():
    return [f for f in os.listdir("daily-attendance") if f.endswith(".csv")]


def get_leave_files():
    return [f for f in os.listdir("leave-management") if f.endswith(".csv")]

# ==========================================================
# DASHBOARD
# ==========================================================

if menu == "Dashboard":

    st.markdown('<div class="main-title">HR DASHBOARD</div>', unsafe_allow_html=True)

    employees = load_employees()
    attendance_files = get_attendance_files()
    leave_files = get_leave_files()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{len(employees)}</h2>
            <p>Total Staff</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{len(attendance_files)}</h2>
            <p>Attendance Files</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{len(leave_files)}</h2>
            <p>Leave Files</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.subheader("Employee List")
    st.dataframe(employees, use_container_width=True)


# ==========================================================
# EMPLOYEE MANAGEMENT
# ==========================================================

elif menu == "Employee Management":

    st.markdown('<div class="main-title">EMPLOYEE MANAGEMENT</div>', unsafe_allow_html=True)

    name = st.text_input("Enter Employee Name")

    if st.button("Add Employee"):
        if name:
            save_employee(name)
            st.success("Employee added")
        else:
            st.warning("Enter name")

    st.subheader("All Employees")
    st.dataframe(load_employees(), use_container_width=True)

# ==========================================================
# ATTENDANCE REPORTS
# ==========================================================

elif menu == "Attendance Reports":

    st.markdown('<div class="main-title">ATTENDANCE REPORTS</div>', unsafe_allow_html=True)

    files = get_attendance_files()

    if not files:
        st.warning("No attendance files found")
    else:

        file = st.selectbox("Select File", files)
        df = pd.read_csv(os.path.join("daily-attendance", file))

        df.columns = df.columns.str.strip()

        # Convert time
        df["Time in"] = pd.to_datetime(df["Time in"], errors="coerce")
        df["Time Out"] = pd.to_datetime(df["Time Out"], errors="coerce")

        # RULES
        late = df[df["Time in"].dt.time > time(8, 30)]
        overtime = df[df["Time Out"].dt.time > time(19, 0)]

        employees = set(load_employees()["Name"])
        attended = set(df["Name"])

        absentees = pd.DataFrame({
            "Name": list(employees - attended)
        })

        st.subheader("Summary")

        c1, c2, c3 = st.columns(3)

        c1.metric("Late", len(late))
        c2.metric("Absent", len(absentees))
        c3.metric("Overtime", len(overtime))

        st.subheader("Latecomers")
        st.dataframe(late)

        st.subheader("Absentees")
        st.dataframe(absentees)

        st.subheader("Overtime")
        st.dataframe(overtime)


# ==========================================================
# LEAVE MANAGEMENT
# ==========================================================

elif menu == "Leave Management":

    st.markdown('<div class="main-title">LEAVE MANAGEMENT</div>', unsafe_allow_html=True)

    files = get_leave_files()

    if files:
        file = st.selectbox("Select Leave File", files)
        df = pd.read_csv(os.path.join("leave-management", file))
        st.dataframe(df)
    else:
        st.warning("No leave data")


# ==========================================================
# HR ANALYTICS
# ==========================================================

elif menu == "HR Analytics":

    st.markdown('<div class="main-title">HR ANALYTICS</div>', unsafe_allow_html=True)

    employees = load_employees()

    st.metric("Total Staff", len(employees))

    fig = px.bar(employees["Name"].value_counts().reset_index(),
                 x="index", y="Name",
                 title="Employee Count")

    st.plotly_chart(fig, use_container_width=True)
