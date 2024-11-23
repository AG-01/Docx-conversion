from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from password import protect_pdf
from io import BytesIO
import os

app = FastAPI()

@app.post("/protect")
async def protect_pdf_endpoint(
    file: UploadFile = File(...),
    password: str = Form(...)
):
    """
    Endpoint to password-protect a PDF file.
    - Uses the protect_pdf helper function
        - Essential logic - uses the PyPDF2 library to password-protect a PDF file.
        - Args:
            - input_file (bytes): Byte content of the input PDF file.
            - password (str): Password to protect the PDF file.
            
    - Returns the password-protected PDF file as a response.
    
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a PDF file.")
    
    input_content = await file.read()
    
    try:
        # Protect the PDF
        protected_pdf = protect_pdf(input_content, password)
        
        return Response(content=protected_pdf, media_type='application/pdf')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))