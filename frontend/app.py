import streamlit as st

from utils.api_client import (
    signup,
    login,
    upload_resume,
    get_ats_analysis,
    match_jd,
    ask_mentor,
    get_learning_resources,
    get_learning_history,
    save_learning_resource,
    get_saved_learning_resources,
    should_i_apply,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="PathPilot AI",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ======================================================
       GLOBAL
       ====================================================== */

    .stApp {
        background: #0b1020;
        color: #f5f7fb;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 1.6rem;
        padding-bottom: 3rem;
    }

    h1,
    h2,
    h3,
    h4 {
        color: #f8fafc !important;
    }

    p,
    label,
    span {
        color: #cbd5e1;
    }

    /* ======================================================
       SIDEBAR
       ====================================================== */

    section[data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid #243047;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1.2rem;
    }

    /* ======================================================
       BUTTONS
       ====================================================== */

    .stButton > button,
    .stLinkButton > a {
        border-radius: 10px;
        border: 1px solid #334155;
        background: #172033;
        color: #f8fafc;
        font-weight: 600;
        transition: all 0.18s ease;
    }

    .stButton > button:hover,
    .stLinkButton > a:hover {
        border-color: #6366f1;
        background: #202a44;
        color: #ffffff;
    }

    /* ======================================================
       INPUTS
       ====================================================== */

    .stTextInput input,
    .stTextArea textarea {
        background: #111827 !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
    }

    .stSelectbox [data-baseweb="select"] > div {
        background: #111827 !important;
        border-color: #334155 !important;
    }

    /* ======================================================
       CARDS
       ====================================================== */

    .pp-card {
        background: #111827;
        border: 1px solid #243047;
        border-radius: 16px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }

    .pp-card-title {
        font-size: 1rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 0.35rem;
    }

    .pp-card-text {
        color: #94a3b8;
        font-size: 0.9rem;
        line-height: 1.55;
    }

    /* ======================================================
       HERO
       ====================================================== */

    .hero {
        background:
            radial-gradient(
                circle at top right,
                rgba(99, 102, 241, 0.25),
                transparent 42%
            ),
            #111827;

        border: 1px solid #263452;
        border-radius: 20px;
        padding: 1.7rem 2rem;
        margin-bottom: 1.5rem;
    }

    .hero-title {
        font-size: 2.15rem;
        font-weight: 800;
        color: #f8fafc;
        margin-bottom: 0.45rem;
    }

    .hero-subtitle {
        color: #94a3b8;
        font-size: 1rem;
    }

    /* ======================================================
       METRICS
       ====================================================== */

    .metric-card {
        background: #111827;
        border: 1px solid #263452;
        border-radius: 15px;
        padding: 1.15rem;
        min-height: 105px;
    }

    .metric-label {
        color: #94a3b8;
        font-size: 0.82rem;
    }

    .metric-value {
        color: #f8fafc;
        font-size: 1.75rem;
        font-weight: 800;
        margin-top: 0.25rem;
    }

    /* ======================================================
       TAGS
       ====================================================== */

    .tag {
        display: inline-block;
        padding: 0.35rem 0.7rem;
        margin: 0.2rem;
        border-radius: 20px;
        background: #1e293b;
        border: 1px solid #334155;
        color: #cbd5e1;
        font-size: 0.8rem;
    }

    .status-pill {
        display: inline-block;
        padding: 0.38rem 0.75rem;
        border-radius: 20px;
        background: #172033;
        border: 1px solid #334155;
        color: #cbd5e1;
        font-size: 0.8rem;
    }

    .score-good {
        color: #86efac;
        font-weight: 800;
    }

    .score-mid {
        color: #facc15;
        font-weight: 800;
    }

    .score-low {
        color: #fb7185;
        font-weight: 800;
    }

    .small-muted {
        color: #94a3b8;
        font-size: 0.85rem;
    }

    /* ======================================================
       MENTOR CHAT
       ====================================================== */

    [data-testid="stChatMessage"] {
        border: 1px solid #263452;
        border-radius: 14px;
        margin-bottom: 0.7rem;
        background: #111827;
        padding: 0.9rem 1rem;
    }

    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li,
    [data-testid="stChatMessage"] span,
    [data-testid="stChatMessage"] div {
        color: #e2e8f0 !important;
        line-height: 1.65;
    }

    [data-testid="stChatMessage"] h1,
    [data-testid="stChatMessage"] h2,
    [data-testid="stChatMessage"] h3,
    [data-testid="stChatMessage"] h4 {
        color: #93c5fd !important;
    }

    [data-testid="stChatMessage"] strong {
        color: #f8fafc !important;
    }

    [data-testid="stChatInput"] textarea {
        background: #111827 !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
    }

    /* ======================================================
       STREAMLIT METRICS
       ====================================================== */

    div[data-testid="stMetric"] {
        background: #111827;
        border: 1px solid #263452;
        border-radius: 14px;
        padding: 0.75rem;
    }

    div[data-testid="stMetric"] label {
        color: #94a3b8 !important;
    }

    div[data-testid="stMetric"] div {
        color: #f8fafc !important;
    }

    hr {
        border-color: #263452 !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

def init_state():
    defaults = {
        "access_token": None,
        "user_email": None,
        "resume_id": None,
        "mentor_chat": [],
        "mentor_pending_question": None,
        "last_ats": None,
        "last_match": None,
        "last_apply": None,
        "workspace": "Dashboard",
        "last_structured_profile": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()


# ============================================================
# GENERIC HELPERS
# ============================================================

def safe_json(response):
    try:
        return response.json()
    except Exception:
        return {}


def show_error(response, prefix="Request failed"):
    if response is None:
        st.error(f"{prefix}. No response received.")
        return

    data = safe_json(response)

    if isinstance(data, dict):
        detail = data.get(
            "detail",
            data.get(
                "message",
                response.text,
            ),
        )
    else:
        detail = response.text

    st.error(f"{prefix}: {detail}")


def display_tags(items):
    if not items:
        st.caption("None identified.")
        return

    if not isinstance(items, list):
        items = [items]

    html_parts = []

    for item in items:
        if isinstance(item, dict):
            value = (
                item.get("name")
                or item.get("skill")
                or item.get("title")
                or str(item)
            )
        else:
            value = str(item)

        html_parts.append(
            f'<span class="tag">{value}</span>'
        )

    st.markdown(
        "".join(html_parts),
        unsafe_allow_html=True,
    )


def reset_session():
    keys = list(st.session_state.keys())

    for key in keys:
        del st.session_state[key]

    init_state()


def go_to(page_name):
    st.session_state.workspace = page_name
    st.rerun()


def score_class(score):
    try:
        score = float(score)
    except Exception:
        return ""

    if score >= 75:
        return "score-good"

    if score >= 50:
        return "score-mid"

    return "score-low"


# ============================================================
# RESUME PROFILE DISPLAY
# ============================================================

def render_profile_value(value):
    """
    Safely display extracted resume values.
    """

    if value is None:
        return

    if isinstance(value, str):
        if value.strip():
            st.write(value)
        return

    if isinstance(value, list):
        if not value:
            return

        for item in value:
            if isinstance(item, dict):
                st.markdown(
                    f"- {item.get('title', item.get('name', str(item)))}"
                )
            else:
                st.markdown(f"- {item}")

        return

    if isinstance(value, dict):
        for key, item in value.items():
            clean_key = str(key).replace("_", " ").title()

            if isinstance(item, (list, dict)):
                st.markdown(f"**{clean_key}**")
                render_profile_value(item)
            else:
                st.markdown(
                    f"**{clean_key}:** {item}"
                )

        return

    st.write(str(value))


def render_structured_profile(profile):
    """
    Render extracted resume information in a clean,
    user-friendly format instead of dumping the entire JSON.
    """

    if not isinstance(profile, dict):
        st.info("Profile information is available.")
        return

    # --------------------------------------------------------
    # BASIC INFORMATION
    # --------------------------------------------------------

    name = profile.get("name")
    email = profile.get("email")
    phone = profile.get("phone")
    linkedin = profile.get("linkedin")
    github = profile.get("github")

    if any([name, email, phone, linkedin, github]):

        st.markdown("### 👤 Candidate profile")

        c1, c2 = st.columns(2)

        with c1:
            if name:
                st.markdown(f"**Name:** {name}")

            if email:
                st.markdown(f"**Email:** {email}")

            if phone:
                st.markdown(f"**Phone:** {phone}")

        with c2:
            if linkedin:
                st.markdown(f"**LinkedIn:** {linkedin}")

            if github:
                st.markdown(f"**GitHub:** {github}")

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    summary = profile.get("summary")

    if summary:
        st.markdown("### 📝 Professional summary")
        st.write(summary)

    # --------------------------------------------------------
    # EDUCATION
    # --------------------------------------------------------

    education = profile.get("education")

    if education:
        st.markdown("### 🎓 Education")
        render_profile_value(education)

    # --------------------------------------------------------
    # SKILLS
    # --------------------------------------------------------

    skills = profile.get("skills")

    if skills:
        st.markdown("### 🛠 Skills")

        if isinstance(skills, dict):

            for category, values in skills.items():

                st.markdown(
                    f"**{str(category).replace('_', ' ').title()}**"
                )

                if isinstance(values, list):
                    display_tags(values)
                else:
                    display_tags([values])

        elif isinstance(skills, list):
            display_tags(skills)

        else:
            display_tags([skills])

    # --------------------------------------------------------
    # EXPERIENCE
    # --------------------------------------------------------

    experience = profile.get("experience")

    if experience:
        st.markdown("### 💼 Experience")
        render_profile_value(experience)

    # --------------------------------------------------------
    # PROJECTS
    # --------------------------------------------------------

    projects = profile.get("projects")

    if projects:
        st.markdown("### 🚀 Projects")
        render_profile_value(projects)

    # --------------------------------------------------------
    # ACHIEVEMENTS
    # --------------------------------------------------------

    achievements = profile.get("achievements")

    if achievements:
        st.markdown("### 🏆 Achievements")
        render_profile_value(achievements)

    # --------------------------------------------------------
    # EXTRA DETAILS
    # --------------------------------------------------------

    known_keys = {
        "name",
        "email",
        "phone",
        "linkedin",
        "github",
        "summary",
        "education",
        "skills",
        "experience",
        "projects",
        "achievements",
    }

    extra_data = {
        key: value
        for key, value in profile.items()
        if key not in known_keys
        and value not in [None, "", [], {}]
    }

    if extra_data:
        with st.expander("View additional resume details"):
            st.json(extra_data)


# ============================================================
# MENTOR RESPONSE NORMALIZATION
# ============================================================

def format_dict_item(item):
    """
    Convert structured mentor dictionaries into readable text.
    """

    if not isinstance(item, dict):
        return str(item)

    preferred_keys = [
        "title",
        "name",
        "role",
        "step",
        "skill",
        "topic",
        "recommendation",
        "reason",
        "why",
        "description",
        "action",
        "priority",
    ]

    parts = []

    for key in preferred_keys:
        value = item.get(key)

        if value is None or value == "":
            continue

        label = key.replace("_", " ").title()

        if isinstance(value, list):
            value = ", ".join(
                str(v) for v in value
            )

        elif isinstance(value, dict):
            value = str(value)

        parts.append(
            f"**{label}:** {value}"
        )

    if parts:
        return " — ".join(parts)

    return str(item)


def extract_mentor_text(raw):
    """
    Convert all known mentor backend response formats
    into stable, readable Markdown.
    """

    if raw is None:
        return ""

    if isinstance(raw, str):
        return raw.strip()

    if not isinstance(raw, dict):
        return str(raw)

    result = raw.get(
        "mentor_response",
        raw,
    )

    if isinstance(result, str):
        return result.strip()

    if not isinstance(result, dict):
        return str(result)

    parts = []

    # --------------------------------------------------------
    # DIRECT RESPONSE
    # --------------------------------------------------------

    direct_keys = [
        "quick_answer",
        "answer",
        "response",
        "message",
        "final_answer",
    ]

    # IMPORTANT: quick_answer must not hide the structured response.
    # The mentor backend can return quick_answer + roadmap + skill gaps
    # in the same response. Display the quick answer and continue parsing
    # the structured fields below.
    quick_answer = result.get("quick_answer")

    if quick_answer and isinstance(quick_answer, str):
        parts.append(
            f"### 💬 Mentor answer\n\n{quick_answer.strip()}"
        )

    # Support alternate direct-answer fields as a fallback.
    if not quick_answer:
        for key in direct_keys:
            value = result.get(key)

            if value and isinstance(value, str):
                parts.append(
                    f"### 💬 Mentor answer\n\n{value.strip()}"
                )
                break

    # --------------------------------------------------------
    # CURRENT ASSESSMENT
    # --------------------------------------------------------

    assessment = result.get(
        "current_assessment"
    )

    if assessment:
        parts.append(
            f"### 🎯 Current assessment\n\n{assessment}"
        )

    # --------------------------------------------------------
    # CAREER RECOMMENDATIONS
    # --------------------------------------------------------

    careers = result.get(
        "career_recommendations",
        [],
    )

    if careers:
        lines = [
            "### 💼 Career recommendations"
        ]

        if not isinstance(careers, list):
            careers = [careers]

        for career in careers:

            if isinstance(career, dict):

                role = career.get(
                    "role",
                    career.get(
                        "title",
                        "Recommended role",
                    ),
                )

                fit = career.get(
                    "fit",
                    "",
                )

                why = career.get(
                    "why",
                    career.get(
                        "reason",
                        "",
                    ),
                )

                line = f"- **{role}**"

                if fit:
                    line += f" — {fit}"

                lines.append(line)

                if why:
                    lines.append(
                        f"  - {why}"
                    )

            else:
                lines.append(
                    f"- {career}"
                )

        parts.append(
            "\n".join(lines)
        )

    # --------------------------------------------------------
    # STRENGTHS
    # --------------------------------------------------------

    strengths = result.get(
        "strengths",
        [],
    )

    if strengths:
        lines = [
            "### 💪 Strengths"
        ]

        if not isinstance(strengths, list):
            strengths = [strengths]

        for item in strengths:
            lines.append(
                f"- {format_dict_item(item)}"
            )

        parts.append(
            "\n".join(lines)
        )

    # --------------------------------------------------------
    # SKILL GAPS
    # --------------------------------------------------------

    skill_gaps = result.get(
        "skill_gaps",
        [],
    )

    if skill_gaps:
        lines = [
            "### 📌 Skill gaps"
        ]

        if not isinstance(skill_gaps, list):
            skill_gaps = [skill_gaps]

        for item in skill_gaps:
            lines.append(
                f"- {format_dict_item(item)}"
            )

        parts.append(
            "\n".join(lines)
        )

    # --------------------------------------------------------
    # INTERVIEW PREPARATION
    # --------------------------------------------------------

    interview = result.get(
        "interview_preparation",
        [],
    )

    if interview:
        lines = [
            "### 🎤 Interview preparation"
        ]

        if not isinstance(interview, list):
            interview = [interview]

        for item in interview:
            lines.append(
                f"- {format_dict_item(item)}"
            )

        parts.append(
            "\n".join(lines)
        )

    # --------------------------------------------------------
    # NEXT STEPS
    # --------------------------------------------------------

    next_steps = result.get(
        "next_steps",
        [],
    )

    if next_steps:
        lines = [
            "### 🚀 Next steps"
        ]

        if not isinstance(next_steps, list):
            next_steps = [next_steps]

        for item in next_steps:
            lines.append(
                f"- {format_dict_item(item)}"
            )

        parts.append(
            "\n".join(lines)
        )

    # --------------------------------------------------------
    # QUESTIONS
    # --------------------------------------------------------

    questions = result.get(
        "questions",
        [],
    )

    if questions:
        lines = [
            "### ❓ Questions for you"
        ]

        if not isinstance(questions, list):
            questions = [questions]

        for item in questions:
            lines.append(
                f"- {format_dict_item(item)}"
            )

        parts.append(
            "\n".join(lines)
        )

    # --------------------------------------------------------
    # ROADMAP
    # --------------------------------------------------------

    roadmap = result.get(
        "roadmap",
        [],
    )

    if roadmap:
        lines = [
            "### 🗺️ Roadmap"
        ]

        if not isinstance(roadmap, list):
            roadmap = [roadmap]

        for index, step in enumerate(
            roadmap,
            1,
        ):

            if isinstance(step, dict):

                name = step.get(
                    "step",
                    step.get(
                        "title",
                        f"Step {index}",
                    ),
                )

                priority = step.get(
                    "priority",
                    "",
                )

                reason = step.get(
                    "reason",
                    "",
                )

                line = (
                    f"{index}. **{name}**"
                )

                if priority:
                    line += (
                        f" — Priority: {priority}"
                    )

                lines.append(line)

                if reason:
                    lines.append(
                        f"   - {reason}"
                    )

            else:
                lines.append(
                    f"{index}. {step}"
                )

        parts.append(
            "\n".join(lines)
        )

    # --------------------------------------------------------
    # FINAL FALLBACK
    # --------------------------------------------------------

    if not parts:
        return (
            "I received a response from the mentor, "
            "but it was not in a format I could display "
            "cleanly. Please try asking the question again."
        )

    return "\n\n".join(parts).strip()


# ============================================================
# MENTOR API
# ============================================================

def ask_mentor_question(user_input):
    """
    Stable wrapper around mentor API.
    """

    try:
        response = ask_mentor(
            st.session_state.access_token,
            st.session_state.resume_id,
            user_input,
        )

    except Exception as exc:
        return (
            None,
            None,
            f"Mentor connection error: {exc}",
        )

    if response.status_code != 200:
        return (
            None,
            response,
            None,
        )

    raw = safe_json(response)

    display_text = extract_mentor_text(raw)

    if not display_text:
        display_text = (
            "I couldn't generate a useful response "
            "right now. Please try asking the question again."
        )

    return (
        display_text,
        response,
        None,
    )


# ============================================================
# LOGIN / SIGNUP
# ============================================================

if st.session_state.access_token is None:

    st.markdown(
        """
        <div
            style="
                text-align:center;
                padding-top:3.2rem;
            "
        >
        <div
                style="
                    font-size:3.3rem;
                    font-weight:800;
                    color:#f8fafc;
                "
            >
                🧭 PathPilot AI
        </div>

        <div
                style="
                    color:#94a3b8;
                    font-size:1.05rem;
                    margin-top:.45rem;
                "
            >
                Your AI-powered career companion
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    _, center, _ = st.columns(
        [1, 1.2, 1]
    )

    with center:

        tab_login, tab_signup = st.tabs(
            [
                "Sign in",
                "Create account",
            ]
        )

        # ----------------------------------------------------
        # LOGIN
        # ----------------------------------------------------

        with tab_login:

            st.markdown(
                "### Welcome back"
            )

            st.caption(
                "Sign in to continue your career journey."
            )

            email = st.text_input(
                "Email",
                key="login_email",
                placeholder="you@example.com",
            )

            password = st.text_input(
                "Password",
                type="password",
                key="login_password",
            )

            if st.button(
                "Sign in →",
                use_container_width=True,
                key="login_button",
            ):

                if (
                    not email.strip()
                    or not password
                ):
                    st.warning(
                        "Please enter your email and password."
                    )

                else:

                    with st.spinner(
                        "Signing you in..."
                    ):

                        try:
                            response = login(
                                email.strip(),
                                password,
                            )

                        except Exception as exc:

                            st.error(
                                f"Login request failed: {exc}"
                            )

                            response = None

                    if response is not None:

                        if response.status_code == 200:

                            data = safe_json(
                                response
                            )

                            token = data.get(
                                "access_token"
                            )

                            if token:

                                st.session_state.access_token = token
                                st.session_state.user_email = email.strip()

                                st.rerun()

                            else:

                                st.error(
                                    "Login succeeded but no access token was returned."
                                )

                        else:

                            show_error(
                                response,
                                "Login failed",
                            )

        # ----------------------------------------------------
        # SIGNUP
        # ----------------------------------------------------

        with tab_signup:

            st.markdown(
                "### Create your account"
            )

            st.caption(
                "Start building your personalized AI career roadmap."
            )

            email = st.text_input(
                "Email",
                key="signup_email",
                placeholder="you@example.com",
            )

            password = st.text_input(
                "Password",
                type="password",
                key="signup_password",
            )

            if st.button(
                "Create account →",
                use_container_width=True,
                key="signup_button",
            ):

                if (
                    not email.strip()
                    or not password
                ):
                    st.warning(
                        "Please enter your email and password."
                    )

                else:

                    with st.spinner(
                        "Creating your account..."
                    ):

                        try:
                            response = signup(
                                email.strip(),
                                password,
                            )

                        except Exception as exc:

                            st.error(
                                f"Signup request failed: {exc}"
                            )

                            response = None

                    if response is not None:

                        if response.status_code in (
                            200,
                            201,
                        ):

                            st.success(
                                "Account created successfully. "
                                "You can now sign in."
                            )

                        else:

                            show_error(
                                response,
                                "Signup failed",
                            )

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div
            style="
                font-size:1.45rem;
                font-weight:800;
                color:#f8fafc;
            "
        >
            🧭 PathPilot AI
        </div>

        <div
            style="
                color:#64748b;
                font-size:.8rem;
                margin-bottom:1.4rem;
            "
        >
            AI Career Companion
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="pp-card">

        <div class="pp-card-text">
                Signed in as
        </div>

        <div class="pp-card-title">
                {st.session_state.user_email}
        </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    pages = [
        "Dashboard",
        "Resume",
        "ATS & JD Match",
        "AI Mentor",
        "Learning Hub",
        "Should I Apply?",
    ]

    page = st.radio(
        "Workspace",
        pages,
        index=(
            pages.index(
                st.session_state.workspace
            )
            if st.session_state.workspace in pages
            else 0
        ),
        label_visibility="collapsed",
    )

    # Store navigation separately from Streamlit widget state.
    # This prevents the "session_state.workspace cannot be modified"
    # exception when dashboard buttons call go_to().
    if page != st.session_state.workspace:
        st.session_state.workspace = page

    st.divider()

    if st.session_state.resume_id:

        st.markdown(
            '<div class="status-pill">'
            '✓ Resume connected'
            '</div>',
            unsafe_allow_html=True,
        )

    else:

        st.markdown(
            '<div class="status-pill">'
            '○ Resume not uploaded'
            '</div>',
            unsafe_allow_html=True,
        )

    st.write("")

    if st.button(
        "Logout",
        use_container_width=True,
    ):

        reset_session()
        st.rerun()


# ============================================================
# PAGE HERO
# ============================================================

st.markdown(
    f"""
    <div class="hero">

    <div class="hero-title">
            {page}
    </div>

    <div class="hero-subtitle">
            Build your skills, improve your resume,
            and make smarter career decisions with AI.
    </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    st.markdown(
        "### Welcome back 👋"
    )

    st.caption(
        "Here's a quick overview of your PathPilot workspace."
    )

    st.write("")

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        value = (
            f"{st.session_state.last_ats}/100"
            if st.session_state.last_ats is not None
            else "—"
        )

        st.markdown(
            f"""
            <div class="metric-card">

            <div class="metric-label">
                    ATS Score
            </div>

            <div class="metric-value">
                    {value}
            </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:

        value = (
            f"{st.session_state.last_match}%"
            if st.session_state.last_match is not None
            else "—"
        )

        st.markdown(
            f"""
            <div class="metric-card">

            <div class="metric-label">
                    Latest Job Match
            </div>

            <div class="metric-value">
                    {value}
            </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:

        value = (
            "Uploaded"
            if st.session_state.resume_id
            else "Pending"
        )

        st.markdown(
            f"""
            <div class="metric-card">

            <div class="metric-label">
                    Resume
            </div>

            <div
                    class="metric-value"
                    style="font-size:1.3rem;"
                >
                    {value}
            </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with c4:

        mentor_count = len(
            st.session_state.mentor_chat
        )

        st.markdown(
            f"""
            <div class="metric-card">

            <div class="metric-label">
                    Mentor Messages
            </div>

            <div class="metric-value">
                    {mentor_count}
             </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    st.markdown(
        "### Quick actions"
    )

    q1, q2, q3 = st.columns(3)

    with q1:

        st.markdown(
            """
            <div class="pp-card">

            <div class="pp-card-title">
                    📄 Resume Analysis
            </div>

            <div class="pp-card-text">
                    Upload your resume and run ATS analysis.
            </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Open Resume",
            key="quick_resume",
            use_container_width=True,
        ):
            go_to("Resume")

    with q2:

        st.markdown(
            """
            <div class="pp-card">

            <div class="pp-card-title">
                    🎯 Analyze a Job
            </div>

            <div class="pp-card-text">
                    Check ATS quality and compare your resume with a JD.
            </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Open Job Analysis",
            key="quick_job",
            use_container_width=True,
        ):
            go_to("ATS & JD Match")

    with q3:

        st.markdown(
            """
            <div class="pp-card">

            <div class="pp-card-title">
                    🤖 Ask your Mentor
            </div>

            <div class="pp-card-text">
                    Have a conversational AI career discussion.
            </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Open Mentor",
            key="quick_mentor",
            use_container_width=True,
        ):
            go_to("AI Mentor")

    if not st.session_state.resume_id:

        st.info(
            "Start by uploading your resume. "
            "PathPilot can then personalize your career analysis."
        )

    else:

        st.success(
            "Your resume is connected. "
            "You can now analyze jobs and use the personalized mentor."
        )


# ============================================================
# RESUME
# ============================================================

elif page == "Resume":

    st.markdown(
        "### Build your career profile"
    )

    st.caption(
        "Upload a PDF or DOCX. "
        "The backend extraction pipeline will process it."
    )

    uploaded_file = st.file_uploader(
        "Upload your resume",
        type=[
            "pdf",
            "docx",
        ],
        help="PDF and DOCX are supported.",
        key="resume_uploader",
    )

    if uploaded_file:

        st.markdown(
            f"""
            <div class="pp-card">

            <div class="pp-card-title">
                    📄 {uploaded_file.name}
            </div>

            <div class="pp-card-text">
                    Ready for analysis
            </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Analyze & Upload Resume →",
            use_container_width=True,
            key="upload_resume_button",
        ):

            with st.spinner(
                "Extracting and analyzing your resume..."
            ):

                try:

                    response = upload_resume(
                        st.session_state.access_token,
                        uploaded_file,
                    )

                except Exception as exc:

                    st.error(
                        f"Resume upload request failed: {exc}"
                    )

                    response = None

            if response is not None:

                if response.status_code == 200:

                    data = safe_json(
                        response
                    )

                    resume_id = data.get(
                        "resume_id"
                    )

                    if resume_id is not None:

                        st.session_state.resume_id = resume_id

                    structured_data = data.get(
                        "structured_data"
                    )

                    if structured_data:

                        st.session_state.last_structured_profile = structured_data

                        st.success(
                            "Resume successfully processed."
                        )

                        st.divider()

                        render_structured_profile(
                            structured_data
                        )

                    else:

                        st.success(
                            "Resume successfully uploaded."
                        )

                else:

                    show_error(
                        response,
                        "Resume upload failed",
                    )

    if st.session_state.resume_id:

        st.divider()

        st.markdown(
            f"""
            <div class="pp-card">

            <div class="pp-card-title">
                    ✓ Resume connected
            </div>

            <div class="pp-card-text">
                    Resume ID: {st.session_state.resume_id}
            </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        # Show the last processed profile if available
        # without forcing raw JSON open.

        if st.session_state.last_structured_profile:

            with st.expander(
                "View extracted profile again"
            ):

                render_structured_profile(
                    st.session_state.last_structured_profile
                )


# ============================================================
# ATS + JD MATCH
# ============================================================

elif page == "ATS & JD Match":

    if not st.session_state.resume_id:

        st.warning(
            "Upload your resume first to run ATS analysis and JD matching."
        )

        if st.button(
            "Go to Resume →",
            key="go_resume_from_job",
        ):
            go_to("Resume")

    else:

        # ----------------------------------------------------
        # ATS
        # ----------------------------------------------------

        st.markdown(
            "### ATS Resume Analysis"
        )

        st.caption(
            "Evaluate resume quality using the existing ATS service."
        )

        if st.button(
            "Analyze ATS Score →",
            use_container_width=True,
            key="ats_button",
        ):

            with st.spinner(
                "Analyzing resume ATS readiness..."
            ):

                try:

                    response = get_ats_analysis(
                        st.session_state.access_token,
                        st.session_state.resume_id,
                    )

                except Exception as exc:

                    st.error(
                        f"ATS request failed: {exc}"
                    )

                    response = None

            if response is not None:

                if response.status_code == 200:

                    data = safe_json(
                        response
                    )

                    ats_data = data.get(
                        "ats_analysis",
                        data,
                    )

                    score = ats_data.get(
                        "ats_score",
                        ats_data.get(
                            "score",
                            0,
                        ),
                    )

                    st.session_state.last_ats = score

                    score_cls = score_class(
                        score
                    )

                    st.divider()

                    st.markdown(
                        f"""
                        <div class="pp-card">

                        <div class="metric-label">
                                ATS readiness score
                        </div>

                        <div
                                class="metric-value {score_cls}"
                            >
                                {score}/100
                        </div>

                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    suggestions = ats_data.get(
                        "suggestions",
                        [],
                    )

                    if suggestions:

                        st.markdown(
                            "### ATS Suggestions"
                        )

                        if not isinstance(
                            suggestions,
                            list,
                        ):
                            suggestions = [
                                suggestions
                            ]

                        for suggestion in suggestions:
                            st.markdown(
                                f"- {suggestion}"
                            )

                    extra_keys = [
                        key
                        for key in ats_data.keys()
                        if key not in {
                            "ats_score",
                            "score",
                            "suggestions",
                        }
                    ]
                    if extra_keys:
                        with st.expander(
                            "View detailed ATS analysis"
                        ):
                            for key in extra_keys:
                                value = ats_data.get(key)
                                label = str(key).replace("_", " ").title()

                                if isinstance(value, dict):
                                    st.markdown(f"**{label}**")

                                    for sub_key, sub_value in value.items():
                                        sub_label = (
                                            str(sub_key)
                                            .replace("_", " ")
                                            .title()
                                        )

                                        if isinstance(sub_value, list):
                                            st.markdown(
                                                f"- **{sub_label}:** "
                                                + ", ".join(
                                                    str(item)
                                                    for item in sub_value
                                                )
                                            )
                                        else:
                                            st.markdown(
                                                f"- **{sub_label}:** {sub_value}"
                                            )

                                elif isinstance(value, list):
                                    st.markdown(f"**{label}**")

                                    for item in value:
                                        st.markdown(f"- {item}")

                                else:
                                    st.markdown(
                                        f"**{label}:** {value}"
                                    )

                else:

                    show_error(
                        response,
                        "ATS analysis failed",
                    )

        # ----------------------------------------------------
        # JD MATCH
        # ----------------------------------------------------

        st.divider()

        st.markdown(
            "### Job Description Match"
        )

        st.caption(
            "Compare your resume with the requirements of a real job."
        )

        jd_text = st.text_area(
            "Job Description",
            height=280,
            placeholder=(
                "Paste the complete job description here..."
            ),
            key="jd_match_text",
        )

        if st.button(
            "Analyze Job Match →",
            use_container_width=True,
            key="jd_match_button",
        ):

            if not jd_text.strip():

                st.warning(
                    "Please paste a job description."
                )

            else:

                with st.spinner(
                    "Comparing your resume with the job..."
                ):

                    try:

                        response = match_jd(
                            st.session_state.access_token,
                            st.session_state.resume_id,
                            jd_text,
                        )

                    except Exception as exc:

                        st.error(
                            f"JD matching request failed: {exc}"
                        )

                        response = None

                if response is not None:

                    if response.status_code == 200:

                        data = safe_json(
                            response
                        )

                        match_data = data.get(
                            "jd_match",
                            data,
                        )

                        score = match_data.get(
                            "overall_match_score",
                            match_data.get(
                                "match_score",
                                0,
                            ),
                        )

                        st.session_state.last_match = score

                        st.divider()

                        st.markdown(
                            "### Match overview"
                        )

                        c1, c2, c3, c4 = st.columns(4)

                        with c1:
                            st.metric(
                                "Overall Match",
                                f"{score}%",
                            )

                        with c2:
                            st.metric(
                                "Skill Match",
                                f"{match_data.get('skill_match_score', 0)}%",
                            )

                        with c3:
                            st.metric(
                                "Matched Skills",
                                len(
                                    match_data.get(
                                        "matched_skills",
                                        [],
                                    )
                                ),
                            )

                        with c4:
                            st.metric(
                                "Skill Gaps",
                                len(
                                    match_data.get(
                                        "missing_skills",
                                        [],
                                    )
                                ),
                            )

                        left, right = st.columns(2)

                        with left:

                            st.markdown(
                                "#### ✓ Matched skills"
                            )

                            display_tags(
                                match_data.get(
                                    "matched_skills",
                                    [],
                                )
                            )

                        with right:

                            st.markdown(
                                "#### ⚠ Missing skills"
                            )

                            display_tags(
                                match_data.get(
                                    "missing_skills",
                                    [],
                                )
                            )

                        detected = match_data.get(
                            "jd_skills_detected",
                            [],
                        )

                        if detected:

                            with st.expander(
                                "Detected JD skills"
                            ):

                                display_tags(
                                    detected
                                )

                        if match_data.get(
                            "recommendation"
                        ):

                            st.info(
                                match_data[
                                    "recommendation"
                                ]
                            )

                        extra_keys = [
                            key
                            for key in match_data.keys()
                            if key not in {
                                "overall_match_score",
                                "match_score",
                                "skill_match_score",
                                "text_similarity_score",
                                "matched_skills",
                                "missing_skills",
                                "jd_skills_detected",
                                "recommendation",
                            }
                        ]

                        if extra_keys:

                            with st.expander(
                                "View detailed match analysis"
                            ):

                                st.json(
                                    {
                                        key: match_data[key]
                                        for key in extra_keys
                                    }
                                )

                    else:

                        show_error(
                            response,
                            "Job matching failed",
                        )


# ============================================================
# AI MENTOR
# ============================================================

elif page == "AI Mentor":

    st.markdown(
        "### Your personal AI career mentor"
    )

    if st.session_state.resume_id:

        st.markdown(
            '<div class="status-pill">'
            '✓ Resume-aware mentor'
            '</div>',
            unsafe_allow_html=True,
        )

        st.caption(
            "Your mentor can use your uploaded resume "
            "for personalized career guidance."
        )

    else:

        st.markdown(
            '<div class="status-pill">'
            'General career mentor'
            '</div>',
            unsafe_allow_html=True,
        )

        st.caption(
            "Upload a resume later for personalized guidance."
        )

    st.write("")

    # --------------------------------------------------------
    # EMPTY STATE
    # --------------------------------------------------------

    if not st.session_state.mentor_chat:

        st.markdown(
            """
            <div class="pp-card">

            <div
                    style="
                        font-size:1.3rem;
                        font-weight:700;
                        color:#f8fafc;
                    "
                >
                    👋 Hi! I'm your PathPilot mentor.
            </div>

            <div
                    style="
                        color:#94a3b8;
                        margin-top:.5rem;
                    "
                >
                    Ask me about AI careers, Python,
                    GenAI, interviews, projects,
                    resume improvement or job search.
            </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption(
            "Try asking:"
        )

        s1, s2, s3 = st.columns(3)

        suggestions = [
            (
                "What AI roles fit me?",
                "mentor_suggest_1",
            ),
            (
                "What should I learn next?",
                "mentor_suggest_2",
            ),
            (
                "How should I prepare for interviews?",
                "mentor_suggest_3",
            ),
        ]

        for col, (
            question,
            key,
        ) in zip(
            (s1, s2, s3),
            suggestions,
        ):

            with col:

                if st.button(
                    question,
                    key=key,
                    use_container_width=True,
                ):

                    st.session_state.mentor_pending_question = question
                    st.rerun()

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    top1, top2 = st.columns(
        [5, 1]
    )

    with top1:

        st.markdown(
            "#### 💬 Career conversation"
        )

    with top2:

        if st.button(
            "Clear chat",
            use_container_width=True,
            key="clear_mentor_chat",
        ):

            st.session_state.mentor_chat = []
            st.session_state.mentor_pending_question = None

            st.rerun()

    # --------------------------------------------------------
    # HISTORY
    # --------------------------------------------------------

    for msg in st.session_state.mentor_chat:

        role = msg.get(
            "role",
            "assistant",
        )

        content = msg.get(
            "content",
            "",
        )

        if not content:
            continue

        with st.chat_message(role):
            st.markdown(content)

    # --------------------------------------------------------
    # INPUT
    # --------------------------------------------------------

    user_input = st.chat_input(
        "Ask your mentor anything..."
    )

    pending = st.session_state.pop(
        "mentor_pending_question",
        None,
    )

    actual_input = (
        user_input
        if user_input
        else pending
    )

    # --------------------------------------------------------
    # SEND MESSAGE
    # --------------------------------------------------------

    if actual_input:

        actual_input = actual_input.strip()

        if not actual_input:
            st.stop()

        # Prevent accidental duplicate user messages
        if (
            st.session_state.mentor_chat
            and st.session_state.mentor_chat[-1]["role"]
            == "user"
            and st.session_state.mentor_chat[-1]["content"]
            .strip()
            == actual_input
        ):
            st.stop()

        st.session_state.mentor_chat.append(
            {
                "role": "user",
                "content": actual_input,
            }
        )

        with st.chat_message("user"):
            st.markdown(actual_input)

        with st.chat_message("assistant"):

            with st.spinner(
                "Thinking..."
            ):

                display_text, response, error = (
                    ask_mentor_question(
                        actual_input
                    )
                )

            if error:

                st.error(error)

                assistant_text = (
                    "I couldn't reach the mentor service right now. "
                    "Please try again."
                )

                st.session_state.mentor_chat.append(
                    {
                        "role": "assistant",
                        "content": assistant_text,
                    }
                )

                st.markdown(
                    assistant_text
                )

            elif display_text is not None:

                st.markdown(
                    display_text
                )

                st.session_state.mentor_chat.append(
                    {
                        "role": "assistant",
                        "content": display_text,
                    }
                )

            else:

                show_error(
                    response,
                    "Mentor request failed",
                )

                assistant_text = (
                    "The mentor service returned an error. "
                    "Please try again."
                )

                st.session_state.mentor_chat.append(
                    {
                        "role": "assistant",
                        "content": assistant_text,
                    }
                )


# ============================================================
# LEARNING HUB
# ============================================================

elif page == "Learning Hub":

    st.markdown(
        "### Learn smarter with AI-curated resources"
    )

    st.caption(
        "Find resources, save them to your account, "
        "or add your own."
    )

    tab_ai, tab_add, tab_saved, tab_history = st.tabs(
        [
            "🔎 Find Resources",
            "➕ Add Resource",
            "📚 My Resources",
            "🕘 Search History",
        ]
    )

    # ========================================================
    # AI SEARCH
    # ========================================================

    with tab_ai:

        question = st.text_input(
            "What do you want to learn?",
            placeholder=(
                "Example: RAG interview preparation "
                "for AI Engineers"
            ),
            key="learning_question",
        )

        if st.button(
            "Find Resources →",
            use_container_width=True,
            key="find_resources_button",
        ):

            if not question.strip():

                st.warning(
                    "Please enter a learning topic."
                )

            else:

                with st.spinner(
                    "Finding useful resources..."
                ):

                    try:

                        response = get_learning_resources(
                            st.session_state.access_token,
                            question.strip(),
                        )

                    except Exception as exc:

                        st.error(
                            f"Resource search failed: {exc}"
                        )

                        response = None

                if response is not None:

                    if response.status_code == 200:

                        data = safe_json(
                            response
                        )

                        if data.get("answer"):

                            st.markdown(
                                "### AI Guidance"
                            )

                            st.markdown(
                                data["answer"]
                            )

                        if data.get(
                            "source_type"
                        ):

                            st.caption(
                                f"Source: "
                                f"{data['source_type']}"
                            )

                        resources = data.get(
                            "resources",
                            [],
                        )

                        if resources:

                            st.markdown(
                                "### Recommended resources"
                            )

                            for index, resource in enumerate(
                                resources,
                                1,
                            ):

                                if not isinstance(
                                    resource,
                                    dict,
                                ):

                                    st.write(
                                        f"- {resource}"
                                    )

                                    continue

                                title = resource.get(
                                    "title",
                                    "Untitled resource",
                                )

                                url = resource.get(
                                    "url"
                                )

                                with st.container(
                                    border=True
                                ):

                                    st.markdown(
                                        f"**{index}. {title}**"
                                    )

                                    if resource.get(
                                        "description"
                                    ):

                                        st.write(
                                            resource[
                                                "description"
                                            ]
                                        )

                                    meta = []

                                    if resource.get(
                                        "skill"
                                    ):
                                        meta.append(
                                            f"Skill: "
                                            f"{resource['skill']}"
                                        )

                                    if resource.get(
                                        "level"
                                    ):
                                        meta.append(
                                            f"Level: "
                                            f"{resource['level']}"
                                        )

                                    if resource.get(
                                        "source"
                                    ):
                                        meta.append(
                                            f"Source: "
                                            f"{resource['source']}"
                                        )

                                    if meta:

                                        st.caption(
                                            " • ".join(meta)
                                        )

                                    a, b = st.columns(2)

                                    with a:

                                        if url:

                                            st.link_button(
                                                "Open Resource",
                                                url,
                                                use_container_width=True,
                                            )

                                    with b:

                                        if st.button(
                                            "Save",
                                            key=f"save_ai_{index}",
                                            use_container_width=True,
                                        ):

                                            save_response = (
                                                save_learning_resource(
                                                    st.session_state.access_token,
                                                    title,
                                                    url,
                                                    resource.get(
                                                        "skill"
                                                    ),
                                                    resource.get(
                                                        "level"
                                                    ),
                                                    resource.get(
                                                        "description"
                                                    ),
                                                )
                                            )

                                            if save_response.status_code in (
                                                200,
                                                201,
                                            ):

                                                st.success(
                                                    "Saved!"
                                                )

                                            else:

                                                show_error(
                                                    save_response,
                                                    "Could not save resource",
                                                )

                        else:

                            st.info(
                                "No resources were returned."
                            )

                    else:

                        show_error(
                            response,
                            "Resource search failed",
                        )

    # ========================================================
    # ADD RESOURCE
    # ========================================================

    with tab_add:

        st.markdown(
            "### Save your own resource"
        )

        title = st.text_input(
            "Title",
            placeholder=(
                "FastAPI Official Documentation"
            ),
            key="own_resource_title",
        )

        url = st.text_input(
            "URL",
            placeholder="https://...",
            key="own_resource_url",
        )

        skill = st.text_input(
            "Skill",
            placeholder="FastAPI",
            key="own_resource_skill",
        )

        level = st.selectbox(
            "Level",
            [
                "Beginner",
                "Intermediate",
                "Advanced",
                "All Levels",
            ],
            key="own_resource_level",
        )

        description = st.text_area(
            "Description",
            placeholder=(
                "Why is this resource useful?"
            ),
            key="own_resource_description",
        )

        if st.button(
            "Save Resource →",
            use_container_width=True,
            key="save_own_resource",
        ):

            if not title.strip():

                st.warning(
                    "Please enter a title."
                )

            elif not url.strip():

                st.warning(
                    "Please enter a URL."
                )

            elif not (
                url.startswith("http://")
                or url.startswith("https://")
            ):

                st.warning(
                    "Please enter a valid URL."
                )

            else:

                with st.spinner(
                    "Saving resource..."
                ):

                    response = save_learning_resource(
                        st.session_state.access_token,
                        title.strip(),
                        url.strip(),
                        skill.strip()
                        or None,
                        level,
                        description.strip()
                        or None,
                    )

                if response.status_code in (
                    200,
                    201,
                ):

                    st.success(
                        "Resource saved successfully."
                    )

                else:

                    show_error(
                        response,
                        "Could not save resource",
                    )

    # ========================================================
    # SAVED RESOURCES
    # ========================================================

    with tab_saved:

        st.markdown(
            "### Your saved resources"
        )

        with st.spinner(
            "Loading saved resources..."
        ):

            response = get_saved_learning_resources(
                st.session_state.access_token
            )

        if response.status_code == 200:

            data = safe_json(
                response
            )

            if isinstance(
                data,
                list,
            ):

                resources = data

            else:

                resources = data.get(
                    "resources",
                    data.get(
                        "saved_resources",
                        [],
                    ),
                )

            if not resources:

                st.info(
                    "You haven't saved any resources yet."
                )

            else:

                st.caption(
                    f"{len(resources)} saved resource(s)"
                )

                for index, resource in enumerate(
                    resources,
                    1,
                ):

                    if not isinstance(
                        resource,
                        dict,
                    ):

                        st.write(
                            f"- {resource}"
                        )

                        continue

                    with st.container(
                        border=True
                    ):

                        st.markdown(
                            f"**{index}. "
                            f"{resource.get('title', 'Resource')}**"
                        )

                        if resource.get(
                            "description"
                        ):

                            st.write(
                                resource[
                                    "description"
                                ]
                            )

                        if resource.get(
                            "url"
                        ):

                            st.link_button(
                                "Open Resource",
                                resource["url"],
                            )

        else:

            show_error(
                response,
                "Could not load saved resources",
            )

    # ========================================================
    # HISTORY
    # ========================================================

    with tab_history:

        st.markdown(
            "### Previous AI learning searches"
        )

        with st.spinner(
            "Loading search history..."
        ):

            response = get_learning_history(
                st.session_state.access_token
            )

        if response.status_code == 200:

            data = safe_json(
                response
            )

            if isinstance(
                data,
                list,
            ):

                history = data

            else:

                history = data.get(
                    "history",
                    data.get(
                        "searches",
                        [],
                    ),
                )

            if not history:

                st.info(
                    "No previous learning searches found."
                )

            else:

                for item in history:

                    if isinstance(
                        item,
                        dict,
                    ):

                        question_text = item.get(
                            "question",
                            item.get(
                                "query",
                                "Learning search",
                            ),
                        )

                        st.markdown(
                            f"**{question_text}**"
                        )

                        if item.get(
                            "created_at"
                        ):

                            st.caption(
                                str(
                                    item[
                                        "created_at"
                                    ]
                                )
                            )

                        if item.get(
                            "answer"
                        ):

                            st.write(
                                item["answer"]
                            )

                        st.divider()

                    else:

                        st.write(
                            f"- {item}"
                        )

        else:

            show_error(
                response,
                "Could not load learning history",
            )


# ============================================================
# SHOULD I APPLY
# ============================================================

elif page == "Should I Apply?":

    if not st.session_state.resume_id:

        st.warning(
            "Upload your resume first so PathPilot "
            "can compare it with the job."
        )

        if st.button(
            "Go to Resume →",
            key="go_resume_from_apply",
        ):

            go_to("Resume")

    else:

        st.markdown(
            "### Make a smarter application decision"
        )

        st.caption(
            "PathPilot uses the multi-agent workflow to "
            "analyze the resume, match the JD, generate "
            "preparation guidance, retrieve resources, "
            "and make the final application recommendation."
        )

        jd_text = st.text_area(
            "Job Description",
            height=280,
            placeholder=(
                "Paste the complete job description here..."
            ),
            key="apply_jd_text",
        )

        if st.button(
            "Analyze Application →",
            use_container_width=True,
            key="apply_button",
        ):

            if not jd_text.strip():

                st.warning(
                    "Please paste the job description."
                )

            else:

                with st.spinner(
                    "Running multi-agent application analysis..."
                ):

                    try:

                        response = should_i_apply(
                            st.session_state.access_token,
                            st.session_state.resume_id,
                            jd_text,
                        )

                    except Exception as exc:

                        st.error(
                            f"Application analysis failed: {exc}"
                        )

                        response = None

                if response is not None:

                    if response.status_code == 200:

                        data = safe_json(
                            response
                        )

                        st.session_state.last_apply = data

                        score = data.get(
                            "match_score",
                            data.get(
                                "overall_match_score",
                                0,
                            ),
                        )

                        recommendation = data.get(
                            "recommendation",
                            "Not available",
                        )

                        prep = data.get(
                            "estimated_prep_time",
                            "—",
                        )

                        st.divider()

                        c1, c2, c3 = st.columns(3)

                        with c1:

                            st.metric(
                                "Match Score",
                                f"{score}%",
                            )

                        with c2:

                            st.metric(
                                "Recommendation",
                                recommendation,
                            )

                        with c3:

                            st.metric(
                                "Preparation",
                                prep,
                            )

                        if data.get(
                            "reasoning"
                        ):

                            st.markdown(
                                "### Why this recommendation?"
                            )

                            st.markdown(
                                f"""
                                <div class="pp-card">
                                    {data['reasoning']}
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                        left, right = st.columns(2)

                        with left:

                            st.markdown(
                                "### ✓ Your strengths"
                            )

                            display_tags(
                                data.get(
                                    "matched_skills",
                                    [],
                                )
                            )

                        with right:

                            st.markdown(
                                "### ⚠ Skill gaps"
                            )

                            display_tags(
                                data.get(
                                    "missing_skills",
                                    [],
                                )
                            )

                        roadmap = data.get(
                            "roadmap",
                            [],
                        )

                        if roadmap:

                            st.divider()

                            st.markdown(
                                "### Preparation roadmap"
                            )

                            for index, step in enumerate(
                                roadmap,
                                1,
                            ):

                                with st.container(
                                    border=True
                                ):

                                    if isinstance(
                                        step,
                                        dict,
                                    ):

                                        name = step.get(
                                            "step",
                                            step.get(
                                                "title",
                                                "Step",
                                            ),
                                        )

                                        st.markdown(
                                            f"**{index}. {name}**"
                                        )

                                        if step.get(
                                            "priority"
                                        ):

                                            st.caption(
                                                "Priority: "
                                                f"{step['priority']}"
                                            )

                                        if step.get(
                                            "reason"
                                        ):

                                            st.write(
                                                step[
                                                    "reason"
                                                ]
                                            )

                                    else:

                                        st.markdown(
                                            f"**{index}. {step}**"
                                        )

                        resources = data.get(
                            "resources",
                            [],
                        )

                        if resources:

                            st.divider()

                            st.markdown(
                                "### Recommended resources"
                            )

                            for resource in resources:

                                if isinstance(
                                    resource,
                                    dict,
                                ):

                                    st.markdown(
                                        f"**{resource.get('title', 'Resource')}**"
                                    )

                                    if resource.get(
                                        "description"
                                    ):

                                        st.write(
                                            resource[
                                                "description"
                                            ]
                                        )

                                    if resource.get(
                                        "url"
                                    ):

                                        st.link_button(
                                            "Open Resource",
                                            resource[
                                                "url"
                                            ],
                                        )

                                else:

                                    st.write(
                                        f"- {resource}"
                                    )

                    else:

                        show_error(
                            response,
                            "Application analysis failed",
                        )