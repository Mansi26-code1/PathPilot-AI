from backend.services.rag.embeddings import get_embedding_model


def main():
    print("Loading embedding model...")

    embeddings = get_embedding_model()

    text = "I want to learn Python programming."

    vector = embeddings.embed_query(text)

    print("Embedding created successfully!")
    print("Vector length:", len(vector))
    print("First 10 values:", vector[:10])


if __name__ == "__main__":
    main()