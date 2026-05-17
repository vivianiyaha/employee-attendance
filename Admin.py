import streamlit as st
import os
import base64

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Admin Document Portal", layout="wide")

# =========================
# FOLDERS
# =========================
MEETINGS_FOLDER = "Meetings"
REPORTS_FOLDER = "Reports"

# =========================
# HELPERS
# =========================

def get_files(folder):
    try:
        return os.listdir(folder)
    except Exception as e:
        st.error(f"Error loading files: {e}")
        return []


def display_file(folder, file_name):
    file_path = os.path.join(folder, file_name)

    st.subheader(file_name)

    # PDF → preview + download
    if file_name.endswith(".pdf"):
        with open(file_path, "rb") as f:
            pdf_bytes = f.read()

        st.download_button(
            "Download PDF",
            data=pdf_bytes,
            file_name=file_name,
            mime="application/pdf",
            key=f"pdf_{file_name}"
        )

        st.markdown("### Preview")
        st.components.v1.iframe(
            src=f"data:application/pdf;base64,{base64.b64encode(pdf_bytes).decode()}",
            width=700,
            height=900
        )

    # DOCX → download only
    elif file_name.endswith(".docx"):
        with open(file_path, "rb") as f:
            docx_bytes = f.read()

        st.info("Preview not supported. Download to view in original format.")

        st.download_button(
            "Download DOCX",
            data=docx_bytes,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key=f"docx_{file_name}"
        )

    # TXT → display
    elif file_name.endswith(".txt"):
        with open(file_path, "r") as f:
            st.text(f.read())

    else:
        st.warning("Unsupported file type")

# =========================
# UI
# =========================

st.title("Admin Document Portal")

with st.sidebar:
    st.header("Navigation")

    meeting_files = get_files(MEETINGS_FOLDER)
    selected_meeting = st.selectbox(
        "Meetings",
        ["None"] + meeting_files
    )

    report_files = get_files(REPORTS_FOLDER)
    selected_report = st.selectbox(
        "Reports",
        ["None"] + report_files
    )

# =========================
# DISPLAY
# =========================

if selected_meeting != "None":
    display_file(MEETINGS_FOLDER, selected_meeting)

elif selected_report != "None":
    display_file(REPORTS_FOLDER, selected_report)

else:
    st.info("Select a file from the sidebar")
