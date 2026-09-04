import json
from pprint import pprint # useful to print dict in a beautiful way in the terminal
from pathlib import Path
import logging

DATA_DIR = Path(__file__).parent.parent.parent / 'data'
RAW_PATH = DATA_DIR / 'raw' / 'musicbrainz_artists.json'
PROCESSED_PATH = DATA_DIR / 'processed' / 'mb_cleaned_artists.json'

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

def parse_artist(raw_artist : dict) -> dict:
    '''
    Extract and clean the fields needed for RAG from a raw MusicBrainz artist record.
    Filters out low-signal tags and MusicBrainz internal bookkeeping fields.
    '''
    clean = {
        'mbid': raw_artist['id'],
        'name': raw_artist['name'],
        'disambiguation': raw_artist['disambiguation'],  # decide: keep or drop, your earlier call
        'life_span': raw_artist['life-span'],       # what shape? just begin/end, or the whole dict as-is?
        'tags': [t['name'] for t in raw_artist['tags'] if t['count'] >= 3],            # filtered list of tag names, above your chosen count threshold
        'relations': [
            {
                'type' : r['type'],
                'artist name' : r['artist']['name'],
                'begin' : r['begin'],
                'end' : r['end']
                }
            for r in raw_artist['relations']],       # list of cleaned relation dicts (type, artist name, begin, end)
        'release_groups': [
            {
                'mbid': r['id'],
                'title' : r['title'],
                'first-release-date' : r['first-release-date'],
                'tags' : [t['name'] for t in r['tags'] if t['count'] >= 3]
                }
            for r in raw_artist['release-groups']],  # list of cleaned album dicts (title, first-release-date, maybe filtered tags)
    }
    return clean


def parse_all_artists(raw_path : Path, processed_path : Path) -> None:
    with open(raw_path) as f:
        data = json.load(f)
    
    processed = []
    
    for i, artist in enumerate(data):
        logger.info(f'Parsing artist #{i} out of {len(data)} : {artist["name"]}')
        processed.append(parse_artist(artist))
    
    logger.info(f'Parsed {len(processed)}/{len(data)} artists')
        
    with open(processed_path, 'w') as f:
        json.dump(processed, f, indent=2)
    
def main():
    parse_all_artists(RAW_PATH, PROCESSED_PATH)
    
if __name__ == '__main__':
    logger.info('Starting parsing')
    main()