import subprocess
from typing import List


def merge_pdfs(inputPaths: List[str], outputPath: str):
    """
    Merges multiple PDF files into one using pandoc.

    Args:
        input_paths (List[str]): A list of paths to the PDF files to merge.
        output_path (str): The path to save the merged PDF file.
    """

    try:
        # Construct the pandoc command
        command = ["pandoc", inputPaths, "-o", outputPath]
        # Execute the pandoc command
        subprocess.run(command, check=True)

    except subprocess.CalledProcessError as e:
        raise Exception(f"Error merging PDFs using pandoc: {e}")

    except FileNotFoundError:
        raise Exception("Pandoc not found. Please make sure pandoc is installed and in your PATH.")