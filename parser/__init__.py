import os

from flask import Flask


def create_app():
    app = Flask(__name__)  # noqa
    UPLOAD_FOLDER = "uploads"
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY")
    app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False
    return app


app = create_app()
