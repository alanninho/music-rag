"""
Load embedded album cover art into pgvector.
"""

import json
import logging
from pathlib import Path

from src.config import get_connection

DATA_DIR = Path(__file__).parent.parent.parent / 'data'
EMBEDDED_COVERS_PATH = DATA_DIR / 'embedding' / 'embedded_covers.json'

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

conn = get_connection()


def load_covers_to_db(embedded_covers_path: Path) -> None:
    """
    Load all embedded album covers into the album_covers table.
    """
    with open(embedded_covers_path) as f:
        covers = json.load(f)

    cursor = conn.cursor()
    logger.info(f'Inserting {len(covers)} covers into album_covers table...')

    failed = []
    for i, cover in enumerate(covers):
        try:
            cursor.execute(
                'INSERT INTO album_covers (artist, album, mbid, cover_url, embedding) VALUES (%s, %s, %s, %s, %s)',
                (cover['artist'], cover['album'], cover['mbid'], cover['cover_url'], cover['embedding'])
            )
        except Exception as e:
            logger.warning(f'Failed to insert cover for {cover["artist"]} - {cover["album"]}: {e}')
            failed.append(cover)
            conn.rollback()
            continue

        if (i + 1) % 10 == 0:
            logger.info(f'Inserted {i + 1}/{len(covers)}')

    conn.commit()

    logger.info(f'Committed {len(covers) - len(failed)}/{len(covers)} covers to database')
    if failed:
        logger.warning(f'{len(failed)} covers failed to insert')

    cursor.close()
    conn.close()


def main():
    load_covers_to_db(EMBEDDED_COVERS_PATH)


if __name__ == '__main__':
    main()