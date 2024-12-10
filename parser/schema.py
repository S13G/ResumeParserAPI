from pydantic import BaseModel, conint, field_validator

from parser import create_app

MAX_FILE_SIZE = 3 * 1024 * 1024

app = create_app()
app.config["ALLOWED_EXTENSIONS"] = {"pdf", "docx", "doc"}


class FileMetadata(BaseModel):
    filename: str
    file_size: conint(le=MAX_FILE_SIZE)

    @field_validator("filename")
    def check_file_extension(cls, filename):
        allowed_extensions = app.config["ALLOWED_EXTENSIONS"]
        file_extension = filename.rsplit(".", 1)[1].lower()

        if file_extension not in allowed_extensions:
            raise ValueError(
                f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
            )

        return filename

    @field_validator("file_size")
    def check_file_size(cls, file_size):
        if file_size > MAX_FILE_SIZE:
            raise ValueError(
                f"File size exceeds the maximum limit of {MAX_FILE_SIZE / (1024 * 1024)} MB."
            )
        return file_size
