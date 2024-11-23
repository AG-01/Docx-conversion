
import streamlit as st
import requests
import os
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter

BASE_URL = "http://backend:8000" 

def main():
    st.title("Document Processing Application")

    # Sidebar options
    options = ["Convert Word to PDF", "Password Protect a PDF", "Merge PDFs"]
    choice = st.sidebar.selectbox("Select an option", options)

    if choice == "Convert Word to PDF":
        word_to_pdf()
    elif choice == "Password Protect a PDF":
        password_protect_pdf()
    elif choice == "Merge PDFs":
        merge_pdfs()
    else:
        st.write("Please select an option from the sidebar.")

def word_to_pdf():
    st.header("Word to PDF Converter")

    uploaded_files = st.file_uploader(
        "Upload Word (.docx) files",
        type="docx",
        accept_multiple_files=True
    )

    if uploaded_files:
        num_files = len(uploaded_files)

        if num_files == 1:
            st.write("**1 file uploaded.**")
            # Show password protect checkbox
            protect_with_password = st.checkbox("Protect with password")
            password = None
            if protect_with_password:
                password = st.text_input("Enter a password", type="password")

            if st.button("Convert"):
                # Send request to /upload endpoint
                file = uploaded_files[0]
                files = {
                    'file': (
                        file.name,
                        file.getvalue(),
                        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                    )
                }
                data = {}
                if password:
                    data['password'] = password

                with st.spinner('Converting...'):
                    try:
                        response = requests.post(f"{BASE_URL}/upload", files=files, data=data)
                        if response.status_code == 200:
                            st.success("Conversion successful!")

                            # Provide a download button
                            st.download_button(
                                label="Download PDF",
                                data=response.content,
                                file_name=file.name.replace('.docx', '.pdf'),
                                mime='application/pdf'
                            )
                        else:
                            st.error(f"Conversion failed: {response.text}")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")

        elif num_files > 1:
            st.write(f"**{num_files} files uploaded.**")
            # Show password protect checkbox
            protect_with_password = st.checkbox("Protect with password")
            password = None
            if protect_with_password:
                password = st.text_input("Enter a password", type="password")

            # Show merge option
            merge_option = st.checkbox("Merge PDFs into a single PDF")

            if st.button("Convert"):
                # Send request to /bulk_convert endpoint
                files = []
                for file in uploaded_files:
                    files.append((
                        'files',
                        (
                            file.name,
                            file.getvalue(),
                            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                        )
                    ))

                data = {}
                if password:
                    data['password'] = password
                if merge_option:
                    data['merge'] = 'true'

                with st.spinner('Converting...'):
                    try:
                        response = requests.post(f"{BASE_URL}/bulk_convert", files=files, data=data)
                        if response.status_code == 200:
                            st.success("Conversion successful!")

                            if merge_option:
                                # Provide a download button for the merged PDF
                                st.download_button(
                                    label="Download Merged PDF",
                                    data=response.content,
                                    file_name="merged.pdf",
                                    mime='application/pdf'
                                )
                            else:
                                # Provide a download button for the ZIP file
                                st.download_button(
                                    label="Download ZIP of PDFs",
                                    data=response.content,
                                    file_name="converted_pdfs.zip",
                                    mime='application/zip'
                                )
                        else:
                            st.error(f"Conversion failed: {response.text}")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
    else:
        st.info("Please upload at least one Word (.docx) file.")

def password_protect_pdf():
    st.header("Password Protect a PDF")

    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
    if uploaded_file is not None:
        password = st.text_input("Enter a password", type="password")
        
        if password:
            if st.button("Protect PDF"):
                try:
                    # Read the uploaded PDF
                    pdf_reader = PdfReader(uploaded_file)
                    pdf_writer = PdfWriter()

                    for page in pdf_reader.pages:
                        pdf_writer.add_page(page)

                    # Encrypt the PDF
                    pdf_writer.encrypt(user_pwd=password)

                    # Write the encrypted PDF to a BytesIO object
                    output_pdf = BytesIO()
                    pdf_writer.write(output_pdf)
                    output_pdf.seek(0)

                    st.success("PDF has been password protected!")

                    # Provide a download button
                    st.download_button(
                        label="Download Protected PDF",
                        data=output_pdf,
                        file_name="protected_" + uploaded_file.name,
                        mime='application/pdf'
                    )
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.info("Please enter a password.")
    else:
        st.info("Please upload a PDF file.")

def merge_pdfs():
    st.header("Merge PDFs")

    uploaded_files = st.file_uploader(
        "Upload PDF files to merge",
        type="pdf",
        accept_multiple_files=True
    )

    if uploaded_files:
        if len(uploaded_files) < 2:
            st.warning("Please upload at least two PDF files to merge.")
        else:
            if st.button("Merge PDFs"):
                files = []
                for file in uploaded_files:
                    files.append((
                        'files',
                        (
                            file.name,
                            file.getvalue(),
                            'application/pdf'
                        )
                    ))

                with st.spinner('Merging PDFs...'):
                    try:
                        response = requests.post(f"{BASE_URL}/merge_pdfs", files=files)
                        if response.status_code == 200:
                            st.success("PDFs merged successfully!")

                            # Provide a download button
                            st.download_button(
                                label="Download Merged PDF",
                                data=response.content,
                                file_name="merged.pdf",
                                mime='application/pdf'
                            )
                        else:
                            st.error(f"Merging failed: {response.text}")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
    else:
        st.info("Please upload PDF files.")

if __name__ == "__main__":
    main()