from langchain_chroma import Chroma

from backend.services.rag.documents import load_resources
from backend.services.rag.embeddings import get_embedding_model


PERSIST_DIRECTORY = "chroma_db"


def create_vector_store():
    """
    Create and persist a Chroma vector store
    from the curated learning resources.
    """

    documents = load_resources()
    embeddings = get_embedding_model()

    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=PERSIST_DIRECTORY,
        collection_name="pathpilot_resources"
    )

    return vector_store


def get_vector_store():
    """
    Load the existing Chroma vector store.
    """

    embeddings = get_embedding_model()

    vector_store = Chroma(
        persist_directory=PERSIST_DIRECTORY,
        embedding_function=embeddings,
        collection_name="pathpilot_resources"
    )

    return vector_store