import re


ACTION_VERBS = {
    "built", "developed", "created", "implemented", "designed",
    "deployed", "engineered", "analysed", "analyzed", "improved",
    "optimized", "optimised", "managed", "led", "automated",
    "developed", "integrated", "configured", "trained", "evaluated",
    "extracted", "cleaned", "transformed", "processed", "achieved",
    "reduced", "increased", "generated", "handled", "joined"
}


WEAK_PHRASES = {
    "responsible for",
    "worked on",
    "helped with",
    "assisted with",
    "involved in",
    "participated in"
}


STANDARD_SECTIONS = {
    "summary",
    "education",
    "skills",
    "experience",
    "projects",
    "achievements"
}


def count_words(text: str):
    return len(text.split())


def extract_bullets(text: str):
    bullets = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        if line.startswith(("•", "-", "–", "*")):
            bullet = line.lstrip("•-*– ").strip()

            if bullet:
                bullets.append(bullet)

    return bullets


def check_action_verbs(bullets: list):
    if not bullets:
        return {
            "score": 0,
            "total": 20,
            "percentage": 0
        }

    strong_count = 0

    for bullet in bullets:
        words = bullet.lower().split()

        if words and words[0].strip(".,:;") in ACTION_VERBS:
            strong_count += 1

    percentage = (strong_count / len(bullets)) * 100
    score = round((percentage / 100) * 20, 2)

    return {
        "score": score,
        "total": 20,
        "percentage": round(percentage, 2)
    }


def check_quantified_achievements(bullets: list):
    if not bullets:
        return {
            "score": 0,
            "total": 25,
            "percentage": 0
        }

    quantified_count = 0

    number_pattern = re.compile(
        r"\b\d+(\.\d+)?%?\b"
        r"|₹\s?\d+"
        r"|\$\s?\d+"
        r"|\b\d+[KMB]\b",
        re.IGNORECASE
    )

    for bullet in bullets:
        if number_pattern.search(bullet):
            quantified_count += 1

    percentage = (quantified_count / len(bullets)) * 100
    score = round((percentage / 100) * 25, 2)

    return {
        "score": score,
        "total": 25,
        "percentage": round(percentage, 2)
    }


def check_sections(sections: dict):
    present = []

    for section in STANDARD_SECTIONS:
        values = sections.get(section, [])

        if values:
            present.append(section)

    percentage = (len(present) / len(STANDARD_SECTIONS)) * 100
    score = round((percentage / 100) * 20, 2)

    return {
        "score": score,
        "total": 20,
        "percentage": round(percentage, 2),
        "present": present,
        "missing": [
            section
            for section in STANDARD_SECTIONS
            if section not in present
        ]
    }


def check_contact_info(structured_data: dict):
    fields = [
        structured_data.get("email"),
        structured_data.get("phone"),
        structured_data.get("linkedin")
    ]

    present = sum(bool(field) for field in fields)

    percentage = (present / 3) * 100

    return {
        "percentage": round(percentage, 2),
        "present": present,
        "total": 3
    }


def check_keyword_presence(structured_data: dict):
    skills = structured_data.get("skills_flat", [])

    if not skills:
        return {
            "score": 0,
            "total": 20,
            "percentage": 0,
            "skill_count": 0
        }

    # Basic practical threshold:
    # 15+ skills = full score
    percentage = min((len(skills) / 15) * 100, 100)
    score = round((percentage / 100) * 20, 2)

    return {
        "score": score,
        "total": 20,
        "percentage": round(percentage, 2),
        "skill_count": len(skills)
    }


def check_formatting(text: str):
    word_count = count_words(text)

    score = 15
    issues = []

    if word_count < 250:
        score -= 5
        issues.append("Resume may be too short")

    elif word_count > 700:
        score -= 5
        issues.append("Resume may be too long")

    bullet_styles = set()

    for line in text.splitlines():
        line = line.strip()

        if line.startswith("•"):
            bullet_styles.add("•")

        elif line.startswith("-"):
            bullet_styles.add("-")

        elif line.startswith("*"):
            bullet_styles.add("*")

    if len(bullet_styles) > 1:
        score -= 5
        issues.append("Inconsistent bullet formatting")

    return {
        "score": max(score, 0),
        "total": 15,
        "percentage": round((max(score, 0) / 15) * 100, 2),
        "word_count": word_count,
        "issues": issues
    }


def find_weak_phrases(text: str):
    text_lower = text.lower()

    found = []

    for phrase in WEAK_PHRASES:
        if phrase in text_lower:
            found.append(phrase)

    return found


def analyze_ats(text: str, structured_data: dict):
    bullets = extract_bullets(text)

    action_verbs = check_action_verbs(bullets)
    quantified = check_quantified_achievements(bullets)

    sections = check_sections({
        "summary": [structured_data.get("summary")]
        if structured_data.get("summary") else [],

        "education": structured_data.get("education", []),

        "skills": structured_data.get("skills", {}),

        "experience": structured_data.get("experience", []),

        "projects": structured_data.get("projects", []),

        "achievements": structured_data.get("achievements", [])
    })

    keywords = check_keyword_presence(structured_data)
    formatting = check_formatting(text)
    contact = check_contact_info(structured_data)

    weak_phrases = find_weak_phrases(text)

   

    raw_score = (
        action_verbs["score"]
        + quantified["score"]
        + sections["score"]
        + keywords["score"]
        + formatting["score"]
    )

    # Keep final score within 0–100.
    final_score = round(min(raw_score, 100), 2)

    suggestions = []

    if action_verbs["percentage"] < 70:
        suggestions.append(
            "Start more bullet points with strong action verbs."
        )

    if quantified["percentage"] < 50:
        suggestions.append(
            "Add more measurable results such as percentages, counts, or scale."
        )

    if sections["missing"]:
        suggestions.append(
            "Add missing standard resume sections."
        )

    if keywords["skill_count"] < 10:
        suggestions.append(
            "Add relevant technical skills and job-specific keywords."
        )

    if formatting["issues"]:
        suggestions.extend(formatting["issues"])

    if weak_phrases:
        suggestions.append(
            "Replace weak phrases with stronger action-oriented language."
        )

    if not structured_data.get("linkedin"):
        suggestions.append("Add a LinkedIn profile.")

    return {
        "ats_score": final_score,

        "breakdown": {
            "action_verbs": action_verbs,
            "quantified_achievements": quantified,
            "section_completeness": sections,
            "keyword_presence": keywords,
            "formatting_consistency": formatting
        },

        "contact_info": contact,

        "weak_phrases": weak_phrases,

        "suggestions": suggestions
    }