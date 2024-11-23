from PyPDF2 import PdfReader, PdfWriter
from fastapi import HTTPException
from io import BytesIO

def merge_pdfs(input_pdfs: list) -> bytes:
    """
    Merges multiple PDF files into one.
    
    Args:
        input_pdfs (list): List of PDF files in bytes.
    
    """
    pdf_writer = PdfWriter()
    
    try:
        for pdf_bytes in input_pdfs:
            pdf_reader = PdfReader(BytesIO(pdf_bytes))
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
        
        output = BytesIO()
        pdf_writer.write(output)
        merged_pdf = output.getvalue()
        return merged_pdf
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Merging failed: {e}")