from backend.services.web_search.tavily_search import (
    search_learning_resources,
    clean_web_results,
)


def main():

    query = "cybersecurity for beginners"

    results = search_learning_resources(
        query,
        max_results=5
    )

    resources = clean_web_results(results)

    print("\nCLEAN WEB RESOURCES:")

    for resource in resources:

        print("\n--- RESOURCE ---")
        print("Title:", resource["title"])
        print("URL:", resource["url"])
        print("Description:", resource["description"])
        print("Source:", resource["source"])


if __name__ == "__main__":
    main()