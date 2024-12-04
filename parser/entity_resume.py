import re

import PyPDF2


class ResumeParser:
    def __init__(self, filename):
        self.filename = filename
        self._resume_text = None

    def extract_text(self):
        """Extracts text from the PDF and caches it."""
        if self._resume_text is None:
            with open(self.filename, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)

                # Extract text from all pages and normalize newlines
                self._resume_text = " ".join(
                    page.extract_text() for page in pdf_reader.pages
                )
                # Replace multiple spaces or newlines with a single space
                self._resume_text = re.sub(r"\s+", " ", self._resume_text).strip()
        return self._resume_text

    def parse_cv(self):
        """Parses the CV and structures the data into sections."""
        headers = {
            "profile": ["PROFILE", "SUMMARY", "ABOUT ME", "BRIEF SUMMARY"],
            "skills": ["SKILLS"],
            "experience": [
                "EXPERIENCE",
                "WORK EXPERIENCE",
                "PROFESSIONAL EXPERIENCE",
                "VOLUNTARY EXPERIENCE",
            ],
            "education": ["EDUCATION"],
            "certificates": ["CERTIFICATES", "AWARDS", "CERTIFICATES AND AWARDS"],
            "interests": ["INTERESTS", "HOBBIES"],
            "projects": ["PROJECTS"],
        }

        result = {
            "name": "",
            "email": "",
            "linkedin": "",
            "address": "",
            "job_role": "",
            "profile": "",
            "skills": [],
            "experience": [],
            "education": "",
            "certificates": [],
            "interests": "",
            "projects": [],
        }

        # Extract clean text
        text = self.extract_text()

        # Extract email
        email_match = re.search(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text
        )
        if email_match:
            result["email"] = email_match.group(0)

        # Extract LinkedIn URL
        linkedin_match = re.search(r"https?://(www\.)?linkedin\.com[^\s]+", text)

        if linkedin_match:
            result["linkedin"] = linkedin_match.group(0)

        # Extract name from the meaningful top lines
        name_lines = []
        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip() and line.strip() != "."
        ]  # Remove blank lines and dots

        if lines:  # Ensure there are meaningful lines
            # Split the first meaningful line into words
            words = lines[0].split()
            if len(words) >= 2:  # Ensure there are at least two words
                name_lines.append(
                    " ".join(words[:2])
                )  # Use the first two words as the name

        result["name"] = " ".join(name_lines)

        # Identify sections and extract their content
        section_positions = {}
        for header, keywords in headers.items():
            for keyword in keywords:
                match = re.search(rf"\b{keyword}\b", text, re.IGNORECASE)
                if match:
                    section_positions[header] = match.start()

        # Sort headers by position in the text
        sorted_sections = sorted(section_positions.items(), key=lambda x: x[1])

        # Extract content between headers
        for i, (header, start_pos) in enumerate(sorted_sections):
            end_pos = (
                sorted_sections[i + 1][1] if i + 1 < len(sorted_sections) else len(text)
            )
            section_content = text[start_pos:end_pos].strip()

            # Remove the header itself from the content
            for keyword in headers.get(header, []):
                section_content = re.sub(
                    rf"\b{keyword}\b", "", section_content, flags=re.IGNORECASE
                ).strip()

            # Assign the content to the corresponding result key
            if header == "skills":
                result[header] = [
                    skill.strip()
                    for skill in section_content.split(",")
                    if skill.strip()
                ]
            elif header in ["experience", "projects"]:
                result[header] = [
                    line.strip() for line in section_content.split(". ") if line.strip()
                ]
            else:
                result[header] = section_content

        # Extract job role: Look for job titles in the profile and experience sections
        job_role_keywords = [
            "developer",
            "engineer",
            "designer",
            "manager",
            "lead",
            "specialist",
            "sales",
            "principal",
            "software",
        ]

        # Check in the profile section
        profile_section = result.get("profile", "")
        if not result["job_role"]:  # Only set if not already extracted
            for keyword in job_role_keywords:
                if re.search(rf"\b{keyword}\b", profile_section, re.IGNORECASE):
                    # Get the word before the job title (e.g., Software Engineer)
                    match = re.search(
                        rf"(\w+)\s+{keyword}", profile_section, re.IGNORECASE
                    )
                    if match:
                        result["job_role"] = f"{match.group(1)} {keyword}".capitalize()
                    else:
                        result["job_role"] = (
                            keyword.capitalize()
                        )  # Just use the keyword if no match
                    break

        # Check in the experience section
        if not result["job_role"]:  # Only set if not already extracted
            experience_section = result.get("experience", [])
            for line in experience_section:
                for keyword in job_role_keywords:
                    if re.search(rf"\b{keyword}\b", line, re.IGNORECASE):
                        # Get the word before the job title (e.g., Software Engineer)
                        match = re.search(rf"(\w+)\s+{keyword}", line, re.IGNORECASE)
                        if match:
                            result["job_role"] = (
                                f"{match.group(1)} {keyword}".capitalize()
                            )
                        else:
                            result["job_role"] = (
                                keyword.capitalize()
                            )  # Just use the keyword if no match
                        break
                if result["job_role"]:
                    break

        return result
