import os

from flask import request, jsonify
from werkzeug.utils import secure_filename

from parser import create_app
from parser.entity_resume import ResumeParser

app = create_app()

# Define upload folder
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["ALLOWED_EXTENSIONS"] = {"pdf"}


def allowed_file(filename):
    return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


@app.route("/upload", methods=["POST"])
def upload_cv():
    # Ensure the upload folder exists
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    """Handles file upload and CV processing."""
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)

        try:
            # Process the uploaded file using ResumeParser
            resume_parser = ResumeParser(file_path)
            parsed_data = resume_parser.parse_cv()

            # Send the parsed data as a response
            response = jsonify(parsed_data)
        finally:
            # Delete the uploaded file after processing
            if os.path.exists(file_path):
                os.remove(file_path)

        return response

    return jsonify({"error": "Invalid file type"}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
