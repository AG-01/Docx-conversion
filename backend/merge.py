
from PyPDF2 import PdfMerger
from typing import List

def merge_pdfs(input_paths: List[str], output_path: str):
    """
    Merges multiple PDF files into one using PyPDF2.

    Args:
        input_paths (List[str]): A list of paths to the PDF files to merge.
        output_path (str): The path to save the merged PDF file.
    """
    try:
        merger = PdfMerger()        
        for pdf_path in input_paths:
            merger.append(pdf_path)        
        with open(output_path, 'wb') as output_file:
            merger.write(output_file)            
        merger.close()
            
    except Exception as e:
        raise Exception(f"Error merging PDFs: {str(e)}")