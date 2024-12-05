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

### `POST /upload`

#### Request
- **Description**: Upload a resume in PDF format for parsing.
- **Headers**:
  - `Content-Type: multipart/form-data`
- **Body Parameters**:
  - `file`: The resume file to upload (PDF format only).

#### Response
- **Success** (`200 OK`):
  - Returns parsed resume data in JSON format.
- **Error** (`400 Bad Request` or `500 Internal Server Error`):
  - Returns an error message if the file is invalid or processing fails.

#### Example Request
```bash
curl -X POST http://127.0.0.1:5000/upload \
-F "file=@resume.pdf"
