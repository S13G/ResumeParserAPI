from flask import Flask


def create_app():
    app = Flask(__name__)  # noqa
    return app


app = create_app()
