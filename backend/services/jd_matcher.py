import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text: str) -> str:
    """
    Normalize text for comparison.
    """

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9+#.\s-]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# TF-IDF + COSINE SIMILARITY
# ============================================================

def calculate_similarity(
    resume_text: str,
    jd_text: str
):
    """
    Calculate resume-JD text similarity
    using TF-IDF + cosine similarity.
    """

    resume_text = normalize_text(
        resume_text
    )

    jd_text = normalize_text(
        jd_text
    )

    if not resume_text or not jd_text:
        return 0.0

    documents = [
        resume_text,
        jd_text
    ]

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    tfidf_matrix = vectorizer.fit_transform(
        documents
    )

    similarity = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:2]
    )[0][0]

    return round(
        float(similarity) * 100,
        2
    )


# ============================================================
# JD SKILL DICTIONARY
# ============================================================

SKILL_DICTIONARY = [
    "python",
    "sql",
    "java",
    "c++",
    "javascript",
    "typescript",

    "fastapi",
    "flask",
    "django",

    "machine learning",
    "deep learning",
    "data science",

    "scikit-learn",
    "tensorflow",
    "pytorch",

    "xgboost",
    "lightgbm",

    "pandas",
    "numpy",
    "matplotlib",
    "seaborn",
    "librosa",

    # Data-analysis skills commonly present in fresher JDs.
    "eda",
    "exploratory data analysis",
    "data analysis",
    "data cleaning",
    "feature engineering",
    "classification models",
    "evaluation metrics",

    "power bi",
    "tableau",
    "excel",

    "nlp",
    "natural language processing",

    "llm",
    "langchain",
    "langgraph",
    "rag",
    "generative ai",

    "docker",
    "kubernetes",

    "aws",
    "azure",
    "gcp",

    "git",
    "github",
    "mlflow",

    "mongodb",
    "postgresql",
    "mysql",

    "rest api",
    "api"
]


# ============================================================
# SKILL ALIASES
# ============================================================
# Different ways people write the same skill.
# Key = alias, Value = canonical skill name
# (canonical names must match SKILL_DICTIONARY entries)

# Broader skills may be supported by concrete sub-skills in the resume.
# These relationships do NOT add skills to the resume; they only let the
# matcher recognize genuine supporting evidence.
RELATED_SKILLS = {
    "data science": {
        "eda",
        "data analysis",
        "data cleaning",
        "feature engineering",
        "classification models",
        "evaluation metrics",
        "pandas",
        "numpy",
        "machine learning",
        "scikit-learn",
    },
    "machine learning": {
        "classification models",
        "feature engineering",
        "evaluation metrics",
        "scikit-learn",
        "xgboost",
        "lightgbm",
    },
    "deep learning": {
        "tensorflow",
        "pytorch",
    },
    "data analysis": {
        "eda",
        "data cleaning",
        "pandas",
        "numpy",
    },
}


SKILL_ALIASES = {
    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "fast api": "fastapi",
    "ml": "machine learning",
    "dl": "deep learning",
    "natural language processing": "nlp",
    "postgres": "postgresql",
    "js": "javascript",
    "ts": "typescript",
    "power-bi": "power bi",
    "powerbi": "power bi",
    "exploratory data analysis": "eda",
}


def resolve_alias(skill_text: str) -> str:
    """
    Map an alias/variant to its canonical skill name.
    If no alias found, return the normalized text as-is.
    """

    normalized = normalize_text(skill_text)

    return SKILL_ALIASES.get(normalized, normalized)


# ============================================================
# SKILL DETECTION FROM JD
# ============================================================

def detect_jd_skills(jd_text: str):
    """
    Detect known technical skills present in the JD.
    """

    jd_text = normalize_text(
        jd_text
    )

    detected = []

    for skill in SKILL_DICTIONARY:

        skill_normalized = normalize_text(
            skill
        )

        pattern = (
            r"(?<!\w)"
            + re.escape(skill_normalized)
            + r"(?!\w)"
        )

        if re.search(
            pattern,
            jd_text
        ):
            detected.append(
                skill
            )

    return detected


# ============================================================
# RESUME-WIDE SKILL EVIDENCE
# ============================================================
# Instead of only trusting the Skills section, we also search
# for skill-dictionary terms inside Experience/Projects/Summary
# text. This catches cases like "Machine Learning Intern" where
# the skill is demonstrated but not explicitly listed under Skills.

def build_resume_skill_evidence(
    skills_flat: list,
    structured_data: dict
):
    """
    Combine explicit Skills section entries with skills
    detected anywhere else in the resume text (experience,
    projects, summary), using the same SKILL_DICTIONARY.
    """

    evidence = set()

    # 1. Explicit skills section entries
    for skill in skills_flat:
        if skill:
            evidence.add(resolve_alias(skill))

    # 2. Search remaining resume text for skill-dictionary terms
    extra_text_parts = []

    summary = structured_data.get("summary", "")
    if summary:
        extra_text_parts.append(summary)

    for key in ("experience", "projects", "achievements"):
        lines = structured_data.get(key, [])
        extra_text_parts.extend(lines)

    # Experience/projects may be strings OR dictionaries depending on the
    # extractor. Convert everything safely before searching.
    flattened_parts = []
    for part in extra_text_parts:
        if isinstance(part, dict):
            flattened_parts.extend(str(v) for v in part.values() if v)
        elif isinstance(part, list):
            flattened_parts.extend(str(v) for v in part if v)
        elif part:
            flattened_parts.append(str(part))

    combined_text = normalize_text(" ".join(flattened_parts))

    for skill in SKILL_DICTIONARY:
        skill_normalized = normalize_text(skill)

        pattern = (
            r"(?<!\w)"
            + re.escape(skill_normalized)
            + r"(?!\w)"
        )

        if re.search(pattern, combined_text):
            evidence.add(resolve_alias(skill))

    return evidence


