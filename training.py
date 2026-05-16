import streamlit as st
import pandas as pd
import os
from datetime import datetime
from pathlib import Path

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Training Management System",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📘 TRAINING MANAGEMENT SYSTEM")

# =====================================================
# FOLDERS & FILES
# =====================================================
base_folder = "training-data"
Path(base_folder).mkdir(exist_ok=True)
Path(f"{base_folder}/materials").mkdir(exist_ok=True)

sessions_file = f"{base_folder}/sessions.csv"
attendance_file = f"{base_folder}/attendance.csv"
employees_file = "employees.csv"

# =====================================================
# INIT FILES
# =====================================================
if not os.path.exists(sessions_file):
    pd.DataFrame(columns=[
        "Training ID", "Title", "Department", "Trainer",
        "Date", "Time", "Description"
    ]).to_csv(sessions_file, index=False)

if not os.path.exists(attendance_file):
    pd.DataFrame(columns=[
        "Training ID", "Employee Name", "Status", "Score", "Date"
    ]).to_csv(attendance_file, index=False)

sessions_df = pd.read_csv(sessions_file)
attendance_df = pd.read_csv(attendance_file)

# =====================================================
# SIDEBAR MENU
# =====================================================
menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Create Training",
        "View Trainings",
        "Mark Attendance",
        "Training Reports"
    ]
)

# =====================================================
# DASHBOARD
# =====================================================
if menu == "Dashboard":

    st.subheader("📊 Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Trainings", len(sessions_df))
    col2.metric("Attendance Records", len(attendance_df))

    if not attendance_df.empty:
        avg_score = attendance_df["Score"].mean()
    else:
        avg_score = 0

    col3.metric("Avg Training Score", round(avg_score, 2))

    st.info("Use the sidebar to manage training sessions, attendance, and reports.")

# =====================================================
# CREATE TRAINING
# =====================================================
elif menu == "Create Training":

    st.subheader("➕ Create Training Session")

    with st.form("create_training"):

        title = st.text_input("Training Title")
        dept = st.text_input("Department")
        trainer = st.text_input("Trainer Name")
        date = st.date_input("Date")
        time = st.time_input("Time")
        desc = st.text_area("Description")

        submit = st.form_submit_button("Create Training")

        if submit:

            new_id = len(sessions_df) + 1

            new_data = {
                "Training ID": new_id,
                "Title": title,
                "Department": dept,
                "Trainer": trainer,
                "Date": str(date),
                "Time": str(time),
                "Description": desc
            }

            sessions_df = pd.concat([sessions_df, pd.DataFrame([new_data])], ignore_index=True)
            sessions_df.to_csv(sessions_file, index=False)

            st.success(f"Training '{title}' created successfully!")

# =====================================================
# VIEW TRAININGS
# =====================================================
elif menu == "View Trainings":

    st.subheader("📚 All Trainings")

    st.dataframe(sessions_df, use_container_width=True)

# =====================================================
# MARK ATTENDANCE
# =====================================================
elif menu == "Mark Attendance":

    st.subheader("🧾 Mark Training Attendance")

    if sessions_df.empty:
        st.warning("No training sessions available.")
    else:

        training_id = st.selectbox("Select Training ID", sessions_df["Training ID"])

        if os.path.exists(employees_file):
            employees_df = pd.read_csv(employees_file)
            employees = employees_df.iloc[:, 0].tolist()
        else:
            employees = []

        if employees:

            emp = st.selectbox("Employee", employees)
            status = st.selectbox("Status", ["Present", "Absent", "Late"])
            score = st.number_input("Score (0-100)", 0, 100)

            if st.button("Save Attendance"):

                new_record = {
                    "Training ID": training_id,
                    "Employee Name": emp,
                    "Status": status,
                    "Score": score,
                    "Date": str(datetime.now().date())
                }

                attendance_df = pd.concat([attendance_df, pd.DataFrame([new_record])], ignore_index=True)
                attendance_df.to_csv(attendance_file, index=False)

                st.success("Attendance saved successfully!")

        else:
            st.error("No employees found. Please upload employees.csv first.")

# =====================================================
# REPORTS
# =====================================================
elif menu == "Training Reports":

    st.subheader("📊 Training Analytics")

    if attendance_df.empty:
        st.warning("No attendance data yet.")
    else:

        report = attendance_df.groupby("Employee Name").agg({
            "Score": "mean",
            "Status": lambda x: (x == "Present").sum()
        }).reset_index()

        report.columns = ["Employee Name", "Average Score", "Attendance Count"]

        st.dataframe(report, use_container_width=True)

        st.bar_chart(report.set_index("Employee Name")["Average Score"])
