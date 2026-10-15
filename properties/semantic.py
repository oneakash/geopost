from functools import lru_cache
from typing import Sequence

from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def embed_text(text: str) -> list[float]:
    if not text.strip():
        raise ValueError("Search text cannot be empty")

    vector = get_embedding_model().encode(
        text,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    return vector.tolist()


def embed_texts(texts: Sequence[str]) -> list[list[float]]:
    vector_batch = get_embedding_model().encode(
        list(texts),
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    return vector_batch.tolist()
