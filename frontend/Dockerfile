# Use the official Python image as the base image
FROM python:3.9-slim-buster

# Set the working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the Streamlit default port
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "index.py", "--server.port=8501", "--server.address=0.0.0.0"]