# ============================================================
# RELATED-SKILL EVIDENCE
# ============================================================

def has_skill_evidence(jd_skill: str, resume_skill_evidence: set) -> bool:
    """Return True for exact evidence or strong supporting sub-skills."""
    normalized = resolve_alias(jd_skill)

    if normalized in resume_skill_evidence:
        return True

    supporting = RELATED_SKILLS.get(normalized, set())
    if not supporting:
        return False

    # Require at least one concrete supporting skill. For broad domains
    # such as Data Science, two independent signals are stronger.
    matches = supporting.intersection(resume_skill_evidence)
    if normalized == "data science":
        return len(matches) >= 2

    return bool(matches)


# ============================================================
# SKILL MATCH SCORE
# ============================================================

def calculate_skill_match(
    jd_skills: list,
    resume_skill_evidence: set
):
    """
    Calculate percentage of JD skills
    already present in the resume (skills section + full text evidence).
    """

    if not jd_skills:
        return {
            "score": 0.0,
            "matched_count": 0,
            "total_skills": 0
        }

    matched_count = 0

    for jd_skill in jd_skills:
        normalized_jd_skill = resolve_alias(jd_skill)

        if has_skill_evidence(jd_skill, resume_skill_evidence):
            matched_count += 1

    total_skills = len(jd_skills)

    score = (matched_count / total_skills) * 100

    return {
        "score": round(score, 2),
        "matched_count": matched_count,
        "total_skills": total_skills
    }


# ============================================================
# MATCHED + MISSING SKILLS
# ============================================================

def find_skill_gaps(
    jd_skills: list,
    resume_skill_evidence: set
):
    """
    Find matched and missing skills using resume-wide evidence.
    """

    matched_skills = []
    missing_skills = []

    for jd_skill in jd_skills:
        normalized_jd_skill = resolve_alias(jd_skill)

        if has_skill_evidence(jd_skill, resume_skill_evidence):
            matched_skills.append(jd_skill)
        else:
            missing_skills.append(jd_skill)

    return (
        matched_skills,
        missing_skills
    )


# ============================================================
# RECOMMENDATION
# ============================================================

def generate_recommendation(
    overall_score: float
):

    if overall_score >= 80:
        return "Strong match"

    elif overall_score >= 60:
        return (
            "Good match, but some improvements "
            "are recommended"
        )

    elif overall_score >= 40:
        return (
            "Moderate match, several improvements "
            "are needed"
        )

    else:
        return (
            "Low match, significant skill and "
            "resume improvements are needed"
        )


# ============================================================
# MAIN MATCHING FUNCTION
# ============================================================

def match_resume_with_jd(
    resume_text: str,
    jd_text: str,
    resume_skills: list,
    structured_data: dict
):
    """
    Complete resume-JD matching.

    Overall score:
        70% Skill Match
        30% Text Similarity
    """

    # --------------------------------------------------------
    # Edge case: empty or very short JD
    # --------------------------------------------------------

    if not jd_text or len(jd_text.strip()) < 20:
        return {
            "overall_match_score": 0.0,
            "skill_match_score": 0.0,
            "text_similarity_score": 0.0,
            "matched_skills": [],
            "missing_skills": [],
            "jd_skills_detected": [],
            "skill_statistics": {
                "matched": 0,
                "total_jd_skills": 0
            },
            "recommendation": (
                "Job description is too short to analyze. "
                "Please provide a more detailed JD."
            )
        }

    # --------------------------------------------------------
    # 1. TF-IDF text similarity
    # --------------------------------------------------------

    text_similarity_score = calculate_similarity(
        resume_text,
        jd_text
    )

    # --------------------------------------------------------
    # 2. Detect skills from JD
    # --------------------------------------------------------

    jd_skills = detect_jd_skills(
        jd_text
    )

    # --------------------------------------------------------
    # 3. Build resume-wide skill evidence (skills section + text)
    # --------------------------------------------------------

    resume_skill_evidence = build_resume_skill_evidence(
        resume_skills,
        structured_data
    )

    # --------------------------------------------------------
    # 4. Skill matching
    # --------------------------------------------------------

    skill_result = calculate_skill_match(
        jd_skills,
        resume_skill_evidence
    )

    skill_match_score = skill_result["score"]

    # --------------------------------------------------------
    # 5. Matched + missing skills
    # --------------------------------------------------------

    matched_skills, missing_skills = find_skill_gaps(
        jd_skills,
        resume_skill_evidence
    )

    # --------------------------------------------------------
    # 6. Overall score
    # --------------------------------------------------------

    if len(jd_skills) == 0:
        overall_match_score = text_similarity_score
    else:
        overall_match_score = round(
            (skill_match_score * 0.70)
            + (text_similarity_score * 0.30),
            2
        )

    # --------------------------------------------------------
    # 7. Recommendation
    # --------------------------------------------------------

    recommendation = generate_recommendation(
        overall_match_score
    )

    # --------------------------------------------------------
    # 8. Final response
    # --------------------------------------------------------

    return {
        "overall_match_score": overall_match_score,
        "skill_match_score": skill_match_score,
        "text_similarity_score": text_similarity_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "jd_skills_detected": jd_skills,
        "skill_statistics": {
            "matched": skill_result["matched_count"],
            "total_jd_skills": skill_result["total_skills"]
        },
        "recommendation": recommendation
    }