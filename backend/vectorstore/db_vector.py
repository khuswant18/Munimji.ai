from langchain_postgres import PGVector
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
import os

connection_string = os.getenv("DATABASE_URL")
collection_name = "munimji_vectors"

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

vector_store = None

def get_vector_store():
    global vector_store
    if vector_store is None:
        if not connection_string:
            raise ValueError("DATABASE_URL environment variable is not set")
        vector_store = PGVector(
            connection=connection_string,
            collection_name=collection_name,
            embeddings=embeddings,
            use_jsonb=True,
        )
    return vector_store

def add_to_vectorstore(text: str):
    doc = Document(page_content=text)
    get_vector_store().add_documents([doc]) 