# Use the official Python image as the base image
FROM python:3.9-slim-buster

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    apt install nano \
    pandoc \
    texlive \
    texlive-xetex \
    texlive-fonts-recommended \
    texlive-latex-extra && \
    texlive-plain-generic \
    texlive-latex-recommended \
    lmodern \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
# Install required packages for PDF conversion



# Set the working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Run the FastAPI app with Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]