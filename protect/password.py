from PyPDF2 import PdfReader, PdfWriter
from fastapi import HTTPException
from io import BytesIO

def protect_pdf(input_pdf: bytes, password: str) -> bytes:
    """
    Protects a PDF with a password.
    
    Args:
        input_pdf (bytes): The original PDF file in bytes.
        password (str): The password to protect the PDF with.
    
    Returns:
        bytes: The password-protected PDF file in bytes.
    """
    try:
        pdf_reader = PdfReader(BytesIO(input_pdf))
        pdf_writer = PdfWriter()
        
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)
        
        pdf_writer.encrypt(user_pwd=password)
        
        output = BytesIO()
        pdf_writer.write(output)
        protected_pdf = output.getvalue()
        return protected_pdf
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Password protection failed: {e}")