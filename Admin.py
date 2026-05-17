import streamlit as st
import os
from docx import Document
from PyPDF2 import PdfReader
import io

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
    except:
        return []

def read_docx(file_path):
    try:
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        return f"Error reading DOCX: {e}"

def read_pdf(file_path):
    try:
        pdf = PdfReader(file_path)
        text = ""
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

def display_file(folder, file_name):
    file_path = os.path.join(folder, file_name)

    st.subheader(file_name)

    if file_name.endswith(".txt"):
        with open(file_path, "r") as f:
            st.text_area("Content", f.read(), height=500)

    elif file_name.endswith(".docx"):
        st.text_area("Content", read_docx(file_path), height=500)

    elif file_name.endswith(".pdf"):
        st.text_area("Content", read_pdf(file_path), height=500)

    else:
        st.warning("Unsupported format")

# =========================
# UI
# =========================

st.title("Admin Document Portal")

with st.sidebar:
    st.header("Navigation")

    meeting_files = get_files(MEETINGS_FOLDER)
    selected_meeting = st.selectbox("Meetings", ["None"] + meeting_files)

    report_files = get_files(REPORTS_FOLDER)
    selected_report = st.selectbox("Reports", ["None"] + report_files)

# =========================
# DISPLAY
# =========================

if selected_meeting != "None":
    display_file(MEETINGS_FOLDER, selected_meeting)

elif selected_report != "None":
    display_file(REPORTS_FOLDER, selected_report)

else:
    st.info("Select a file")
