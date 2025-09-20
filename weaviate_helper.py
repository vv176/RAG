import os

import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.config import Property, DataType
from weaviate.classes.query import MetadataQuery, Filter

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass


def _require_env(name: str) -> str:
    val = os.getenv(name)
    if not val:
        raise RuntimeError(f"Environment variable {name} is required but not set")
    return val


_url = _require_env("WEAVIATE_URL")
_api_key = _require_env("WEAVIATE_API_KEY")

# Connect to Weaviate Cloud using environment-provided URL and API key
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=_url,
    auth_credentials=Auth.api_key(_api_key),
)

# Ensure collection 'FAQ' exists with desired schema
if not client.collections.exists("FAQ"):
    client.collections.create(
        "FAQ",
        properties=[
            Property(name="question", data_type=DataType.TEXT),
            Property(name="answer", data_type=DataType.TEXT),
        ],
    )

faq = client.collections.get("FAQ")

# Ensure collection 'story_parts' exists with desired schema
if not client.collections.exists("story_parts"):
    client.collections.create(
        "story_parts",
        properties=[
            Property(name="part", data_type=DataType.TEXT),
        ],
    )

story_parts = client.collections.get("story_parts")

# Ensure collection 'story_parts_overlap' exists with desired schema
if not client.collections.exists("story_parts_overlap"):
    client.collections.create(
        "story_parts_overlap",
        properties=[
            Property(name="part", data_type=DataType.TEXT),
        ],
    )

story_parts_overlap = client.collections.get("story_parts_overlap")


def insert_chunk(question: str, answer: str, vector: list[float]) -> str | None:
    """
    Insert a FAQ item if it does not already exist (same question and answer).

    Returns the UUID of the inserted object, or None if it already existed.
    """
    # Deduplicate by exact match on both properties
    existing_filter = (
        Filter.by_property("question").equal(question)
        & Filter.by_property("answer").equal(answer)
    )
    existing = faq.query.fetch_objects(filters=existing_filter, limit=1)
    if existing.objects:
        # Already present; do nothing
        return None

    uuid = faq.data.insert(
        properties={
            "question": question,
            "answer": answer,
        },
        vector=vector,
    )
    return uuid


def search_near_vector(vector: list[float], limit: int = 3):
    """Search top-N nearest FAQ items by vector."""
    response = faq.query.near_vector(
        near_vector=vector,
        limit=limit,
        return_metadata=MetadataQuery(distance=True),
    )
    results = []
    for obj in response.objects:
        results.append(
            {
                "question": obj.properties.get("question"),
                "answer": obj.properties.get("answer"),
                "distance": obj.metadata.distance,
                "uuid": obj.uuid,
            }
        )
    return results


def close_client() -> None:
    client.close()


# Story Parts Collection Functions

def insert_story_part(part: str, vector: list[float]) -> str | None:
    """
    Insert a story part if it does not already exist (exact text match).
    Returns the UUID of the inserted object, or None if it already existed.
    """
    # Deduplicate by exact match on part text
    existing_filter = Filter.by_property("part").equal(part)
    existing = story_parts.query.fetch_objects(filters=existing_filter, limit=1)
    if existing.objects:
        # Already present; do nothing
        return None

    uuid = story_parts.data.insert(
        properties={
            "part": part,
        },
        vector=vector,
    )
    return uuid


def search_near_vector_story(vector: list[float], limit: int = 3):
    """Search top-N nearest story parts by vector."""
    response = story_parts.query.near_vector(
        near_vector=vector,
        limit=limit,
        return_metadata=MetadataQuery(distance=True),
    )
    results = []
    for obj in response.objects:
        results.append(
            {
                "part": obj.properties.get("part"),
                "distance": obj.metadata.distance,
                "uuid": obj.uuid,
            }
        )
    return results


def search_bm25_story(query: str, limit: int = 10):
    """Keyword/BM25 search on story parts."""
    response = story_parts.query.bm25(
        query=query,
        limit=limit,
        return_metadata=MetadataQuery(score=True),
    )
    results = []
    for obj in response.objects:
        results.append(
            {
                "part": obj.properties.get("part"),
                "score": getattr(obj.metadata, "score", None),
                "uuid": obj.uuid,
            }
        )
    return results


