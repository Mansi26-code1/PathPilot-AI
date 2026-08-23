import requests


BASE_URL = "http://127.0.0.1:8000"


def signup(email, password):
    return requests.post(
        f"{BASE_URL}/auth/signup",
        json={
            "email": email,
            "password": password
        }
    )


def login(email, password):
    return requests.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": email,
            "password": password
        }
    )


def upload_resume(token, file):
    return requests.post(
        f"{BASE_URL}/resume/upload",
        headers={
            "Authorization": f"Bearer {token}"
        },
        files={
            "file": (
                file.name,
                file.getvalue()
            )
        }
    )


def get_ats_analysis(token, resume_id):
    return requests.get(
        f"{BASE_URL}/resume/{resume_id}/ats",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )


def match_jd(token, resume_id, jd_text):
    return requests.post(
        f"{BASE_URL}/resume/{resume_id}/match",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "jd_text": jd_text
        }
    )


def ask_mentor(token, resume_id, message):
    """
    Resume ID is optional.

    If resume_id exists:
        Resume-aware mentor

    If resume_id is None:
        General/no-resume mentor
    """

    headers = {
        "Authorization": f"Bearer {token}"
    }

    if resume_id is not None:
        url = f"{BASE_URL}/mentor/{resume_id}"
    else:
        url = f"{BASE_URL}/mentor"

    return requests.post(
        url,
        headers=headers,
        json={
            "message": message
        }
    )


# ============================================================
# LEARNING HUB
# ============================================================

def get_learning_resources(token, question):
    """
    AI/RAG + web search resources.
    Resume is NOT required.
    """

    return requests.post(
        f"{BASE_URL}/learning/resources",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "question": question
        }
    )


def get_learning_history(token):
    """
    Get previous AI learning searches.
    """

    return requests.get(
        f"{BASE_URL}/learning/history",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )


def save_learning_resource(
    token,
    title,
    url,
    skill=None,
    level=None,
    description=None
):
    """
    Save a user-provided learning resource.
    """

    return requests.post(
        f"{BASE_URL}/learning/saved",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": title,
            "url": url,
            "skill": skill,
            "level": level,
            "description": description
        }
    )


def get_saved_learning_resources(token):
    """
    Get resources manually saved by the user.
    """

    return requests.get(
        f"{BASE_URL}/learning/saved",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )


# ============================================================
# SHOULD I APPLY
# ============================================================

def should_i_apply(token, resume_id, jd_text):

    return requests.post(
        f"{BASE_URL}/agent/should-i-apply",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "resume_id": resume_id,
            "jd_text": jd_text
        }
    )