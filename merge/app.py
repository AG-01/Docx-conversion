from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response
from merge import merge_pdfs
from io import BytesIO

app = FastAPI()

@app.post("/merge")
async def merge_pdfs_endpoint(files: list[UploadFile] = File(...)):
    """
    Endpoint to merge multiple PDF files into a single PDF.
        - Uses the merge_pdfs helper function
            - Essential logic - uses the PyPDF2 library to merge multiple PDF files.
            - Args:
                - pdf_contents (List[bytes]): List of byte contents of the PDF files to merge.
        - Returns the merged PDF file as a response.
    """
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="Please upload at least two PDF files to merge.")
    
    pdf_contents = []
    try:
        for file in files:
            if not file.filename.endswith('.pdf'):
                raise HTTPException(status_code=400, detail=f"Invalid file format detected: {file.filename}")
            content = await file.read()
            pdf_contents.append(content)
        
        # Merge PDFs
        merged_pdf = merge_pdfs(pdf_contents)
        
        return Response(content=merged_pdf, media_type='application/pdf')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))