# 🧭 PathPilot AI — Your Personalized AI Career Mentor

PathPilot AI is a full-stack AI career platform built for CS students and freshers who don't know which tech role fits them, what skills they're missing, or how to prepare — the exact problem I faced myself while job-hunting. It connects resume analysis, ATS scoring, JD matching, an AI mentor, a RAG-based learning hub, and a multi-agent "Should I Apply?" decision workflow into one working product.

## 🎯 What it does

- **Resume Intelligence** — Upload a PDF/DOCX → automatic parsing, section detection, structured extraction (skills, education, experience, projects)
- **ATS Scoring** — Rule-based, weighted, explainable score (action verbs, quantified achievements, section completeness, keywords, formatting) with actionable suggestions
- **JD Matching** — TF-IDF + cosine similarity combined with explicit skill-evidence matching (70% skill match + 30% text similarity) → overall match score, matched/missing skills, recommendation
- **AI Career Mentor** — Grounded, hallucination-controlled LLM mentor. Never invents skills, distinguishes existing vs. recommended skills, gives honest guidance to students from any background (CS or non-CS). Works in General Mode (no resume) or Resume-Aware Mode.
- **RAG Learning Hub** — Hybrid retrieval (curated ChromaDB knowledge base + Tavily web search fallback), a scope-check guardrail that declines off-topic queries, plus save-your-own-resource and search history features
- **"Should I Apply?" Agent** — A 5-agent LangGraph workflow (Resume → JD Match → conditional branch → Roadmap → Resource → Decision) that returns, in one API call, whether to apply now or prepare first, with reasoning, a prep timeline, and matched resources
- **Streamlit Frontend** — Login/signup, resume upload, ATS & JD match dashboard, mentor chat, learning hub, agent workflow — all wired to the live backend

## 🏗️ System Architecture

```
                    ┌──────────────────────┐
                    │   Streamlit Frontend │
                    └───────────┬──────────┘
                                │ HTTP / REST + JWT
                                ▼
                    ┌──────────────────────┐
                    │    FastAPI Backend   │
                    └───────────┬──────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ Auth & Users   │     │ Resume / ATS /   │     │ AI Services      │
│ (JWT, bcrypt)  │     │ JD Matching       │     │ (Mentor / RAG /  │
│                │     │ (pypdf, TF-IDF)   │     │  Agents)         │
└───────────────┘     └──────────────────┘     └─────────┬────────┘
                                                            │
                                     ┌──────────────────────┼──────────────────────┐
                                     ▼                      ▼                      ▼
                              ┌────────────┐        ┌────────────┐        ┌────────────┐
                              │ Groq LLM   │        │ ChromaDB + │        │ LangGraph  │
                              │ (grounded) │        │ Tavily RAG │        │ Agents     │
                              └────────────┘        └────────────┘        └────────────┘

                    ┌────────────────────────────────┐
                    │  SQLite/PostgreSQL Database     │
                    │  Users / Resumes / History /    │
                    │  Saved Resources / Conversations│
                    └────────────────────────────────┘
```

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| Frontend | Python, Streamlit |
| Backend | FastAPI, Uvicorn, Pydantic, SQLAlchemy |
| Auth | JWT (OAuth2PasswordBearer), bcrypt password hashing |
| Classical ML/NLP | scikit-learn (TF-IDF, cosine similarity) |
| GenAI | Groq (Llama models), grounded prompt engineering |
| RAG | LangChain (LCEL), ChromaDB, HuggingFace sentence-transformers, Tavily web search |
| Agents | LangGraph (StateGraph, conditional routing, multi-agent orchestration) |
| Document processing | pypdf, python-docx |
| Database | SQLAlchemy ORM, SQLite (dev) → PostgreSQL (planned for prod) |

## 📁 Project Structure

```
PathPilot-AI/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── dependencies.py
│   ├── models.py
│   ├── schemas/
│   ├── crud/
│   ├── routers/
│   │   ├── auth.py
│   │   ├── resume.py
│   │   ├── mentor.py
│   │   ├── learning.py
│   │   └── agent.py
│   └── services/
│       ├── rag/
│       ├── agents/
│       └── ...
├── frontend/
│   ├── app.py
│   └── utils/api_client.py
├── knowledge_base/
├── tests/
├── .gitignore
├── README.md
└── requirements.txt
```

