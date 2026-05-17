# app.py
# Streamlit Admin App for GitHub File Management + Viewer
#
# Features:
# - Upload .pdf, .docx, .txt files directly to GitHub folder: admin/
# - Collapsible sidebar
# - Dropdown sections:
#     - Meetings
#     - Admin Reports
# - Dynamically loads files from GitHub folders:
#     - Meetings/
#     - Reports/
# - Displays selected file contents on screen
#
# REQUIRED:
# pip install streamlit PyGithub python-docx PyPDF2

import streamlit as st
from github import Github
from github.GithubException import GithubException
from docx import Document
from PyPDF2 import PdfReader
import base64
import io

# =========================
# CONFIG
# =========================


# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Admin Document Portal",
    layout="wide",
)

# =========================
# CUSTOM STYLING
# =========================

st.markdown("""
<style>
.main {
    padding-top: 1rem;
}

section[data-testid="stSidebar"] {
    width: 320px !important;
}

.file-box {
    background-color: #f5f5f5;
    padding: 15px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# HELPERS
# =========================

def upload_file_to_github(uploaded_file):
    try:
        file_path = f"{ADMIN_FOLDER}/{uploaded_file.name}"

        content = uploaded_file.read()

        try:
            existing_file = repo.get_contents(file_path)

            repo.update_file(
                path=file_path,
                message=f"Updated {uploaded_file.name}",
                content=content,
                sha=existing_file.sha,
            )

            st.success(f"Updated {uploaded_file.name} in GitHub")

        except GithubException:
            repo.create_file(
                path=file_path,
                message=f"Uploaded {uploaded_file.name}",
                content=content,
            )

            st.success(f"Uploaded {uploaded_file.name} to GitHub")

    except Exception as e:
        st.error(f"Upload failed: {e}")


def get_files_from_folder(folder_name):
    try:
        contents = repo.get_contents(folder_name)

        files = [
            item.name for item in contents
            if item.type == "file"
        ]

        return files

    except Exception as e:
        st.error(f"Could not load files from {folder_name}: {e}")
        return []


def get_file_content(folder_name, file_name):
    path = f"{folder_name}/{file_name}"

    file = repo.get_contents(path)

    return base64.b64decode(file.content)


def read_pdf(file_bytes):
    pdf = PdfReader(io.BytesIO(file_bytes))

    text = ""

    for page in pdf.pages:
        text += page.extract_text() + "\n"

    return text


def read_docx(file_bytes):
    doc = Document(io.BytesIO(file_bytes))

    text = "\n".join([para.text for para in doc.paragraphs])

    return text


def display_file(folder_name, file_name):
    file_bytes = get_file_content(folder_name, file_name)

    lower = file_name.lower()

    st.subheader(file_name)

    if lower.endswith(".txt"):
        text = file_bytes.decode("utf-8")
        st.text_area("Content", text, height=500)

    elif lower.endswith(".docx"):
        text = read_docx(file_bytes)
        st.text_area("Content", text, height=500)

    elif lower.endswith(".pdf"):
        text = read_pdf(file_bytes)
        st.text_area("Extracted PDF Text", text, height=500)

        st.download_button(
            label="Download PDF",
            data=file_bytes,
            file_name=file_name,
            mime="application/pdf",
        )

    else:
        st.warning("Unsupported file format")


# =========================
# MAIN HEADER
# =========================

st.title("Admin Document Management Portal")

# =========================
# FILE UPLOAD SECTION
# =========================

st.header("Upload Files")

upload_type = st.selectbox(
    "Select destination folder",
    ["admin", "Meetings", "Reports"]
)

uploaded_file = st.file_uploader(
    "Upload PDF, DOCX, or TXT",
    type=["pdf", "docx", "txt"]
)

if uploaded_file and st.button("Upload to GitHub"):
    upload_file_to_github(uploaded_file, upload_type)

# =========================
# SIDEBAR
# =========================

with st.sidebar:
    st.title("Navigation")

    # Meetings Dropdown
    with st.expander("Meetings", expanded=False):

        meeting_files = get_files_from_folder(MEETINGS_FOLDER)

        selected_meeting = st.selectbox(
            "Select Meeting File",
            ["None"] + meeting_files,
            key="meetings_select"
        )

    # Reports Dropdown
    with st.expander("Admin Reports", expanded=False):

        report_files = get_files_from_folder(REPORTS_FOLDER)

        selected_report = st.selectbox(
            "Select Report File",
            ["None"] + report_files,
            key="reports_select"
        )

# =========================
# DISPLAY CONTENT
# =========================

if selected_meeting != "None":
    display_file(MEETINGS_FOLDER, selected_meeting)

elif selected_report != "None":
    display_file(REPORTS_FOLDER, selected_report)

else:
    st.info("Select a file from the sidebar to view content.")
