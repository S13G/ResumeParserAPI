import json
import os
from json import JSONDecodeError

from dotenv import load_dotenv
from flask import request, jsonify
from pdf2docx import Converter
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


def convert_pdf_to_docx(pdf_path):
    """
    Convert a PDF file to DOCX format using pdf2docx library.
    """
    docx_path = pdf_path.replace(".pdf", ".docx")
    cv = Converter(pdf_path)
    cv.convert(docx_path)  # Converts the whole document
    return docx_path


@app.route("/upload", methods=["POST"])
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

    parsed_resume = parse_resume(file_path)

    try:
        response = json.loads(parsed_resume)
    except JSONDecodeError:
        return (
            jsonify(
                {"error": "Error parsing the resume. Please try again or use another."}
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
