from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_embedding(text):
    """Generates a 384-dimensional vector for the given text."""
    if not text:
        return None
    embedding = model.encode(text)
    return embedding.tolist()