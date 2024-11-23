import subprocess
import os
from uuid import uuid4

def document_to_pdf(inputPath, outputPath):
    """
    Converts a .docx file to a .pdf file using Pandoc with a specific LaTeX engine.

    Args:
        input_file (str): Path to the input .docx file.
        output_file (str): Path to the output .pdf file.
    """
    try:
        command = ["pandoc", inputPath, "-o", outputPath, "--pdf-engine=xelatex"]
        subprocess.run(command, check=True)
        print(f"Conversion successful: {inputPath} -> {outputPath}")
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")
        raise e
    
def bulk_convert(input_files: list, output_folder: str):
    """'
    Converts multiple .docx files to .pdf files using Pandoc with a specific LaTeX engine.
    
    Args:
        input_files (List[Dict]): List of dictionaries containing the path to the input .docx files.
        output_folder (str): Path to the output folder where the converted .pdf files will be saved.
    """
    converted_files = []
    for file in input_files:
        input_path = file['path']
        output_filename = f"{uuid4()}_{input_path.split('/')[-1].replace('.docx', '.pdf')}"
        output_path = f"{output_folder}/{output_filename}"
        document_to_pdf(input_path, output_path)
        converted_files.append(output_path)
    return converted_files