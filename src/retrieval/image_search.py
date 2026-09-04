"""
Cross-modal (text-to-image) retrieval over album cover art, using
CLIP's shared embedding space.
"""

from sentence_transformers import SentenceTransformer
from src.config import get_connection, get_logger
from PIL import Image
from io import BytesIO
import requests

logger = get_logger(__name__)
conn = get_connection()
clip_model = SentenceTransformer('clip-ViT-B-32')


def search_covers_by_text(query: str, top_k: int = 5) -> list[dict]:
    """
    Embed a text query using CLIP and find the most visually/semantically
    similar album covers, via cosine distance in the shared embedding space.
    """
    query_embedding = clip_model.encode(query).tolist()
    cursor = conn.cursor()

    cursor.execute(
        'SELECT artist, album, cover_url, embedding <=> %s::vector AS distance '
        'FROM album_covers '
        'ORDER BY embedding <=> %s::vector '
        'LIMIT %s;',
        (query_embedding, query_embedding, top_k)
    )

    results = []
    for artist, album, cover_url, distance in cursor.fetchall():
        results.append({
            'artist': artist,
            'album': album,
            'cover_url': cover_url,
            'distance': distance
        })

    return results




def search_covers_by_image(image_url: str, top_k: int = 5) -> list[dict]:
    """
    Given an album cover image URL, find visually similar covers
    via CLIP embedding similarity.
    """
    response = requests.get(image_url, timeout=15)
    image = Image.open(BytesIO(response.content))
    query_embedding = clip_model.encode(image).tolist()

    cursor = conn.cursor()
    cursor.execute(
        'SELECT artist, album, cover_url, embedding <=> %s::vector AS distance '
        'FROM album_covers '
        'ORDER BY embedding <=> %s::vector '
        'LIMIT %s;',
        (query_embedding, query_embedding, top_k)
    )

    results = []
    for artist, album, cover_url, distance in cursor.fetchall():
        results.append({
            'artist': artist,
            'album': album,
            'cover_url': cover_url,
            'distance': distance
        })

    return results


results = search_covers_by_image("http://coverartarchive.org/release/f00af81c-9249-49d0-b3f5-8b6725bd1900/28008351580.jpg")
for r in results:
    print(r['artist'], '-', r['album'], '-', round(r['distance'], 3))