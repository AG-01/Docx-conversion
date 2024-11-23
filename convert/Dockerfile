FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        nano \
        pandoc \
        texlive \
        texlive-xetex \
        texlive-fonts-recommended \
        texlive-latex-extra \
        texlive-plain-generic \
        texlive-latex-recommended \
        lmodern && \
    rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]