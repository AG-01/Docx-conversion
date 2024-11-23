from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from typing import List
import os
from uuid import uuid4
from zipfile import ZipFile

from convert import document_to_pdf
from password import protect_pdf
from merge import merge_pdfs

app = FastAPI()

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@app.post("/upload")
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
    input_path = os.path.join(UPLOAD_FOLDER, input_filename)
    output_filename = os.path.splitext(input_filename)[0] + '.pdf'
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)    
    with open(input_path, 'wb') as f:
        content = await file.read()
        f.write(content)
    try:
        document_to_pdf(input_path, output_path)
        
        if password:
            protected_output = os.path.join(OUTPUT_FOLDER, f"protected_{output_filename}")
            protect_pdf(output_path, protected_output, password)
            os.replace(protected_output, output_path)
        
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
async def bulk_convert(
    files: List[UploadFile] = File(...),
    password: str = Form(None),
    merge: bool = Form(False)
):
    """
    Endpoint to convert the multiple documents into the PDF format.
    
    
     - Uses the document_to_pdf helper function iteratively for each uploaded document
     
        - Essential logic - pandoc wrapper with xelatex engine
           - Args:
                - input_file (str): Path to the input .docx file.
                - output_file (str): Path to the output .pdf file.  
                
                
         - If password is provided, protects the PDF using the protect_pdf helper function.
            To be Noted : All the converted pdfs will have the same password.
        
            - Essential logic - uses the PyPDF2 library
                - Args:
                    - input_file (str): Path to the input .pdf file.
                    - output_file (str): Path to the output .pdf file with password protection.
                    - password (str): Password to protect the PDF file.
         - If merge is True, merges all the converted PDFs into a single PDF using the merge_pdfs helper function.
            - Essential logic - uses the PyPDF2 library
                - Args:
                    - input_files (List[str]): List of paths to the input .pdf files.
                    - output_file (str): Path to the output .pdf file with merged PDFs.
    
    - Returns the zip file of converted PDF files as a response.

    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")
    
    input_paths = []
    output_paths = []
    
    try:
        for file in files:
            if not file.filename.endswith(('.docx', '.doc')):
                raise HTTPException(status_code=400, detail=f"Invalid file format detected: {file.filename}")
            input_filename = f"{uuid4()}_{file.filename}"
            input_path = os.path.join(UPLOAD_FOLDER, input_filename)
            input_paths.append(input_path)            
            with open(input_path, 'wb') as f:
                content = await file.read()
                f.write(content)
        
        for input_path in input_paths:
            output_filename = os.path.splitext(os.path.basename(input_path))[0] + '.pdf'
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            document_to_pdf(input_path, output_path)
            
            if password:
                protected_output = os.path.join(OUTPUT_FOLDER, f"protected_{output_filename}")
                protect_pdf(output_path, protected_output, password)
                os.replace(protected_output, output_path)
            output_paths.append(output_path)
        
        if merge:
            merged_output_filename = f"merged_{uuid4()}.pdf"
            merged_output_path = os.path.join(OUTPUT_FOLDER, merged_output_filename)
            merge_pdfs(output_paths, merged_output_path)            
            for path in output_paths:
                if os.path.exists(path):
                    os.remove(path)            
            if password:
                protected_merged_output = os.path.join(OUTPUT_FOLDER, f"protected_{merged_output_filename}")
                protect_pdf(merged_output_path, protected_merged_output, password)
                os.replace(protected_merged_output, merged_output_path)
            
            response = FileResponse(
                path=merged_output_path,
                media_type='application/pdf',
                filename=os.path.basename(merged_output_path)
            )
        else:
            zip_filename = f"converted_{uuid4()}.zip"
            zip_path = os.path.join(OUTPUT_FOLDER, zip_filename)
            with ZipFile(zip_path, 'w') as zipf:
                for output_path in output_paths:
                    zipf.write(output_path, arcname=os.path.basename(output_path))
            
            for path in output_paths:
                if os.path.exists(path):
                    os.remove(path)
            
            response = FileResponse(
                path=zip_path,
                media_type='application/zip',
                filename=os.path.basename(zip_path)
            )
        
        for path in input_paths:
            if os.path.exists(path):
                os.remove(path)
        
        return response
        
    except Exception as e:
        for path in input_paths + output_paths:
            if os.path.exists(path):
                os.remove(path)
        raise HTTPException(status_code=500, detail=f"Error during bulk conversion: {str(e)}")
    
@app.post("/merge_pdfs")
async def merge_pdfs_endpoint(files: List[UploadFile] = File(...)):
    """
    Endpoint to merge multiple PDF files into a single PDF file.
     - Uses the merge_pdfs helper function to merge the uploaded PDF files.
        - Essential logic - uses the PyPDF2 library
         - Args:
            - input_files (List[str]): List of paths to the input .pdf files.
            - output_file (str): Path to the output .pdf file with merged PDFs.
    - Returns the merged PDF file as a response.
    """
    if not files or len(files) < 2:
        raise HTTPException(status_code=400, detail="Please upload at least two PDF files to merge.")
    
    input_paths = []
    try:
        for file in files:
            if not file.filename.endswith('.pdf'):
                raise HTTPException(status_code=400, detail=f"Invalid file format detected: {file.filename}")
            input_filename = f"{uuid4()}_{file.filename}"
            input_path = os.path.join(UPLOAD_FOLDER, input_filename)
            input_paths.append(input_path)

            with open(input_path, 'wb') as f:
                content = await file.read()
                f.write(content)
        
        merged_output_filename = f"merged_{uuid4()}.pdf"
        merged_output_path = os.path.join(OUTPUT_FOLDER, merged_output_filename)
        merge_pdfs(input_paths, merged_output_path)

        return FileResponse(
            path=merged_output_path,
            media_type='application/pdf',
            filename=os.path.basename(merged_output_path)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during PDF merging: {str(e)}")
    finally:
        for input_path in input_paths:
            if os.path.exists(input_path):
                os.remove(input_path)
        if 'merged_output_path' in locals() and os.path.exists(merged_output_path):
            os.remove(merged_output_path)