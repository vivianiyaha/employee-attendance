import streamlit as st
import os

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Dropdown select button
meeting_type = st.selectbox(
    "Select Meeting Type",
    [
        "Board Meeting",
        "Management Meeting",
        "Project Meeting",
        "HR Meeting",
        "Client Meeting"
    ]
)

st.write(f"Selected: {meeting_type}")

uploaded_file = st.file_uploader(
    "Upload Meeting File",
    type=["pdf", "docx", "txt"]
)

if uploaded_file is not None:

    # Create folder based on dropdown selection
    meeting_folder = os.path.join(
        UPLOAD_FOLDER,
        meeting_type.replace(" ", "_")
    )

    os.makedirs(meeting_folder, exist_ok=True)

    file_path = os.path.join(
        meeting_folder,
        uploaded_file.name
    )

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(
        f"{uploaded_file.name} uploaded successfully to {meeting_type}"
    )
