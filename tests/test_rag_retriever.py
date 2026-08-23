from backend.services.rag.retriever import get_retriever


def main():
    retriever = get_retriever(k=2)

    query = "I want to learn Python programming"

    results = retriever.invoke(query)

    print("\nQUERY:")
    print(query)

    print("\nRESULTS:")

    for i, document in enumerate(results, start=1):
        print(f"\n--- RESULT {i} ---")
        print(document.page_content)
        print("Metadata:", document.metadata)


if __name__ == "__main__":
    main()



























