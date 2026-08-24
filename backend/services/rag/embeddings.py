from langchain_huggingface import HuggingFaceEndpointEmbeddings
import os

def get_embedding_model():
    """
    Use HuggingFace's hosted Inference API instead of loading
    the model locally — saves RAM on low-memory servers.
    """
    return HuggingFaceEndpointEmbeddings(
        model="sentence-transformers/all-MiniLM-L6-v2",
        huggingfacehub_api_token=os.getenv("HF_TOKEN"),
    )