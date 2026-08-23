from backend.services.rag.documents import load_resources
from langchain_text_splitters import RecursiveCharacterTextSplitter


def main():
    documents = load_resources()

    print("Original documents:", len(documents))

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50
    )

    chunks = splitter.split_documents(documents)

    print("Total chunks:", len(chunks))

    for i, chunk in enumerate(chunks):
        print("\n--- CHUNK", i + 1, "---")
        print(chunk.page_content)
        print("Metadata:", chunk.metadata)


if __name__ == "__main__":
    main()