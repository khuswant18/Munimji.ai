from .db_vector import vector_store
from .embeddings import get_embeddings

def search_vectorstore(query: str, top_k=5):
    query_embedding = get_embeddings(query)
    results = vector_store.similarity_search_by_vector(query_embedding, k=top_k)
    return results