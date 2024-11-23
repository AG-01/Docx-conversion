# Docx-conversion
---

## Features

- **Docx to PDF Conversion:** Convert `.docx` and `.doc` files to high-quality PDFs.
- **Password Protection:** Secure your PDFs with a custom password to prevent unauthorized access.
- **PDF Merging:** Combine multiple PDFs into a single document for streamlined management.
- **Intuitive Frontend:** User-friendly interface built with Streamlit for easy interaction.
- **Automated CI/CD Pipeline:** Utilize GitHub Actions for continuous integration and deployment of Docker images.
- **Microservices Architecture:** Modular design with independent services for scalability and maintainability.

---

## Technologies Used

- **Backend:**
  - [FastAPI](https://fastapi.tiangolo.com/) - High-performance web framework for building APIs with Python.
  - [Python 3.9](https://www.python.org/) - Programming language.
  - [Uvicorn](https://www.uvicorn.org/) - Lightning-fast ASGI server.
  - [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation and settings management using Python type annotations.
  
- **Frontend:**
  - [Streamlit](https://streamlit.io/) - Open-source app framework for Machine Learning and Data Science teams.
  
- **Containerization:**
  - [Docker](https://www.docker.com/) - Platform for developing, shipping, and running applications in containers.
  - [Docker Compose](https://docs.docker.com/compose/) - Tool for defining and running multi-container Docker applications.
  
- **CI/CD:**
  - [GitHub Actions](https://github.com/features/actions) - Automate, customize, and execute software development workflows right in GitHub.
  
- **Others:**
  - [Pandoc](https://pandoc.org/) - Universal document converter.
  - [TexLive](https://www.tug.org/texlive/) - Comprehensive TeX document production system.

---

## Directory Structure

```
docx-conversion/
├── frontend/
│   ├── Dockerfile
│   ├── index.py
│   └── requirements.txt
├── conversion_service/
│   ├── Dockerfile
│   ├── app.py
│   ├── convert.py
│   └── requirements.txt
├── protect/
│   ├── Dockerfile
    |── password.py
│   ├── app.py
│   └── requirements.txt
├── merge/
│   ├── Dockerfile
│   ├── app.py
│   ├── merge.py
│   └── requirements.txt
├── .github/
│   └── workflows/
│       └── docker-image.yml
├── docker-compose.yaml
├── run_containers.sh
├── README.md
└── .gitignore
```

---

## Prerequisites

- **Docker:** [Install Docker](https://docs.docker.com/get-docker/) on your machine.
- **Docker Compose:** [Install Docker Compose](https://docs.docker.com/compose/install/) if not included with Docker.
- **Git:** [Install Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).
- **GitHub Account:** For accessing the repository and setting up GitHub Actions.
- **Docker Hub Account:** To store and manage Docker images.
  
---

## Setup and Installation

### 1. Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/AG-01/docx-conversion.git
cd docx-conversion
```

### 2. Build and Run Docker Containers

You have two options to build and run the Docker containers: using the provided bash script or running Docker Compose commands directly.

#### Using the Bash Script

The `run_containers.sh` script automates the process of building Docker images, starting the containers, and opening the Streamlit frontend in your default browser.

1. **Make the Script Executable:**

   ```bash
   chmod +x run_containers.sh
   ```

2. **Run the Script:**

   ```bash
   ./run_containers.sh
   ```

   **Script Details:**

   - **Build Docker Images:** Uses `docker-compose build` to build all services.
   - **Start Containers:** Launches all services in detached mode with `docker-compose up -d`.
   - **Open Streamlit Frontend:** Waits for initialization and opens the frontend in your default browser.

   **Sample Output:**

   ```
   ===============================
   Building Docker images...
   ===============================
   # Docker builds output...
   ===============================
   Starting Docker containers...
   ===============================
   # Docker containers startup output...
   ===============================
   All containers are up and running.
   ===============================
   # Listing of running containers...
   ===============================
   Waiting for Streamlit frontend to initialize...
   ===============================
   Opening Streamlit frontend in your default browser...
   ==============================================
   Streamlit frontend should now be open in your browser.
   ==============================================
   ```

#### Using Docker Compose Directly

If you prefer manual control or are using a non-Unix environment (like Windows without Git Bash), you can use Docker Compose commands directly.

1. **Build Docker Images:**

   ```bash
   docker-compose build
   ```

2. **Start Docker Containers:**

   ```bash
   docker-compose up -d
   ```

3. **Verify Containers are Running:**

   ```bash
   docker-compose ps
   ```

4. **Access the Application:**

   Open your web browser and navigate to [http://localhost:8501](http://localhost:8501) to access the Streamlit frontend.

---

---

## Usage

Once the Docker containers are up and running, you can interact with the application through the Streamlit frontend.

### Uploading Files

1. **Access the Frontend:**

   Navigate to [http://localhost:8501](http://localhost:8501) in your web browser.

2. **Select Files:**

   - Click on the "Upload Files" button.
   - Select one or multiple `.docx` or `.doc` files from your local machine.

### Password Protecting PDFs

1. **Set a Password (Optional):**

   - In the frontend interface, there is an option to set a password.
   - Enter a secure password to protect your converted PDFs. This step is optional.

### Merging PDFs

1. **Enable Merging (Optional):**

   - Toggle the "Merge PDFs" option if you wish to combine all converted PDFs into a single document.

### Downloading Results

1. **Initiate Conversion:**

   - After uploading the files and setting your preferences, click the "Convert" button.

2. **Download Converted Files:**

   - **Without Merging:** If merging is disabled, a ZIP file containing all your converted PDFs will be available for download.
   - **With Merging:** If merging is enabled, a single merged PDF will be available for download.
   - **Password Protection:** If a password was set, the downloaded PDFs will be encrypted with the provided password.

---
### Getting Detailed Logs

To view logs for a specific service, use:

```bash
docker-compose logs <service_name>
```

**Example:**

```bash
docker-compose logs frontend
docker-compose logs protection_service
docker-compose logs merge
docker-compose logs conversion_service
```

---
