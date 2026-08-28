import requests, time, json, logging
from pathlib import Path

BASE_URL = "https://musicbrainz.org/ws/2/"  # MusicBrainz API root

HEADERS = {
    "User-Agent": "MusicRAG/1.0 ( alanmitouamona@gmail.com )"  # format: AppName/version (contact-or-purpose) - MusicBrainz requires this
}

RATE_LIMIT_DELAY = 1.2  # musicbrainz limit = 1 request/second but it's better to bump it up and avoid issues

DATA_DIR = Path(__file__).parent.parent / 'data'
SEED_ARTISTS_PATH = DATA_DIR / 'seed_artists.json' # path to seed list file
RAW_OUTPUT_PATH = DATA_DIR / "raw" / "musicbrainz_artists.json" # path to save ingestion results

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s") # format like 'timestamp, level of severity, message'
logger = logging.getLogger(__name__) # logger for this module

MAX_RETRIES = 5


def _rate_limited_get(url: str, params: dict) -> requests.Response:
    """
    Wraps requests.get with MusicBrainz's rate limit and raises on HTTP errors.
    Callers are responsible for catching exceptions and returning None on failure.
    Retries on 503 (server temporarily unavailable) with exponential backoff.
    """
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
            time.sleep(RATE_LIMIT_DELAY) # always pausing after attempting a request, succeed or fail


def search_artists(name : str) -> str | None:
    '''
    Search MusicBrainz for an artist by name.
    Returns the MBID of the best match, or None if not found.
    '''
    url = BASE_URL + 'artist'
    params = {
        'query': f'artist:"{name}"',
        'fmt': 'json',
        'limit': 3
    }
    
    try:
        response = _rate_limited_get(url, params=params)
        data = response.json()
        
        if data['artists'] == []: # when no artist found, empty list
            logger.warning(f'No artist found for {name}')
            return None
        else:
            logger.debug(f'{name} found') # debug level of severity because no need to print it since we found what we needed
            return max(data['artists'], key=lambda a: a['score'])['id'] # keeping the artist with the highest score, return MBID or None
        
    except requests.exceptions.RequestException as e:
        logger.warning(f'Failed to search {name} : {e}')
        return None


def get_artist_details(mbid : str) -> dict | None:
    '''
    Fetch full artist details from MusicBrainz, including release-groups, relationships, and tags.
    Returns the raw JSON response, or None if the request fails.
    '''
    url = BASE_URL + f'artist/{mbid}'
    params={
        'inc' : 'release-groups+artist-rels+tags',
        'fmt' : 'json'
    }
    
    try:
        response = _rate_limited_get(url, params=params)
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        logger.warning(f'Failed to fetch details for {mbid} : {e}')
        return None


def ingest_all_artists(seed_path: Path, output_path: Path) -> None:
    '''
    Reads the seed artist list, fetches search + details for each,
    and writes successfully-ingested results to output_path.
    '''
    with open(seed_path) as f: # 'with' block automatically closes when ends even if error
        seed_data = json.load(f) # loads for json file
        
    names = seed_data['artists'] # pull the artist name list out of your seed_artists.json structure
    
    results = []
    failed = []
    
    for i, name in enumerate(names, start=1):
        logger.info(f'Artist #{i} out {len(names)} : {name}')
        mbid = search_artists(name)
        
        if mbid is None:
            logger.warning(f'MBID not found for {name}')
            failed.append(name)
            continue
        
        details = get_artist_details(mbid=mbid)
        
        if details is None:
            logger.warning(f'No details fetched for {name}')
            failed.append(name)
            continue
        
        results.append(details)
            
    logger.info(f'Ingested {len(results)}/{len(names)}')
    if failed:
        logger.warning(f'Failed artists: {failed}')
        
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
        
def main():
    ingest_all_artists(SEED_ARTISTS_PATH, RAW_OUTPUT_PATH)
        
if __name__ == '__main__':
    logger.info('Starting ingestion')
    main()