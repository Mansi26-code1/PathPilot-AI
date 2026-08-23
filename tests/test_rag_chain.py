from backend.services.rag.chain import generate_rag_response


QUERIES = [
    "I want to learn Python programming",
    "I want to learn cybersecurity for beginners",
    "I want to learn photography",
]


def main():

    for query in QUERIES:

        print("\n" + "=" * 60)
        print("QUERY")
        print("=" * 60)

        print(query)

        result = generate_rag_response(query)

        print("\n" + "=" * 60)
        print("ANSWER")
        print("=" * 60)

        print(result["answer"])

        print("\n" + "=" * 60)
        print("SOURCE TYPE")
        print("=" * 60)

        print(result["source_type"])

        print("\n" + "=" * 60)
        print("RESOURCES")
        print("=" * 60)

        for resource in result["resources"]:
            print(resource)


if __name__ == "__main__":
    main()