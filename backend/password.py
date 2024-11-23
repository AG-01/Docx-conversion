from PyPDF2 import PdfReader, PdfWriter

def protect_pdf(inputPath, outputPath, key):
    reader = PdfReader(inputPath)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(user_password=key, owner_password=key, use_128bit=True)
    with open(outputPath, 'wb') as f:
        writer.write(f)