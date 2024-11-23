# Use an official Python runtime as a parent image
FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies if needed
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        nano && \
    rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose port
EXPOSE 8002

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8002"]