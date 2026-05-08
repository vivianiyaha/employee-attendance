import streamlit as st
import pandas as pd
import os
from datetime import datetime

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="HR Attendance System",
    layout="wide"
)

# =====================================================
# DATA FOLDER
# =====================================================
DATA_FOLDER = "data"
os.makedirs(DATA_FOLDER, exist_ok=True)

# =====================================================
# FILES
# =====================================================
EMP_FILE = "employee.csv"
LEV_FILE = "leaves.csv"

# =====================================================
# SETTINGS
# =====================================================
LATE_TIME = "08:30:00"
OVERTIME_TIME = "18:00:00"

# =====================================================
# LOGIN USERS
# =====================================================
USERS = {
    "admin": "admin123",
    "hr": "hr123"
}

# =====================================================
# CUSTOM CSS
# =====================================================
st.markdown("""
<style>

.stApp {
    background-color: white;
}

h1, h2, h3 {
    color: black;
}

[data-testid="stSidebar"] {
    background-color: #f5f5f5;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================
col1, col2 = st.columns([1, 5])

with col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=180)

with col2:
    st.title("HR Attendance System")

# =====================================================
# SESSION STATE
# =====================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# =====================================================
# LOAD DATA
# =====================================================
def load_data(file):

    if os.path.exists(file):

        try:
            df = pd.read_csv(file)

            # Remove spaces from columns
            df.columns = df.columns.str.strip()

            # Remove empty rows
            df = df.dropna(how="all")

            return df.to_dict("records")

        except Exception as e:
            st.error(f"Error loading {file}: {e}")

    return []

# =====================================================
# SAVE DATA
# =====================================================
def save_data(data, file):

    try:
        pd.DataFrame(data).to_csv(file, index=False)

    except Exception as e:
        st.error(f"Error saving {file}: {e}")

# =====================================================
# SAVE DAILY ATTENDANCE
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

    files = [
        f for f in os.listdir(DATA_FOLDER)
        if f.startswith("attendance_")
    ]

    all_data = []

    for file in files:

        path = os.path.join(DATA_FOLDER, file)

        try:
            df = pd.read_csv(path)

            df.columns = df.columns.str.strip()

            all_data.append(df)

        except:
            pass

    if all_data:

        combined = pd.concat(all_data, ignore_index=True)

        combined = combined.drop_duplicates()

        return combined.to_dict("records")

    return []

# =====================================================
# LOGIN FUNCTION
# =====================================================
def login():

    st.title("🔐 HR Login")

    username = st.text_input("Username").strip()

    password = st.text_input(
        "Password",
        type="password"
    ).strip()

    if st.button("Login"):

        if username in USERS and USERS[username] == password:

            st.session_state.logged_in = True
            st.session_state.username = username

            st.rerun()

        else:
            st.error("Invalid login credentials")

# =====================================================
# LOGOUT FUNCTION
# =====================================================
def logout():

    st.session_state.logged_in = False
    st.session_state.username = ""

    st.rerun()

# =====================================================
# LOGIN CHECK
# =====================================================
if not st.session_state.logged_in:
    login()
    st.stop()

# =====================================================
# LOAD SESSION DATA
# =====================================================
if "employees" not in st.session_state:
    st.session_state.employees = load_data(EMP_FILE)

if "leaves" not in st.session_state:
    st.session_state.leaves = load_data(LEV_FILE)

st.session_state.attendance = load_all_attendance()

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.success(
    f"👤 {st.session_state.username}"
)

if st.sidebar.button("Logout"):
    logout()

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
# DASHBOARD
# =====================================================
if menu == "Dashboard":

    st.subheader("Dashboard")

    c1, c2 = st.columns(2)

    c1.metric(
        "Employees",
        len(st.session_state.employees)
    )

    c2.metric(
        "Attendance Records",
        len(st.session_state.attendance)
    )

# =====================================================
# EMPLOYEE MANAGEMENT
# =====================================================
elif menu == "Employee Management":

    st.subheader("Employee Management")

    # =============================================
    # ADD EMPLOYEE
    # =============================================
    with st.form("employee_form"):

        name = st.text_input("Employee Name")

        submit = st.form_submit_button(
            "Add Employee"
        )

        if submit:

            if name.strip() == "":

                st.error("Employee name required")

            else:

                # Check duplicates
                existing_names = [
                    e.get("Name", "").lower()
                    for e in st.session_state.employees
                ]

                if name.lower() in existing_names:

                    st.warning("Employee already exists")

                else:

                    new_employee = {
                        "Name": name.strip()
                    }

                    st.session_state.employees.append(
                        new_employee
                    )

                    save_data(
                        st.session_state.employees,
                        EMP_FILE
                    )

                    st.success(
                        "Employee added successfully"
                    )

                    st.rerun()

    st.divider()

    # =============================================
    # EMPLOYEE LIST
    # =============================================
    st.subheader("Employee List")

    if st.session_state.employees:

        df_emp = pd.DataFrame(
            st.session_state.employees
        )

        st.dataframe(
            df_emp,
            use_container_width=True
        )

    else:
        st.info("No employees found")

# =====================================================
# CLOCK IN / OUT
# =====================================================
elif menu == "Clock In/Out":

    st.subheader("Clock In / Clock Out")

    if not st.session_state.employees:

        st.warning("Add employees first")

        st.stop()

    names = [
        e.get("Name", "")
        for e in st.session_state.employees
        if e.get("Name")
    ]

    if not names:

        st.warning("No employee names found")

        st.stop()

    employee = st.selectbox(
        "Select Employee",
        names
    )

    today = pd.Timestamp.now()

    # Sunday off
    if today.weekday() == 6:

        st.warning(
            "Attendance only Monday - Saturday"
        )

        st.stop()

    action = st.radio(
        "Action",
        ["Clock In", "Clock Out"]
    )

    if st.button("Submit Attendance"):

        date = str(today.date())

        time_now = today.strftime("%H:%M:%S")

        attendance = st.session_state.attendance

        df = pd.DataFrame(attendance)

        # =========================================
        # CLOCK IN
        # =========================================
        if action == "Clock In":

            if not df.empty:

                exists = df[
                    (df["Name"] == employee) &
                    (df["Date"] == date)
                ]

                if not exists.empty:

                    st.error(
                        "Employee already clocked in"
                    )

                    st.stop()

            late = time_now > LATE_TIME

            new_record = {
                "Name": employee,
                "Date": date,
                "Time In": time_now,
                "Time Out": ""
            }

            attendance.append(new_record)

            save_daily_upload(
                pd.DataFrame([new_record])
            )

            if late:
                st.warning("Employee is late")

            else:
                st.success(
                    "Clock In recorded successfully"
                )

        # =========================================
        # CLOCK OUT
        # =========================================
        else:

            updated = False

            for rec in attendance:

                if (
                    rec["Name"] == employee
                    and rec["Date"] == date
                ):

                    rec["Time Out"] = time_now

                    updated = True

                    save_daily_upload(
                        pd.DataFrame([rec])
                    )

                    break

            if updated:

                st.success(
                    "Clock Out recorded successfully"
                )

            else:

                st.error("No clock-in found")

# =====================================================
# DAILY UPLOAD
# =====================================================
elif menu == "Daily Upload":

    st.subheader(
        "Upload Daily Attendance CSV Files"
    )

    uploaded_files = st.file_uploader(
        "Upload CSV Files",
        type=["csv"],
        accept_multiple_files=True
    )

    if uploaded_files:

        for uploaded_file in uploaded_files:

            try:

                df = pd.read_csv(uploaded_file)

                df.columns = df.columns.str.strip()

                required_columns = [
                    "Name",
                    "Date",
                    "Time In",
                    "Time Out"
                ]

                missing = [
                    col for col in required_columns
                    if col not in df.columns
                ]

                if missing:

                    st.error(
                        f"{uploaded_file.name} "
                        f"missing columns: "
                        f"{', '.join(missing)}"
                    )

                else:

                    save_daily_upload(df)

                    st.success(
                        f"{uploaded_file.name} uploaded"
                    )

            except Exception as e:

                st.error(
                    f"Error processing "
                    f"{uploaded_file.name}: {e}"
                )

        st.session_state.attendance = (
            load_all_attendance()
        )

# =====================================================
# ATTENDANCE REPORTS
# =====================================================
elif menu == "Attendance Reports":

    st.subheader("Attendance Reports")

    if not st.session_state.attendance:

        st.info("No attendance records found")

        st.stop()

    df = pd.DataFrame(
        st.session_state.attendance
    )

    # =============================================
    # DAILY ATTENDANCE
    # =============================================
    st.subheader("Daily Attendance")

    st.dataframe(
        df,
        use_container_width=True
    )

    # =============================================
    # DATE PROCESSING
    # =============================================
    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    df = df.dropna(subset=["Date"])

    # =============================================
    # WEEKLY REPORT
    # =============================================
    df["Week"] = (
        df["Date"]
        .dt
        .isocalendar()
        .week
        .astype(int)
    )

    weeks = sorted(df["Week"].unique())

    if weeks:

        selected_week = st.selectbox(
            "Select Week",
            weeks
        )

        weekly_df = df[
            df["Week"] == selected_week
        ]

        st.subheader("Weekly Report")

        st.dataframe(
            weekly_df,
            use_container_width=True
        )

    # =============================================
    # LATE STAFF
    # =============================================
    st.subheader("Late Staff")

    df["Time In"] = pd.to_datetime(
        df["Time In"],
        errors="coerce"
    ).dt.time

    late_time = pd.to_datetime(
        LATE_TIME
    ).time()

    late_df = df[
        df["Time In"] > late_time
    ]

    st.dataframe(
        late_df,
        use_container_width=True
    )

    # =============================================
    # OVERTIME STAFF
    # =============================================
    st.subheader("Overtime Staff")

    df["Time Out"] = pd.to_datetime(
        df["Time Out"],
        errors="coerce"
    ).dt.time

    overtime_time = pd.to_datetime(
        OVERTIME_TIME
    ).time()

    overtime_df = df[
        df["Time Out"] >= overtime_time
    ]

    st.dataframe(
        overtime_df,
        use_container_width=True
    )

    # =============================================
    # ABSENTEES
    # =============================================
    st.subheader("Absentees")

    employees = [
        e.get("Name", "")
        for e in st.session_state.employees
    ]

    today = pd.Timestamp.now().date()

    df["Date"] = df["Date"].dt.date

    present = df[
        df["Date"] == today
    ]["Name"].tolist()

    absentees = [
        {
            "Name": e,
            "Date": today,
            "Status": "Absent"
        }
        for e in employees
        if e not in present
    ]

    absent_df = pd.DataFrame(absentees)

    st.dataframe(
        absent_df,
        use_container_width=True
    )

    # =============================================
    # SUMMARY
    # =============================================
    st.subheader("Summary")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Employees",
        len(employees)
    )

    c2.metric(
        "Present",
        len(present)
    )

    c3.metric(
        "Absent",
        len(absentees)
    )

    c4.metric(
        "Late",
        len(late_df)
    )

    c5.metric(
        "Overtime",
        len(overtime_df)
    )

# =====================================================
# LEAVE MANAGEMENT
# =====================================================
elif menu == "Leave Management":

    st.subheader("Leave Management")

    st.info("Leave system coming soon")

# =====================================================
# HR ANALYTICS
# =====================================================
elif menu == "HR Analytics":

    st.subheader("HR Analytics")

    if st.session_state.attendance:

        df = pd.DataFrame(
            st.session_state.attendance
        )

        st.write("Attendance Analytics")

        st.dataframe(
            df.describe(include="all"),
            use_container_width=True
        )

    else:
        st.info("No attendance data available")
