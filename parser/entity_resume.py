import docx  # noqa
from PyPDF2 import PdfReader
from anthropic import Anthropic
from dotenv import load_dotenv

from parser import create_app

load_dotenv()

app = create_app()

# Access the API key from the environment variable
client = Anthropic(api_key=app.config["ANTHROPIC_API_KEY"])


def extract_text_from_file(file_name):
    """
    Extracts text from PDF, DOC, or DOCX files
    """
    if file_name.lower().endswith(".pdf"):
        reader = PdfReader(file_name)
        return " ".join(page.extract_text() for page in reader.pages)
    elif file_name.lower().endswith((".doc", ".docx")):
        doc = docx.Document(file_name)
        return " ".join(paragraph.text for paragraph in doc.paragraphs)
    else:
        raise ValueError("Unsupported file format. Use PDF or DOCX.")


# Prompt template
prompt_template = """
Extract the following details from the given resume text in a structured JSON format:
{{
    "first_name": "",
    "last_name": "",
    "email": "",
    "linkedin": "",
    "job_title": "",
    "profile_summary": "",
    "skills": [
        {{
        "skill": "",
        "tools": ""
        }}
    ],
    "education": [
        {{
            "degree": "",
            "institution": "",
            "start_year": "",
            "end_year": ""
        }}
    ],
    "work_experience": [
        {{
            "job_title": "",
            "job_description": "",
            "company": "",
            "company_description": "",
            "start_date": "",
            "end_date": "",
            "location": ""
        }}
    ],
    "certifications": [
        {{
          "name": "",
          "code": "",
          "date": ""  
        }}
    ],
    "awards": [],
    "interests": []
}}

Resume Text: {text}
"""


# Main logic
def parse_resume(filename):
    # Extract text from the PDF
    resume_text = extract_text_from_file(filename)

    # Format the prompt with the resume text
    formatted_prompt = prompt_template.format(text=resume_text)

    # Call the Anthropic API
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{"role": "user", "content": formatted_prompt}],
    )

    return response.content[0].text
