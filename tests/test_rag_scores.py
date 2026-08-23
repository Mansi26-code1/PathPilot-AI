from backend.services.rag.vector_store import get_vector_store


QUERIES = [
    "I want to learn Python programming",
    "I want to learn FastAPI",
    "I want to learn LangChain",
    "I want to learn cybersecurity",
    "I want to learn photography",
]


def main():

    vector_store = get_vector_store()

    for query in QUERIES:

        print("\n" + "=" * 70)
        print("QUERY:", query)
        print("=" * 70)

        results = vector_store.similarity_search_with_score(
            query,
            k=3
        )

        for i, (document, score) in enumerate(results, start=1):

            print(f"\n--- RESULT {i} ---")
            print("Score:", score)
            print("Title:", document.metadata.get("title"))
            print("Skill:", document.metadata.get("skill"))
            print("Level:", document.metadata.get("level"))


if __name__ == "__main__":
    main()