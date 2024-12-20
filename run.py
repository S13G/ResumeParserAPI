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
APP_VERSION = "1.0.7"


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
        # Parse the original file
        parsed_resume = parse_resume(file_path)

        # Clean and parse the resume
        cleaned_resume = parsed_resume.strip()

        # If the cleaned string is empty, raise an error
        if not cleaned_resume:
            return (
                jsonify(
                    {
                        "error": f"Error: resume parsing result is empty. Please try again or use another."
                    }
                ),
                400,
            )

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
