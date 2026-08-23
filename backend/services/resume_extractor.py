import re


def extract_name(text: str):
    lines = text.splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if "@" in line:
            continue
        if "linkedin" in line.lower():
            continue
        if "github" in line.lower():
            continue
        if len(line.split()) <= 4:
            return line
    return None


def extract_email(text: str):
    match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return match.group(0) if match else None


def extract_phone(text: str):
    match = re.search(r"(\+91[- ]?)?[6-9]\d{9}", text)
    return match.group(0) if match else None


def extract_skills(skills_lines: list):
    """
    Input: ['Languages: Python, SQL', 'ML & Libraries: Scikit-learn, XGBoost, ...']
    Output: {'Languages': ['Python', 'SQL'], 'ML & Libraries': ['Scikit-learn', 'XGBoost', ...]}
    """
    skills_dict = {}
    for line in skills_lines:
        if ":" in line:
            category, items = line.split(":", 1)
            skill_list = [s.strip() for s in items.split(",") if s.strip()]
            skills_dict[category.strip()] = skill_list
        else:
            skills_dict.setdefault("Other", []).extend(
                [s.strip() for s in line.split(",") if s.strip()]
            )
    return skills_dict


def extract_flat_skills(skills_lines: list):
    """Ek flat list ke liye — TF-IDF/matching ke liye useful hoga Phase 3 me"""
    skills_dict = extract_skills(skills_lines)
    flat = []
    for category_skills in skills_dict.values():
        flat.extend(category_skills)
    return flat


def extract_resume(text: str, sections: dict):
    """
    text: raw cleaned resume text (name/email/phone nikalne ke liye)
    sections: parse_resume() se aaya dict (summary/education/skills/etc ki lists)
    """
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "linkedin": sections.get("linkedin", ""),
        "github": sections.get("github", ""),

        "summary": " ".join(sections.get("summary", [])),
        "education": sections.get("education", []),
        "skills": extract_skills(sections.get("skills", [])),
        "skills_flat": extract_flat_skills(sections.get("skills", [])),
        "experience": sections.get("experience", []),
        "projects": sections.get("projects", []),
        "achievements": sections.get("achievements", [])
    }