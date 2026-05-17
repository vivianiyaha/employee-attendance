import streamlit as st
import requests
from docx import Document
from PyPDF2 import PdfReader
import io

# =========================
# CONFIG
# =========================

GITHUB_USER = "vivianiyaha"
REPO_NAME = "employee-attendance"
BRANCH = "main"

MEETINGS_FOLDER = "Meetings"
REPORTS_FOLDER = "Reports"

BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}"

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Admin Document Portal",
    layout="wide",
)

# =========================
# HELPERS
# =========================

def get_files_from_github(folder):
    """Fetch file list from GitHub API (public repo only)"""
    api_url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/contents/{folder}"

    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        return [file["name"] for file in data if file["type"] == "file"]
    else:
        st.error(f"Error loading {folder}")
        return []


def get_file_content(folder, file_name):
    """Download raw file"""
    url = f"{BASE_URL}/{folder}/{file_name}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.content
    else:
        st.error("Failed to fetch file")
        return None


def read_pdf(file_bytes):
    pdf = PdfReader(io.BytesIO(file_bytes))
    text = ""

    for page in pdf.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"

    return text


def read_docx(file_bytes):
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join([p.text for p in doc.paragraphs])


def display_file(folder, file_name):
    file_bytes = get_file_content(folder, file_name)

    if not file_bytes:
        return

    st.subheader(file_name)

    if file_name.endswith(".txt"):
        st.text_area("Content", file_bytes.decode("utf-8"), height=500)

    elif file_name.endswith(".docx"):
        st.text_area("Content", read_docx(file_bytes), height=500)

    elif file_name.endswith(".pdf"):
        text = read_pdf(file_bytes)
        st.text_area("Extracted Text", text, height=500)

        st.download_button(
            "Download PDF",
            data=file_bytes,
            file_name=file_name,
            mime="application/pdf"
        )

    else:
        st.warning("Unsupported format")


# =========================
# UI
# =========================

st.title("Admin Document Portal")

with st.sidebar:
    st.header("Navigation")

    # Meetings
    with st.expander("Meetings"):
        meeting_files = get_files_from_github(MEETINGS_FOLDER)

        selected_meeting = st.selectbox(
            "Select Meeting File",
            ["None"] + meeting_files
        )

    # Reports
    with st.expander("Reports"):
        report_files = get_files_from_github(REPORTS_FOLDER)

        selected_report = st.selectbox(
            "Select Report File",
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