def search_hybrid_story(query: str, vector: list[float] | None = None, alpha: float = 0.5, limit: int = 10):
    """
    Hybrid search on story parts: combines keyword (BM25) and vector signals.
    alpha in [0,1]: 0 => pure keyword, 1 => pure vector.
    If vector is None, Weaviate will use keyword-only weighting per alpha.
    """
    response = story_parts.query.hybrid(
        query=query,
        alpha=alpha,
        vector=vector,
        limit=limit,
        return_metadata=MetadataQuery(score=True),
    )
    results = []
    for obj in response.objects:
        results.append(
            {
                "part": obj.properties.get("part"),
                "score": getattr(obj.metadata, "score", None),
                "uuid": obj.uuid,
            }
        )
    return results


# Story Parts Overlap Collection Functions

def insert_story_part_overlap(part: str, vector: list[float]) -> str | None:
    """
    Insert a story part overlap if it does not already exist (exact text match).
    Returns the UUID of the inserted object, or None if it already existed.
    """
    # Deduplicate by exact match on part text
    existing_filter = Filter.by_property("part").equal(part)
    existing = story_parts_overlap.query.fetch_objects(filters=existing_filter, limit=1)
    if existing.objects:
        # Already present; do nothing
        return None

    uuid = story_parts_overlap.data.insert(
        properties={
            "part": part,
        },
        vector=vector,
    )
    return uuid


def search_near_vector_story_overlap(vector: list[float], limit: int = 3):
    """Search top-N nearest story parts overlap by vector."""
    response = story_parts_overlap.query.near_vector(
        near_vector=vector,
        limit=limit,
        return_metadata=MetadataQuery(distance=True),
    )
    results = []
    for obj in response.objects:
        results.append(
            {
                "part": obj.properties.get("part"),
                "distance": obj.metadata.distance,
                "uuid": obj.uuid,
            }
        )
    return results


def search_bm25_story_overlap(query: str, limit: int = 10):
    """Keyword/BM25 search on story parts overlap."""
    response = story_parts_overlap.query.bm25(
        query=query,
        limit=limit,
        return_metadata=MetadataQuery(score=True),
    )
    results = []
    for obj in response.objects:
        results.append(
            {
                "part": obj.properties.get("part"),
                "score": getattr(obj.metadata, "score", None),
                "uuid": obj.uuid,
            }
        )
    return results


def search_hybrid_story_overlap(query: str, vector: list[float] | None = None, alpha: float = 0.5, limit: int = 10):
    """
    Hybrid search on story parts overlap: combines keyword (BM25) and vector signals.
    alpha in [0,1]: 0 => pure keyword, 1 => pure vector.
    If vector is None, Weaviate will use keyword-only weighting per alpha.
    """
    response = story_parts_overlap.query.hybrid(
        query=query,
        alpha=alpha,
        vector=vector,
        limit=limit,
        return_metadata=MetadataQuery(score=True),
    )
    results = []
    for obj in response.objects:
        results.append(
            {
                "part": obj.properties.get("part"),
                "score": getattr(obj.metadata, "score", None),
                "uuid": obj.uuid,
            }
        )
    return results


def search_bm25(query: str, limit: int = 10):
    """Keyword/BM25 search (TF-IDF-style scoring)."""
    response = faq.query.bm25(
        query=query,
        limit=limit,
        return_metadata=MetadataQuery(score=True),
    )
    results = []
    for obj in response.objects:
        results.append(
            {
                "question": obj.properties.get("question"),
                "answer": obj.properties.get("answer"),
                "score": getattr(obj.metadata, "score", None),
                "uuid": obj.uuid,
            }
        )
    return results


def search_hybrid(query: str, vector: list[float] | None = None, alpha: float = 0.5, limit: int = 10):
    """
    Hybrid search: combines keyword (BM25) and vector signals.
    alpha in [0,1]: 0 => pure keyword, 1 => pure vector.
    If vector is None, Weaviate will use keyword-only weighting per alpha.
    The alpha parameter controls the weighting of the two signals, not the proportion of results.
    How Hybrid Search Actually Works:
        alpha = 0.5 means:
        50% weight to keyword (BM25) score
        50% weight to vector (semantic) score
    Final score = alpha × BM25_score + (1-alpha) × vector_score
    """
    response = faq.query.hybrid(
        query=query,
        alpha=alpha,
        vector=vector,
        limit=limit,
        return_metadata=MetadataQuery(score=True),
    )
    results = []
    for obj in response.objects:
        results.append(
            {
                "question": obj.properties.get("question"),
                "answer": obj.properties.get("answer"),
                "score": getattr(obj.metadata, "score", None),
                "uuid": obj.uuid,
            }
        )
    return results


