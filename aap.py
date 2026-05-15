import streamlit as st
import pandas as pd
import numpy as np
import os
from pathlib import Path
from datetime import datetime, time
import plotly.express as px
import plotly.graph_objects as go

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="HR Attendance Tracker",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================================
# CREATE FOLDERS
# ==========================================================

Path("daily-attendance").mkdir(exist_ok=True)
Path("leave-management").mkdir(exist_ok=True)
Path("reports").mkdir(exist_ok=True)

employee_file = "employee.csv"

# ==========================================================
# CUSTOM STYLING
# ==========================================================

st.markdown("""
<style>

.stApp {
    background-color: white;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: black;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* Title */
.main-title {
    color: #ff6b00;
    font-size: 38px;
    font-weight: bold;
}

/* KPI Cards */
.metric-card {
    background-color: #ff6b00;
    padding: 20px;
    border-radius: 15px;
    color: white;
    text-align: center;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.2);
}

.metric-card h2 {
    color: white;
    font-size: 32px;
}

.metric-card p {
    color: white;
    font-size: 16px;
}

/* Buttons */
.stButton>button {
    background-color: #ff6b00;
    color: white;
    border-radius: 10px;
    border: none;
}

.stButton>button:hover {
    background-color: black;
    color: white;
}

/* Tables */
[data-testid="stDataFrame"] {
    border: 2px solid #ff6b00;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# ==========================================================
# SIDEBAR MENU
# ==========================================================

st.sidebar.title("Attendance System")

menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Employee Management",
        "Attendance Reports",
        "Leave Management",
        "HR Analytics"
    ]
)

# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def load_employees():
    return pd.read_csv(employee_file)


def save_employee(employee_id, staff_name, dept, position):

    df = load_employees()

    new_row = pd.DataFrame({
        "Employee ID": [employee_id],
        "Staff Name": [staff_name],
        "Department": [dept],
        "Position": [position]
    })

    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(employee_file, index=False)


def get_attendance_files():
    folder = "daily-attendance"

    files = [
        f for f in os.listdir(folder)
        if f.endswith(".csv")
    ]

    return files


def get_leave_files():
    folder = "leave-management"

    files = [
        f for f in os.listdir(folder)
        if f.endswith(".csv")
    ]

    return files


# ==========================================================
# DASHBOARD
# ==========================================================

if menu == "Dashboard":

    st.markdown(
        '<p class="main-title">Attendance Dashboard</p>',
        unsafe_allow_html=True
    )

    employees = load_employees()

    total_staff = len(employees)

    attendance_files = get_attendance_files()

    total_reports = len(attendance_files)

    leave_files = get_leave_files()

    total_leave_files = len(leave_files)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{total_staff}</h2>
            <p>Total Staff</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{total_reports}</h2>
            <p>Attendance Reports</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{total_leave_files}</h2>
            <p>Leave Records</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.subheader("📊 Employee Distribution")

    if len(employees) > 0:

        dept_count = (
            employees["Department"]
            .value_counts()
            .reset_index()
        )

        dept_count.columns = [
            "Department",
            "Count"
        ]

        fig = px.pie(
            dept_count,
            names="Department",
            values="Count",
            title="Employees by Department"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:
        st.info("No employee records found.")

# ==========================================================
# EMPLOYEE MANAGEMENT
# ==========================================================

elif menu == "Employee Management":

    st.markdown(
        '<p class="main-title">👨‍💼 Employee Management</p>',
        unsafe_allow_html=True
    )


    # ============================================
    # VIEW EMPLOYEES
    # ============================================

    with tab2:

        st.subheader(
            "Employee Master File"
        )

        employees = load_employees()

        st.dataframe(
            employees,
            use_container_width=True
        )

        st.download_button(
            label="⬇ Download Employee CSV",
            data=employees.to_csv(
                index=False
            ),
            file_name="employees.csv",
            mime="text/csv"
        )

# ==========================================================
# ATTENDANCE REPORTS
# ==========================================================

elif menu == "Attendance Reports":

    st.markdown(
        '<p class="main-title">🕒 Attendance Reports</p>',
        unsafe_allow_html=True
    )

    attendance_files = get_attendance_files()

    if len(attendance_files) == 0:
        st.warning(
            "No attendance files found in 'daily-attendance' folder."
        )

    else:

        selected_file = st.selectbox(
            "Select Daily Attendance CSV",
            attendance_files
        )

        file_path = os.path.join(
            "daily-attendance",
            selected_file
        )

        try:

            attendance_df = pd.read_csv(
                file_path
            )

            required_columns = [
                "Staff Name",
                "Clock In",
                "Clock Out"
            ]

            missing_cols = [
                col for col in required_columns
                if col not in attendance_df.columns
            ]

            if missing_cols:
                st.error(
                    f"Missing columns: {missing_cols}"
                )

            else:

                # ===================================
                # LOAD EMPLOYEE MASTER FILE
                # ===================================

                employee_df = load_employees()

                all_staff = set(
                    employee_df[
                        "Staff Name"
                    ].astype(str).str.strip()
                )

                attended_staff = set(
                    attendance_df[
                        "Staff Name"
                    ].astype(str).str.strip()
                )

                # ===================================
                # TIME CONVERSION
                # ===================================

                attendance_df["Clock In"] = pd.to_datetime(
                    attendance_df["Clock In"],
                    errors="coerce"
                )

                attendance_df["Clock Out"] = pd.to_datetime(
                    attendance_df["Clock Out"],
                    errors="coerce"
                )

                # ===================================
                # LATECOMERS (> 8:30AM)
                # ===================================

                late_time = time(8, 30)

                latecomers = attendance_df[
                    attendance_df[
                        "Clock In"
                    ].dt.time > late_time
                ]

                # ===================================
                # ABSENTEES
                # ===================================

                absentees_list = list(
                    all_staff - attended_staff
                )

                absentees = pd.DataFrame({
                    "Staff Name":
                    absentees_list
                })

                # ===================================
                # NIGHT SHIFT
                # (6PM till next day)
                # ===================================

                night_shift_time = time(18, 0)

                night_shift = attendance_df[
                    attendance_df[
                        "Clock In"
                    ].dt.time >= night_shift_time
                ]

                # ===================================
                # OVERTIMERS
                # (After 7PM)
                # ===================================

                overtime_time = time(19, 0)

                overtimers = attendance_df[
                    attendance_df[
                        "Clock Out"
                    ].dt.time > overtime_time
                ]

                # ===================================
                # KPI CARDS
                # ===================================

                st.subheader(
                    "📊 Daily Attendance Summary"
                )

                c1, c2, c3, c4 = st.columns(4)

                with c1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h2>{len(latecomers)}</h2>
                        <p>Latecomers</p>
                    </div>
                    """, unsafe_allow_html=True)

                with c2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h2>{len(absentees)}</h2>
                        <p>Absentees</p>
                    </div>
                    """, unsafe_allow_html=True)

                with c3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h2>{len(night_shift)}</h2>
                        <p>Night Shift</p>
                    </div>
                    """, unsafe_allow_html=True)

                with c4:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h2>{len(overtimers)}</h2>
                        <p>Overtimers</p>
                    </div>
                    """, unsafe_allow_html=True)

                st.divider()

                # ===================================
                # REPORT TABLES
                # ===================================

                tab1, tab2, tab3, tab4 = st.tabs([
                    "Latecomers",
                    "Absentees",
                    "Night Shift",
                    "Overtimers"
                ])

                # ----------------------------
                # LATECOMERS
                # ----------------------------

                with tab1:

                    st.subheader(
                        "⏰ Latecomers"
                    )

                    st.dataframe(
                        latecomers,
                        use_container_width=True
                    )

                    st.download_button(
                        "Download Latecomers",
                        latecomers.to_csv(
                            index=False
                        ),
                        file_name=
                        "latecomers.csv",
                        mime="text/csv"
                    )

                # ----------------------------
                # ABSENTEES
                # ----------------------------

                with tab2:

                    st.subheader(
                        "❌ Absentees"
                    )

                    st.dataframe(
                        absentees,
                        use_container_width=True
                    )

                    st.download_button(
                        "Download Absentees",
                        absentees.to_csv(
                            index=False
                        ),
                        file_name=
                        "absentees.csv",
                        mime="text/csv"
                    )

                # ----------------------------
                # NIGHT SHIFT
                # ----------------------------

                with tab3:

                    st.subheader(
                        "🌙 Night Shift"
                    )

                    st.dataframe(
                        night_shift,
                        use_container_width=True
                    )

                    st.download_button(
                        "Download Night Shift",
                        night_shift.to_csv(
                            index=False
                        ),
                        file_name=
                        "night_shift.csv",
                        mime="text/csv"
                    )

                # ----------------------------
                # OVERTIMERS
                # ----------------------------

                with tab4:

                    st.subheader(
                        "🕖 Overtimers"
                    )

                    st.dataframe(
                        overtimers,
                        use_container_width=True
                    )

                    st.download_button(
                        "Download Overtimers",
                        overtimers.to_csv(
                            index=False
                        ),
                        file_name=
                        "overtimers.csv",
                        mime="text/csv"
                    )

                st.divider()

                # ===================================
                # CHARTS
                # ===================================

                st.subheader(
                    "📈 Attendance Insights"
                )

                summary_df = pd.DataFrame({
                    "Category": [
                        "Latecomers",
                        "Absentees",
                        "Night Shift",
                        "Overtimers"
                    ],
                    "Count": [
                        len(latecomers),
                        len(absentees),
                        len(night_shift),
                        len(overtimers)
                    ]
                })

                col1, col2 = st.columns(2)

                with col1:

                    fig_bar = px.bar(
                        summary_df,
                        x="Category",
                        y="Count",
                        title=
                        "Attendance Summary"
                    )

                    st.plotly_chart(
                        fig_bar,
                        use_container_width=True
                    )

                with col2:

                    fig_pie = px.pie(
                        summary_df,
                        names="Category",
                        values="Count",
                        title=
                        "Attendance Distribution"
                    )

                    st.plotly_chart(
                        fig_pie,
                        use_container_width=True
                    )

        except Exception as e:
            st.error(
                f"Error loading file: {e}"
            )

# ==========================================================
# LEAVE MANAGEMENT
# ==========================================================

elif menu == "Leave Management":

    st.markdown(
        '<p class="main-title">📅 Leave Management</p>',
        unsafe_allow_html=True
    )

    leave_files = get_leave_files()

    if len(leave_files) == 0:
        st.warning("No leave records found in 'leave-management' folder.")

    else:

        selected_leave = st.selectbox(
            "Select Leave CSV",
            leave_files
        )

        leave_path = os.path.join(
            "leave-management",
            selected_leave
        )

        try:

            leave_df = pd.read_csv(leave_path)

            st.subheader("📄 Leave Records")

            st.dataframe(
                leave_df,
                use_container_width=True
            )

            st.download_button(
                "Download Leave Report",
                leave_df.to_csv(index=False),
                file_name="leave_report.csv",
                mime="text/csv"
            )

            st.divider()

            st.subheader("📊 Leave Breakdown")

            if "Leave Type" in leave_df.columns:

                leave_summary = leave_df["Leave Type"].value_counts().reset_index()
                leave_summary.columns = ["Leave Type", "Count"]

                fig = px.pie(
                    leave_summary,
                    names="Leave Type",
                    values="Count",
                    title="Leave Distribution"
                )

                st.plotly_chart(fig, use_container_width=True)

            else:
                st.info("Add 'Leave Type' column for analytics.")

        except Exception as e:
            st.error(f"Error loading leave file: {e}")


# ==========================================================
# HR ANALYTICS
# ==========================================================

elif menu == "HR Analytics":

    st.markdown(
        '<p class="main-title">📊 HR Analytics</p>',
        unsafe_allow_html=True
    )

    employees = load_employees()

    if len(employees) == 0:
        st.warning("No employee data available.")

    else:

        st.subheader("👨‍💼 Workforce Overview")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Staff", len(employees))
        col2.metric("Departments", employees["Department"].nunique())
        col3.metric("Positions", employees["Position"].nunique())

        st.divider()

        # ==========================================
        # DEPARTMENT ANALYSIS
        # ==========================================

        st.subheader("🏢 Department Distribution")

        dept_df = employees["Department"].value_counts().reset_index()
        dept_df.columns = ["Department", "Count"]

        fig1 = px.bar(
            dept_df,
            x="Department",
            y="Count",
            title="Employees per Department"
        )

        st.plotly_chart(fig1, use_container_width=True)

        # ==========================================
        # POSITION ANALYSIS
        # ==========================================

        st.subheader("👔 Position Breakdown")

        pos_df = employees["Position"].value_counts().reset_index()
        pos_df.columns = ["Position", "Count"]

        fig2 = px.pie(
            pos_df,
            names="Position",
            values="Count",
            title="Employee Positions"
        )

        st.plotly_chart(fig2, use_container_width=True)

        # ==========================================
        # SAMPLE PERFORMANCE METRICS (SIMULATED)
        # ==========================================

        st.subheader("📈 HR Performance Insights")

        performance_df = pd.DataFrame({
            "Metric": [
                "Attendance Rate",
                "Punctuality",
                "Overtime Rate",
                "Leave Utilization"
            ],
            "Score": [
                np.random.randint(70, 100),
                np.random.randint(60, 100),
                np.random.randint(40, 90),
                np.random.randint(50, 95)
            ]
        })

        fig3 = px.bar(
            performance_df,
            x="Metric",
            y="Score",
            title="HR Performance Indicators",
            text="Score"
        )

        st.plotly_chart(fig3, use_container_width=True)

        # ==========================================
        # ATTENDANCE HEALTH SCORE
        # ==========================================

        st.subheader("❤️ Attendance Health Overview")

        health_score = np.random.randint(65, 98)

        st.progress(health_score / 100)

        st.write(f"Overall Attendance Health Score: **{health_score}%**")

        if health_score > 85:
            st.success("Excellent workforce attendance performance!")
        elif health_score > 70:
            st.info("Good attendance, but room for improvement.")
        else:
            st.warning("Attendance needs attention.")
