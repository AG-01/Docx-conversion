import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import List
from uuid import uuid4
from zipfile import ZipFile
import asyncio
import requests
from io import BytesIO
from fastapi.responses import FileResponse
from convert import *

app = FastAPI()


app = FastAPI()

DOCS = 'uploads'
PDFS = 'output'
os.makedirs(DOCS, exist_ok=True)
os.makedirs(PDFS, exist_ok=True)

Password_url = "http://password:8001/protect"
merge_url = "http://merge:8002/merge"

@app.post("/convert")
async def upload_file(
    file: UploadFile = File(...),
    password: str = Form(None)
):
    """
    Endpoint to convert the uploaded document into the PDF format.
     - Uses the document_to_pdf helper function
        - Essential logic - pandoc wrapper with xelatex engine
           - Args:
                - input_file (str): Path to the input .docx file.
                - output_file (str): Path to the output .pdf file.
     - If password is provided, protects the PDF using the protect_pdf helper function
        - Essential logic - uses the PyPDF2 library
           - Args:
                - input_file (str): Path to the input .pdf file.
                - output_file (str): Path to the output .pdf file with password protection.
                - password (str): Password to protect the PDF file.
    - Returns the converted PDF file as a response.
    """
    if not file.filename.endswith(('.docx', '.doc')):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a .docx or .doc file.")
    input_filename = f"{uuid4()}_{file.filename}"
    input_path = os.path.join(DOCS, input_filename)
    output_filename = os.path.splitext(input_filename)[0] + '.pdf'
    output_path = os.path.join(PDFS, output_filename)    
    with open(input_path, 'wb') as f:
        content = await file.read()
        f.write(content)
    try:
        document_to_pdf(input_path, output_path)
        
        if password:
            with open(output_path, 'rb') as pdf_file:
                files = {'file': (output_filename, pdf_file, 'application/pdf')}
                data = {'password': password}
                resp = requests.post(Password_url, files=files, data=data)
                if resp.status_code == 200:
                    # Replace output PDF with protected PDF
                    with open(output_path, 'wb') as f:
                        f.write(resp.content)
                else:
                    raise HTTPException(status_code=500, detail="Password protection failed.")
        
        return FileResponse(
            path=output_path,
            media_type='application/pdf',
            filename=os.path.basename(output_path)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during conversion: {str(e)}")
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)

@app.post("/bulk_convert")
async def bulk_convert_endpoint(
    files: List[UploadFile] = File(...),
    password: str = Form(None),
    merge: bool = Form(False)
):
    UPLOAD_FOLDER = '/app/uploads/conversion'
    OUTPUT_FOLDER = '/app/output/conversion'
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    input_files = []
    converted_files = []
    zip_path = None

    try:
        # Save uploaded files
        for file in files:
            if not file.filename.lower().endswith(('.docx', '.doc')):
                raise HTTPException(status_code=400, detail=f"Invalid file format: {file.filename}")
            input_filename = f"{uuid4()}_{file.filename}"
            input_path = os.path.join(UPLOAD_FOLDER, input_filename)
            input_files.append({'filename': file.filename, 'path': input_path})
            with open(input_path, 'wb') as f:
                f.write(await file.read())

        # Convert files
        converted_files = await asyncio.to_thread(bulk_convert, input_files, OUTPUT_FOLDER)

        # Password protection
        if password:
            protected_files = []
            for pdf_path in converted_files:
                with open(pdf_path, 'rb') as pdf_file:
                    files_p = {'file': (os.path.basename(pdf_path), pdf_file, 'application/pdf')}
                    data_p = {'password': password}
                    resp_p = requests.post(Password_url, files=files_p, data=data_p)
                    if resp_p.status_code == 200:
                        protected_path = pdf_path.replace('.pdf', '_protected.pdf')
                        with open(protected_path, 'wb') as f:
                            f.write(resp_p.content)
                        protected_files.append(protected_path)
                    else:
                        raise HTTPException(status_code=500, detail="Password protection failed.")
            converted_files = protected_files

        # Merging PDFs
        if merge:
            files_to_merge = []
            for pdf_path in converted_files:
                files_to_merge.append(
                    ('files', (os.path.basename(pdf_path), open(pdf_path, 'rb'), 'application/pdf'))
                )
            resp_m = requests.post(merge_url, files=files_to_merge)
            if resp_m.status_code == 200:
                merged_filename = f"merged_{uuid4()}.pdf"
                merged_path = os.path.join(OUTPUT_FOLDER, merged_filename)
                # Save merged content to file
                with open(merged_path, 'wb') as f:
                    f.write(resp_m.content)
                return FileResponse(
                    path=merged_path,
                    media_type='application/pdf',
                    filename=merged_filename,
                    background=None  # Prevent background task from deleting file too early
                )
            else:
                raise HTTPException(status_code=500, detail="Merging failed.")
        else:
            # Create zip file only after all conversions are successful
            zip_filename = f"converted_pdfs_{uuid4()}.zip"
            zip_path = os.path.join(OUTPUT_FOLDER, zip_filename)
            with ZipFile(zip_path, 'w') as zipf:
                for pdf_path in converted_files:
                    if os.path.exists(pdf_path):  # Check file exists before adding to zip
                        zipf.write(pdf_path, arcname=os.path.basename(pdf_path))
            
            if not os.path.exists(zip_path):
                raise HTTPException(status_code=500, detail="Failed to create zip file")
                
            return FileResponse(
                path=zip_path,
                media_type='application/zip',
                filename=zip_filename,
                background=None  # Prevent background task from deleting file too early
            )
    except Exception as e:
        # Log the error details
        print(f"Error in bulk_convert_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Delayed cleanup using background tasks
        async def cleanup():
            await asyncio.sleep(1)  # Give time for file to be sent
            # Cleanup uploaded files
            for file in input_files:
                if os.path.exists(file['path']):
                    os.remove(file['path'])
            # Cleanup converted files
            for pdf_path in converted_files:
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
            # Cleanup zip file
            if zip_path and os.path.exists(zip_path):
                os.remove(zip_path)
        
        asyncio.create_task(cleanup())