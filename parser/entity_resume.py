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
REQUIREMENTS:
1.  Do not omit or modify any details in the text parsed to be populated
2.  Make sure you fill in everything that has been passed to you from the resume, DO NOT LEAVE ANYTHING OUT!!
3.  For date, start_date and end_date: If specified, Turn them into A DATETIME ISO format e.g. (2024-12-15T14:30:00+00:00), if only month and year or just year, add the first or last day and month
4.  Also sometimes the headers in the resume may not have correlate with the json keys, so be sure to match them up with the json keys
    e.g. we have "education" key in the json structure, and the resume may have something like "educational accomplishments", so watch out for things like this in the entire resume,
    THIS DOESN'T APPLY TO EDUCATION ALONE, SO MATCH THEM UP PROPERLY.
5.  AGAIN, DO NOT LEAVE OUT ANY DETAIL PASSED TO YOU FROM THE RESUME OR SHORTEN ANYTHING
6.  Sometimes skills may be like this, with no tools specified, make sure you fill it in and leave the tools section blank unless some tools is specified in the summary which you can pass to the tools section of skill in the below JSON STRUCTURE: 
    • Expert in formulating and implementing comprehensive product strategies across key areas, driving
    initiatives from conception to successful launch. Demonstrated ability to develop clear roadmaps and
    delivery milestones that align with both short-term actions and long-term vision.
7.  MAKE SURE YOU FILL IN ALL THE ROLES, ACCOMPLISHMENTS, RESPONSIBILITIES of a work experience indicated in the resume text.
8.  The job description field should take in all the description, roles, responsibilities and accomplishments done on the job, not just description alone, AND PUT THEM IN NEW LINES
    AND DONT JUST PUT newline escape sequence character \n, use a dot instead to separate the responsibilities'
    AND REMOVE THE HEADERS like (Accomplishments and Responsibilities(IF ANY))
8b. BE CAREFUL NOT TO MIX JOB DESCRIPTIONS AND COMPANY DESCRIPTION(which is just talking about the company).
9.  DONT SUMMARIZE THE SKILLS, PARSE IT INTO THE JSON AS GIVEN TO YOU, IF SKILL IS A SUMMARY, PASS IN THE SUMMARY AND TAKE THE TOOLS FROM THE SUMMARY, DO NOT OMIT ANYTHING!!!
    IF THERE IS SUMMARY AFTER THE TOOLS, PARSE IT INTO THE SKILL SUMMARY TOO. AGAIN DONT OMIT ANYTHING!!!.
    An example would be:
    •Proficient with Azure DevOps, JIRA, Figma, Confluence, Bamboo, Wrike, MIRO, Mural, Python, PowerBI,
    Monday.com, Google Analytics, MS Clarity, Clevertap, Hotjar, Google Suite (Drive, Doc, Sheet), MS Office
    365 (Word, Excel, PowerPoint, SharePoint). Proficient in using online collaboration tools (Confluence, Trello,
    Zoom, Slack, and Microsoft Teams).
    
    'AFTER TOOLS HAS BEEN REMOVED. STILL ADD "Proficient in using online collaboration tools (Confluence, Trello,
    Zoom, Slack, and Microsoft Teams)." TO THE SUMMARY.'
    DONT FORGET TO STILL GET THE TOOLS FROM THE SUMMARY AND POPULATE THE TOOLS SECTION IN THE JSON.
10. If no end date for a particular work experience, put 'Present' as the end date. or if you see 'present' or other similar words e.g. 'now' in the resume text, put 'Present' as the end date.

DON'TS:
DONT OMIT ANYTHING PARSED FROM THE RESUME TEXT!!!!!

DATA:
Resume Text: {text}

JSON FORMAT:
{{
    "first_name": "",
    "last_name": "",
    "email": "",
    "linkedin": "",
    "portfolio": "",
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
            "cgpa": "",
            "start_date": "",
            "end_date": ""
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

Ensure all string tags are properly closed, and the output is a valid JSON object. ALWAYS RETURN VALID JSON ONLY.
"""


def parse_resume(filename):
    # Extract text from the PDF
    resume_text = extract_text_from_file(filename)

    # Format the prompt with the resume text
    formatted_prompt = prompt_template.format(text=resume_text)

    # Call the Anthropic API
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=8192,
        messages=[{"role": "user", "content": formatted_prompt}],
    )

    return response.content[0].text
