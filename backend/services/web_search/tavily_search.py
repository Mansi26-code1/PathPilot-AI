from tavily import TavilyClient
import re

from backend.config import TAVILY_API_KEY


def search_learning_resources(
    query: str,
    max_results: int = 5
):
    """
    Search the web for learning resources using Tavily.
    """

    client = TavilyClient(api_key=TAVILY_API_KEY)

    response = client.search(
        query=f"best learning resources for {query}",
        search_depth="advanced",
        max_results=max_results,
        include_answer=False,
    )

    return response.get("results", [])


def clean_url(url: str) -> str:
    """
    Convert Markdown-style URLs into plain URLs.
    """

    if not url:
        return ""

    # [https://example.com](https://example.com)
    match = re.match(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        url
    )

    if match:
        return match.group(2)

    # <https://example.com>
    if url.startswith("<") and url.endswith(">"):
        return url[1:-1]

    return url.strip()


def clean_web_results(results):
    """
    Convert Tavily results into clean learning resources.
    """

    resources = []

    for result in results:

        title = result.get("title")
        url = result.get("url")
        content = result.get("content", "")

        if not title or not url:
            continue

        url = clean_url(url)

        resources.append(
            {
                "title": title,
                "url": url,
                "description": content[:500],
                "source": "Web Search",
            }
        )

    return resources