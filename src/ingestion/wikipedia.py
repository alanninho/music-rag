"""
Wikipedia ingestion for the Music RAG project.

Fetches full article extracts for the seed artist list, to be used
as unstructured source text for chunking (unlike the structured
MusicBrainz metadata).
"""

import json
import time
import logging
from pathlib import Path

import requests

WIKI_BASE_URL = "https://en.wikipedia.org/w/api.php"
HEADERS = {
    "User-Agent": "MusicRAG/1.0 ( alanmitouamona@gmail.com )"  # same convention as MusicBrainz - descriptive app name + contact
}

RATE_LIMIT_DELAY = 1  # Wikipedia is looser than MusicBrainz, but still be deliberate about a value
MAX_RETRIES = 5

DATA_DIR = Path(__file__).parent.parent / 'data'
SEED_ARTISTS_PATH = DATA_DIR / 'seed_artists.json'
RAW_WIKI_OUTPUT_PATH = DATA_DIR / 'raw' / 'wikipedia_artists.json'  # pick a filename, distinct from musicbrainz_artists.json

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def _rate_limited_get(url: str, params: dict) -> requests.Response:
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, params=params, headers=HEADERS)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            if response.status_code == 503 and attempt < MAX_RETRIES-1:
                wait_time = RATE_LIMIT_DELAY * (2 ** attempt)
                time.sleep(wait_time)
                continue
            else:
                raise
        finally:
            time.sleep(RATE_LIMIT_DELAY)


def get_wikipedia_extract(title: str) -> str | None:
    """
    Fetch the full plain-text extract of a Wikipedia article by title.
    Returns the article text, or None if the page doesn't exist.
    """
    params = {
        'action': 'query',
        'titles': title,
        'prop': 'extracts',
        'explaintext': True,  # strips HTML/wiki markup, gives plain text
        'format': 'json',
    }

    try:
        response = _rate_limited_get(WIKI_BASE_URL, params=params)
        data = response.json()

        # NEW/UNUSUAL PART: MediaWiki's response nests the actual page data
        # under a dynamically-generated page ID, not a fixed key. The shape is:
        # data['query']['pages'] = {"<page_id>": {"title": ..., "extract": ...}}
        # Since you don't know the page_id in advance, you need to pull out
        # whatever single value that inner dict holds:
        pages = data['query']['pages']
        page = next(iter(pages.values()))  # gets the one (and only) value, regardless of its key

        # A missing page comes back with a 'missing' key instead of 'extract' -
        # check for that before assuming 'extract' exists
        if 'missing' in page:
            logger.info(f'The page for {title} is missing')
            return None # your logic: check if page is missing, return None if so
        
        return page['extract']
    
    except requests.exceptions.RequestException as e:
        logger.info(f'Failed to extract page for {title} : {e}')
        return None


def ingest_all_wikipedia(seed_path: Path, output_path: Path) -> None:
    with open(seed_path) as f:
        data = json.load(f)
    
    names = data['artists']
    ingested = []
    failed = []
    
    for i, artist in enumerate(names):
        logger.info(f'Wikipedia ingestion for artist #{i} out of {len(names)} - {artist}')
        extract = get_wikipedia_extract(artist)
        if extract is None:
            failed.append(artist)
            continue
        ingested.append({'name': artist, 'extract': extract})
    
    logger.info(f'Ingested {len(ingested)}/{len(names)}')
    if failed:
            logger.warning(f'Failed artists: {failed}')
        
    with open(output_path, 'w') as f:
        json.dump(ingested, f, indent=2)
        # same orchestration shape as ingest_all_artists: load names, loop,
        # call get_wikipedia_extract, collect results + failures, save raw


def main():
    ingest_all_wikipedia(SEED_ARTISTS_PATH, RAW_WIKI_OUTPUT_PATH)


if __name__ == '__main__':
    main()