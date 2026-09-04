"""
Embed album cover art using CLIP, for cross-modal (text-image)
retrieval alongside the existing text-based pipeline.
"""

import json
import logging
from pathlib import Path
from io import BytesIO

import requests
from PIL import Image
from sentence_transformers import SentenceTransformer

DATA_DIR = Path(__file__).parent.parent.parent / 'data'
COVERS_PATH = DATA_DIR / 'processed' / 'album_covers.json'
EMBEDDED_COVERS_PATH = DATA_DIR / 'embedding' / 'embedded_covers.json'

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

clip_model = SentenceTransformer('clip-ViT-B-32')


def embed_image_from_url(image_url: str):
    """
    Download an image from a URL and return its CLIP embedding.
    Returns None if the download or embedding fails.
    """
    try:
        response = requests.get(image_url, timeout=15)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        return clip_model.encode(image)
    except Exception as e:
        logger.warning(f'Failed to embed image from {image_url}: {e}')
        return None


def embed_all_covers(covers_path: Path, output_path: Path) -> None:
    """
    Embed every album cover in the covers file, saving results with
    embeddings attached.
    """
    with open(covers_path) as f:
        covers = json.load(f)

    embedded = []
    for i, cover in enumerate(covers):
        logger.info(f'Embedding cover #{i + 1}/{len(covers)}: {cover["artist"]} - {cover["album"]}')
        embedding = embed_image_from_url(cover['cover_url'])
        if embedding is not None:
            cover['embedding'] = embedding.tolist()
            embedded.append(cover)

    with open(output_path, 'w') as f:
        json.dump(embedded, f)

    logger.info(f'Embedded {len(embedded)}/{len(covers)} covers')


def main():
    embed_all_covers(COVERS_PATH, EMBEDDED_COVERS_PATH)


if __name__ == '__main__':
    main()