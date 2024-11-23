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

# Existing '/upload' endpoint for single file conversion
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    password: str = Form(None)
):
    if not file.filename.endswith(('.docx', '.doc')):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a .docx or .doc file.")
    
    # Generate unique filenames
    input_filename = f"{uuid4()}_{file.filename}"
    input_path = os.path.join(UPLOAD_FOLDER, input_filename)
    output_filename = os.path.splitext(input_filename)[0] + '.pdf'
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    
    # Save the uploaded file
    with open(input_path, 'wb') as f:
        content = await file.read()
        f.write(content)
    
    try:
        # Convert document to PDF
        document_to_pdf(input_path, output_path)
        
        # Apply password protection if a password is provided
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
        # Clean up the uploaded file
        if os.path.exists(input_path):
            os.remove(input_path)
        
@app.post("/bulk_convert")
async def bulk_convert(
    files: List[UploadFile] = File(...),
    password: str = Form(None),
    merge: bool = Form(False)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")
    
    input_paths = []
    output_paths = []
    
    try:
        # Save uploaded files
        for file in files:
            if not file.filename.endswith(('.docx', '.doc')):
                raise HTTPException(status_code=400, detail=f"Invalid file format detected: {file.filename}")
            input_filename = f"{uuid4()}_{file.filename}"
            input_path = os.path.join(UPLOAD_FOLDER, input_filename)
            input_paths.append(input_path)
            
            # Save the uploaded file
            with open(input_path, 'wb') as f:
                content = await file.read()
                f.write(content)
        
        # Convert documents to PDFs and apply password protection if needed
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
            # Merge PDFs into a single PDF
            merged_output_filename = f"merged_{uuid4()}.pdf"
            merged_output_path = os.path.join(OUTPUT_FOLDER, merged_output_filename)
            merge_pdfs(output_paths, merged_output_path)
            
            # Clean up individual PDFs after merging
            for path in output_paths:
                if os.path.exists(path):
                    os.remove(path)
            
            # Apply password protection to the merged PDF if password is provided
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
            # Create and return ZIP file
            zip_filename = f"converted_{uuid4()}.zip"
            zip_path = os.path.join(OUTPUT_FOLDER, zip_filename)
            with ZipFile(zip_path, 'w') as zipf:
                for output_path in output_paths:
                    zipf.write(output_path, arcname=os.path.basename(output_path))
            
            # Clean up individual PDFs after creating ZIP
            for path in output_paths:
                if os.path.exists(path):
                    os.remove(path)
            
            response = FileResponse(
                path=zip_path,
                media_type='application/zip',
                filename=os.path.basename(zip_path)
            )
        
        # Clean up input files
        for path in input_paths:
            if os.path.exists(path):
                os.remove(path)
        
        return response
        
    except Exception as e:
        # Clean up any remaining files in case of error
        for path in input_paths + output_paths:
            if os.path.exists(path):
                os.remove(path)
        raise HTTPException(status_code=500, detail=f"Error during bulk conversion: {str(e)}")
    
# Existing '/merge_pdfs' endpoint for merging PDFs directly
@app.post("/merge_pdfs")
async def merge_pdfs_endpoint(files: List[UploadFile] = File(...)):
    if not files or len(files) < 2:
        raise HTTPException(status_code=400, detail="Please upload at least two PDF files to merge.")
    
    input_paths = []
    try:
        # Save uploaded PDF files
        for file in files:
            if not file.filename.endswith('.pdf'):
                raise HTTPException(status_code=400, detail=f"Invalid file format detected: {file.filename}")
            input_filename = f"{uuid4()}_{file.filename}"
            input_path = os.path.join(UPLOAD_FOLDER, input_filename)
            input_paths.append(input_path)

            # Save the uploaded file
            with open(input_path, 'wb') as f:
                content = await file.read()
                f.write(content)
        
        # Merge PDFs
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
        # Clean up the input and output files
        for input_path in input_paths:
            if os.path.exists(input_path):
                os.remove(input_path)
        if 'merged_output_path' in locals() and os.path.exists(merged_output_path):
            os.remove(merged_output_path)