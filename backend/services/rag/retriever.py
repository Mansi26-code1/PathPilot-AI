from backend.services.rag.vector_store import get_vector_store


DEFAULT_THRESHOLD = 1.0


def get_relevant_documents(
    query: str,
    k: int = 3,
    threshold: float = DEFAULT_THRESHOLD
):
    """
    Retrieve learning resources from Chroma
    and keep only sufficiently relevant results.

    Chroma returns distance scores where:
    lower score = more similar.
    """

    vector_store = get_vector_store()

    results = vector_store.similarity_search_with_score(
        query,
        k=k
    )

    relevant_documents = []

    for document, score in results:

        if score <= threshold:
            relevant_documents.append(document)

    return relevant_documents


def get_retriever(k: int = 3):
    """
    Return a standard Chroma retriever.
    """

    vector_store = get_vector_store()

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": k
        }
    )

    return retriever