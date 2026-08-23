import re

SECTION_HEADERS = {
    "summary": [
        "summary",
        "objective",
        "profile",
        "about"
    ],

    "education": [
        "education"
    ],

    "skills": [
        "skills",
        "technical skills"
    ],

    "experience": [
        "experience",
        "internship",
        "work experience"
    ],

    "projects": [
        "projects",
        "project"
    ],

    "achievements": [
        "achievement",
        "achievements"
    ]
}


def parse_resume(text: str):

    sections = {}

    current_section = "other"

    sections[current_section] = []

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if line:
            lines.append(line)

    # -----------------------------
    # Personal Information
    # -----------------------------

    name = lines[0] if len(lines) > 0 else ""

    email = ""
    phone = ""
    linkedin = ""
    github = ""

    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    phone_pattern = r'(\+?\d[\d\s\-]{8,}\d)'
    linkedin_pattern = r'linkedin\.com/\S+'
    github_pattern = r'github\.com/\S+'

    for line in lines:

        if email == "":
            match = re.search(email_pattern, line)
            if match:
                email = match.group()

        if phone == "":
            match = re.search(phone_pattern, line)
            if match:
                phone = match.group()

        if linkedin == "":
            match = re.search(linkedin_pattern, line, re.IGNORECASE)
            if match:
                linkedin = match.group().rstrip(".,|")

        if github == "":
            match = re.search(github_pattern, line, re.IGNORECASE)
            if match:
                github = match.group().rstrip(".,|")

    # -----------------------------
    # Section Parsing
    # -----------------------------

    for line in lines:

        lower = line.lower()

        matched = False

        for section, headers in SECTION_HEADERS.items():

            if lower in headers:

                current_section = section

                if current_section not in sections:
                    sections[current_section] = []

                matched = True
                break

        if not matched:
            sections[current_section].append(line)

    return {

        "name": name,
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,

        "summary": sections.get("summary", []),
        "education": sections.get("education", []),
        "skills": sections.get("skills", []),
        "experience": sections.get("experience", []),
        "projects": sections.get("projects", []),
        "achievements": sections.get("achievements", []),
        "other": sections.get("other", [])
    }