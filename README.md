# Resume Parser API

The **Resume Parser API** is a Flask-based web application designed to parse resumes and extract meaningful information such as personal details, job roles, education, skills, and more. This API processes uploaded PDF resumes, analyzes their content, and returns structured JSON data that can be used by frontend applications or integrated into other systems.

---

## Features

- Upload and parse resumes in PDF format.
- Extract critical information, including:
  - Name
  - Email
  - LinkedIn URL
  - Address
  - Job Role/Title
  - Profile Summary
  - Skills
  - Experience (with company, role, start and end dates, and description)
  - Education
  - Certificates
  - Interests
  - Projects
- Automatically deletes uploaded resumes after processing to ensure data security.

---

## How It Works

1. **Upload a Resume**:
   - A user uploads a PDF resume via a POST request.
2. **Parse Resume**:
   - The API uses a custom Python parser to extract structured data from the uploaded resume.
3. **Return Response**:
   - The extracted data is returned as a JSON response to the frontend or client application.
4. **Delete File**:
   - The uploaded resume is deleted from the server after parsing.

---

## API Endpoints

### `GET /`

#### Request
- **Description**: Health check endpoint to verify the application is running.

#### Response
- **Success** (`200 OK`):
  - Returns a JSON response with status and additional system information.
    ```
      {
        "environment": "production",
        "message": "Welcome to the Resume Parser API!",
        "status": "healthy",
        "upload_folder_accessible": true,
        "version": "<api-version>"
      }
      ```
- **Error** (`500 Internal Server Error`):
  - Returns a JSON response with error information.

### `POST /api/v1/upload`

#### Request
- **Description**: Upload a resume in PDF format for parsing.
- **Headers**:
  - `Content-Type: multipart/form-data`
- **Body Parameters**:
  - `file`: The resume file to upload (PDF and DOCX format only).

#### Response
- **Success** (`200 OK`):
  - Returns parsed resume data in JSON format.
    ```
      {
        "resume_data": {
          "awards": [],
          "certifications": [
              {
                 "name": "",
                 "code": "",
                 "date": ""  
              }
          ],
          "education": [
              {
                  "degree": "",
                  "end_year": "",
                  "institution": "",
                  "start_year": ""
              }
          ],
          "email": "@gmail.com",
          "first_name": "Temitope",
          "interests": [],
          "job_title": "Flutter Developer",
          "last_name": "Aladesiun",
          "linkedin": "",
          "profile_summary": "",
          "skills": [
              {
                  "skill": "Programming Languages & Frameworks",
                  "tools": "Flutter, Dart, Javascript, Typescript, HTML, CSS, ReactJS, VueJS"
              }
          ],
          "work_experience": [
              {
                  "company": "",
                  "company_description": "",
                  "end_date": "",
                  "job_description": "",
                  "job_title": "",
                  "location": "",
                  "start_date": ""
              },
            
          ]
      }
    }
    ```
- **Error** (`400 Bad Request` or `500 Internal Server Error`):
  - Returns an error message if the file is invalid or processing fails.

#### Example Request
```bash
curl -X POST http://127.0.0.1:5000/upload \
-F "file=@resume.pdf"
```

## Local Setup

### Clone the Repository

```bash
# Clone the repository
git clone https://github.com/S13G/resume-parser-api.git

# Navigate to the project directory
cd resume-parser-api

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.
```

### Create a `.env` FILE

```bash
# Add the following requirements
ANTHROPIC_API_KEY=your_anthropic_api_key
# Add any other necessary environment variables
```

### Run the Application

```bash
# Run the application
python run.py
```

## Docker Setup

```bash
# Build the Docker image
docker build -t resume-parser-api .

# Run the Docker container
docker run -p 5000:5000 resume-parser-api

# OR

# Build the Docker image
docker-compose build

# Run the application
docker-compose up
```