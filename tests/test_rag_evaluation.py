from backend.services.rag.chain import generate_rag_response


TEST_QUERIES = [
    "I want to learn Python programming",
    "I want to learn FastAPI",
    "I want to learn LangChain",
    "I want to learn cybersecurity",
    "I want to learn photography",
]


def run_test(query: str):

    print("\n" + "=" * 60)
    print("QUERY:", query)
    print("=" * 60)

    result = generate_rag_response(query)

    print("\nANSWER:")
    print(result["answer"])

    print("\nRETRIEVED RESOURCES:")

    if not result["resources"]:
        print("No resources found.")
        return

    for resource in result["resources"]:
        print(
            f"- {resource['title']} "
            f"| Skill: {resource['skill']} "
            f"| Level: {resource['level']}"
        )


def main():

    print("\nPATHPILOT RAG EVALUATION")

    for query in TEST_QUERIES:
        run_test(query)


if __name__ == "__main__":
    main()