import json
from pathlib import Path

from langchain_core.documents import Document


# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Knowledge base file
RESOURCES_FILE = PROJECT_ROOT / "Knowledge_base" / "resources.json"


def load_resources() -> list[Document]:
    """
    Load learning resources from JSON
    and convert them into LangChain Document objects.
    """

    if not RESOURCES_FILE.exists():
        raise FileNotFoundError(
            f"Resources file not found: {RESOURCES_FILE}"
        )

    with open(
        RESOURCES_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        resources = json.load(file)

    documents = []

    for resource in resources:

        content = (
            f"Title: {resource.get('title', '')}\n"
            f"Description: {resource.get('description', '')}\n"
            f"Skill: {resource.get('skill', '')}\n"
            f"Level: {resource.get('level', '')}\n"
            f"Source: {resource.get('source', '')}"
        )

        metadata = {
            "title": resource.get("title"),
            "url": resource.get("url"),
            "skill": resource.get("skill"),
            "level": resource.get("level"),
            "source": resource.get("source")
        }

        document = Document(
            page_content=content,
            metadata=metadata
        )

        documents.append(document)

    return documents