from backend.services.rag.retriever import get_relevant_documents


QUERIES = [
    "I want to learn Python programming",
    "I want to learn FastAPI",
    "I want to learn LangChain",
    "I want to learn cybersecurity",
    "I want to learn photography",
]


def main():

    for query in QUERIES:

        print("\n" + "=" * 60)
        print("QUERY:", query)
        print("=" * 60)

        documents = get_relevant_documents(
            query,
            k=3,
            threshold=1.0
        )

        if not documents:
            print("NO RELEVANT RESOURCE FOUND")
            continue

        print("RELEVANT RESOURCES:")

        for document in documents:
            print(
                "-",
                document.metadata.get("title"),
                "|",
                document.metadata.get("skill")
            )


if __name__ == "__main__":
    main()