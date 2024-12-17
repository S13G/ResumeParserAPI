import json
import os

import fitz  # noqa
from docx import Document  # noqa
from docx.shared import Pt  # noqa
from dotenv import load_dotenv
from flask import request, jsonify
from pydantic import ValidationError
from werkzeug.utils import secure_filename

from parser import create_app
from parser.entity_resume import parse_resume
from parser.schema import FileMetadata

# Load environment variables from .env file
load_dotenv()

app = create_app()

# Define upload folder
UPLOAD_FOLDER = app.config["UPLOAD_FOLDER"]
APP_VERSION = "1.0.5"


def convert_pdf_to_docx(pdf_path):
    """
    Convert PDF to DOCX by extracting text using PyMuPDF and creating a new DOCX file
    """
    try:
        # Open the PDF
        pdf_document = fitz.open(pdf_path)

        # Extract text from all pages
        full_text = ""
        for page in range(len(pdf_document)):
            page = pdf_document.load_page(page)
            full_text += page.get_text() + "\n\n"

        # Close the PDF document
        pdf_document.close()

        # Create a new DOCX document
        docx_path = pdf_path.replace(".pdf", ".docx")
        doc = Document()

        # Add text to the document
        paragraph = doc.add_paragraph()
        paragraph.style = "Normal"
        run = paragraph.add_run(full_text)

        # Optional: Set font and size
        font = run.font
        font.name = "Calibri"  # noqa
        font.size = Pt(11)

        # Save the DOCX file
        doc.save(docx_path)

        return docx_path

    except Exception as e:  # noqa
        return (
            jsonify(
                {
                    "error": f"Empty resume parsing result. Please try again or use another."
                }
            ),
            400,
        )


@app.route("/", methods=["GET"])
def health_check():
    try:
        health_info = {
            "status": "healthy",
            "message": "Welcome to the Resume Parser API!",
            "version": APP_VERSION,
            "upload_folder_accessible": os.path.exists(UPLOAD_FOLDER),
            "environment": os.getenv("FLASK_ENV", "Not set"),
        }
        return jsonify(health_info), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


@app.route("/api/v1/upload", methods=["POST"])
def upload_cv():
    # Ensure the upload folder exists
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # Handle file upload and CV processing
    file = request.files.get("file")
    if not file or file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Check file size
    file.seek(0, os.SEEK_END)  # Move to the end of the file to get the size
    file_size = file.tell()
    file.seek(0)  # Reset file pointer after checking size

    try:
        # Validate file metadata with Pydantic
        FileMetadata(filename=file.filename, file_size=file_size)
    except ValidationError:
        return (
            jsonify(
                {
                    "error": "Invalid file type or file size exceeds the maximum size limit"
                }
            ),
            400,
        )

    # Save the file after validation
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    try:
        # Check file extension and convert if it's a PDF
        if filename.lower().endswith(".pdf"):
            # Convert PDF to DOCX
            docx_path = convert_pdf_to_docx(file_path)

            # Parse the DOCX file
            parsed_resume = parse_resume(docx_path)

            # Remove the converted DOCX file
            if os.path.exists(docx_path):
                os.remove(docx_path)
        else:
            # If not a PDF, parse the original file
            parsed_resume = parse_resume(file_path)

        # Clean and parse the resume
        cleaned_resume = parsed_resume.strip()

        # If the cleaned string is empty, raise an error
        if not cleaned_resume:
            raise ValueError("Empty resume parsing result")

        # Try parsing the JSON
        response = json.loads(cleaned_resume)

    except Exception as e:
        return (
            jsonify(
                {
                    "error": f"Error parsing the resume: {str(e)}. Please try again or use another."
                }
            ),
            400,
        )
    finally:
        # Remove the uploaded file after processing
        if os.path.exists(file_path):
            os.remove(file_path)

    return jsonify({"resume_data": response}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
