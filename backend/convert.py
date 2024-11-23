import subprocess

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