## 🔌 Key API Endpoints

```
POST   /auth/signup
POST   /auth/login
GET    /users/me

POST   /resume/upload
GET    /resume/{resume_id}
GET    /resume/{resume_id}/ats
POST   /resume/{resume_id}/match

POST   /mentor/{resume_id}

POST   /learning/resources
GET    /learning/history
POST   /learning/saved
GET    /learning/saved

POST   /agent/should-i-apply
```

## 🔐 Security Design

- JWT-based authentication between frontend and backend
- Ownership checks on every resume-related endpoint (`resume.user_id != user.id → 403`) — users can only access their own data
- Passwords hashed with bcrypt, never stored in plaintext

## 🗃️ Data Model

```
User
 ├── UserProfile
 ├── Resumes
 ├── Conversations (mentor chat history)
 ├── LearningHistory (search history)
 └── SavedLearningResources
```

## 🧠 Engineering Highlights (things I can explain in depth)

- **Why TF-IDF + explicit skill matching instead of an LLM-generated score** — a raw LLM score is non-deterministic and costly to call repeatedly; TF-IDF is fast and explainable, and combining it with skill-evidence matching gives a more actionable, defensible result than either alone
- **Grounding rules for the LLM mentor** — the system prompt explicitly forbids inventing skills, distinguishes "existing" vs. "recommended" skills, and requires honest scope statements for non-CS backgrounds — verified by deliberately asking about skills not present in the resume
- **Hybrid RAG with a scope-check guardrail** — a lightweight LLM classifier runs *before* retrieval to reject out-of-scope queries (e.g. "how to cook pasta"), saving unnecessary web-search calls and keeping the assistant honest about what it covers
- **LangGraph used selectively, not everywhere** — multi-agent orchestration is used specifically where multi-step, conditional decision-making is needed (the "Should I Apply?" workflow); simpler single-purpose features (ATS scoring, JD matching) intentionally use direct service calls instead of agent-wrapping everything
- **Evaluation & guardrails** — automated checks for hallucination, valid recommendation values, and no-guaranteed-outcome language, run against the agent workflow's final output

## ⚙️ Local Setup

**1. Clone and enter the repo**
```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd PathPilot-AI
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv
venv\Scripts\activate      # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

Create a `.env` file in the project root:
```
DATABASE_URL=sqlite:///./pathpilot.db
SECRET_KEY=your_secret_key
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```
Never commit `.env` or API keys to GitHub.

**5. Run the backend**
```bash
set OPENBLAS_NUM_THREADS=1
set OMP_NUM_THREADS=1
uvicorn backend.main:app --reload --port 8001
```
Backend: `http://127.0.0.1:8001` · Swagger docs: `http://127.0.0.1:8001/docs`

**6. Run the frontend** (in a separate terminal)
```bash
venv\Scripts\activate
streamlit run frontend/app.py
```

## 🧩 Development Philosophy

- **Modular architecture** — AI logic, API routes, database access, and frontend logic are kept in separate layers, not one file
- **API-first backend** — the frontend talks to the backend only through REST APIs, never touching the database or AI services directly
- **Structured AI outputs** — LLM responses are normalized into structured JSON wherever possible, so the frontend renders useful UI instead of raw model text
- **Reusable services** — RAG, agents, and resume processing are built as backend services that multiple features (mentor, agent workflow) reuse rather than duplicate

## 🚧 Status & Roadmap

**Done:** FastAPI backend, Streamlit frontend, auth, resume intelligence, ATS analysis, JD matching, AI mentor, RAG learning hub, LangGraph career agent.

**In progress:** Automated pytest test suite, Docker containerization, cloud deployment (backend + frontend + production database).

## 👩‍💻 Author

**Mansi Pandey** — B.Tech, Computer Science & Engineering
Interests: AI/ML, Generative AI, LLM applications, RAG, AI engineering, backend engineering, data science.

## 💡 Why PathPilot AI?

Most career tools solve one piece of the job-search puzzle. PathPilot AI connects the full workflow — understand your profile → analyze your resume → measure job fit → identify skill gaps → learn → prepare → decide → apply — as one platform where multiple AI capabilities share the same user context, rather than a single-purpose chatbot or resume scanner.