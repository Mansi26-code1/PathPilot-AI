from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

from backend.config import GROQ_API_KEY, GROQ_MODEL
from backend.services.rag.retriever import get_relevant_documents

from backend.services.web_search.tavily_search import (
    search_learning_resources,
    clean_web_results,
)


# --------------------------------------------------
# Scope Check Prompt
# --------------------------------------------------

SCOPE_CHECK_PROMPT = ChatPromptTemplate.from_template(
    """
You are a scope classifier for PathPilot AI, a technology
and career-learning platform.

PathPilot AI's Learning Hub ONLY helps with topics related to:
- programming languages, frameworks, and tools
- data science, machine learning, AI, GenAI
- software engineering, DevOps, cloud, cybersecurity
- career/technical skill-building (SQL, Git, APIs, etc.)

Determine if the following user question is asking to learn
something within this technology/career-learning scope.

Answer with EXACTLY one word: "YES" or "NO".

USER QUESTION:
{question}
"""
)


# --------------------------------------------------
# RAG Prompt
# --------------------------------------------------

RAG_PROMPT = ChatPromptTemplate.from_template(
    """
You are PathPilot AI's Learning Hub assistant.

Your job is to help users find suitable learning resources.

Use ONLY the resources provided in the context.

STRICT RULES:

1. Never invent a resource.
2. Never invent a URL.
3. Never recommend a resource that is not present in the context.
4. If the context does not contain a suitable resource,
   clearly say that no suitable verified resource was found.
5. Explain briefly why the recommended resource is relevant.
6. Do not claim that a resource teaches something unless
   the provided resource description supports that claim.

RESOURCE CONTEXT:
{context}

USER QUESTION:
{question}
"""
)


# --------------------------------------------------
# LLM
# --------------------------------------------------

llm = ChatGroq(
    model=GROQ_MODEL,
    groq_api_key=GROQ_API_KEY,
    temperature=0.2
)


# --------------------------------------------------
# Output parser
# --------------------------------------------------

output_parser = StrOutputParser()


# --------------------------------------------------
# Document formatter
# --------------------------------------------------

def format_documents(documents):
    """
    Convert retrieved LangChain Documents
    into text context for the LLM.
    """

    formatted_documents = []

    for document in documents:

        metadata = document.metadata

        formatted_documents.append(
            f"""
Title: {metadata.get("title", "")}
Description: {metadata.get("description", "")}
Skill: {metadata.get("skill", "")}
Level: {metadata.get("level", "")}
Source: {metadata.get("source", "")}
URL: {metadata.get("url", "")}
"""
        )

    return "\n---\n".join(formatted_documents)


# --------------------------------------------------
# LCEL Chains
# --------------------------------------------------

rag_chain = (
    RAG_PROMPT
    | llm
    | output_parser
)

scope_check_chain = (
    SCOPE_CHECK_PROMPT
    | llm
    | output_parser
)


import re

def clean_url(url: str) -> str:
    """Convert Markdown-formatted URLs into plain URLs."""

    if not url:
        return url

    url = str(url).strip()

    # [text](https://example.com)
    match = re.match(r"\[.*?\]\((https?://[^)]+)\)", url)

    if match:
        return match.group(1)

    # <https://example.com>
    if url.startswith("<") and url.endswith(">"):
        return url[1:-1]

    return url

def is_in_scope(question: str) -> bool:
    """
    Classify whether the question is within PathPilot AI's
    technology/career-learning scope, before running any
    retrieval or web search.
    """

    response = scope_check_chain.invoke(
        {"question": question}
    )

    return response.strip().upper().startswith("YES")


# --------------------------------------------------
# Generate RAG Response
# --------------------------------------------------
def generate_rag_response(question: str):

    # --------------------------------------------------
    # STEP 0: Scope check — reject clearly unrelated queries
    # before spending time/cost on retrieval or web search
    # --------------------------------------------------

    if not is_in_scope(question):

        return {
            "answer": (
                "PathPilot AI's Learning Hub is focused on "
                "technology and career-related learning resources "
                "(programming, data, ML/AI, cloud, cybersecurity, etc.). "
                "This question seems to be outside that scope."
            ),
            "resources": [],
            "source_type": "out_of_scope"
        }

    # --------------------------------------------------
    # STEP 1: Search curated knowledge base
    # --------------------------------------------------

    documents = get_relevant_documents(
        query=question,
        k=3,
        threshold=1.0
    )

    curated_resources = []

    for document in documents:

        metadata = document.metadata
        curated_resources.append(
    {
        "title": metadata.get("title"),
        "description": metadata.get("description", ""),
        "url": clean_url(metadata.get("url")),
        "skill": metadata.get("skill"),
        "level": metadata.get("level"),
        "source": metadata.get("source")
    }
)

        

    # --------------------------------------------------
    # STEP 2: ALWAYS search web as well
    # --------------------------------------------------

    web_results = search_learning_resources(
        question,
        max_results=5
    )

    web_resources = clean_web_results(web_results)

    # --------------------------------------------------
    # STEP 3: Merge curated + web resources
    # --------------------------------------------------

    all_resources = []

    # Curated resources get priority
    all_resources.extend(curated_resources)

    # Add web resources
    all_resources.extend(web_resources)

    # --------------------------------------------------
    # STEP 4: Remove duplicate URLs
    # --------------------------------------------------

    unique_resources = []
    seen_urls = set()

    for resource in all_resources:

        url = resource.get("url")

        if not url:
            continue

        if url in seen_urls:
            continue

        seen_urls.add(url)
        unique_resources.append(resource)

    # --------------------------------------------------
    # STEP 5: No resources found anywhere
    # --------------------------------------------------

    if not unique_resources:

        return {
            "answer": (
                "No suitable learning resource "
                "was found for this topic."
            ),
            "resources": [],
            "source_type": "none"
        }

    # --------------------------------------------------
    # STEP 6: Build grounded context
    # --------------------------------------------------

    context_parts = []

    for resource in unique_resources:

        context_parts.append(
            f"""
Title: {resource.get("title", "")}
Description: {resource.get("description", "")}
Skill: {resource.get("skill", "")}
Level: {resource.get("level", "")}
Source: {resource.get("source", "")}
URL: {resource.get("url", "")}
"""
        )

    context = "\n---\n".join(context_parts)

    # --------------------------------------------------
    # STEP 7: Generate grounded answer
    # --------------------------------------------------

    answer = rag_chain.invoke(
        {
            "context": context,
            "question": question
        }
    )

    # --------------------------------------------------
    # STEP 8: Determine source type
    # --------------------------------------------------

    if curated_resources and web_resources:
        source_type = "hybrid"

    elif curated_resources:
        source_type = "curated"

    elif web_resources:
        source_type = "web_search"

    else:
        source_type = "none"

    # --------------------------------------------------
    # STEP 9: Final response
    # --------------------------------------------------

    return {
        "answer": answer,
        "resources": unique_resources,
        "source_type": source_type
    }