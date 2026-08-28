import json
from pprint import pprint # useful to print dict in a beautiful way in the terminal
from pathlib import Path
import logging
import re

DATA_DIR = Path(__file__).parent.parent / 'data'
RAW_PATH = DATA_DIR / 'raw' / 'wikipedia_artists.json'
PROCESSED_PATH = DATA_DIR / 'processed' / 'wiki_cleaned_artists.json'

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)




def split_into_section(text:str) -> list[dict]:
    
    
    pattern = r'\n==+\s*(.+?)\s*==+\n'
    
    splitted_text = re.split(pattern, text)
    
    sections = []
    if splitted_text[0].strip():
        sections.append({
            'section': 'intro',
            'text': splitted_text[0].strip()
            })
    
    for i in range(1, len(splitted_text), 2):
        stripped_text = splitted_text[i+1].strip()
        if stripped_text: # skips if empty string (falsy)
            sections.append({
                'section': splitted_text[i],
                'text': stripped_text
                })
        
    return sections


def split_into_section_all_artists(raw_path: Path, processed_path: Path) -> None:
    with open(raw_path) as f:
        data = json.load(f)
    
    processed = []
    
    for i, artist in enumerate(data):
        logger.info(f'Parsing artist #{i} out of {len(data)} : {artist["name"]}')
        processed.append({
    'name': artist['name'],
    'sections': split_into_section(artist['extract'])
})
    
    logger.info(f'Parsed {len(processed)}/{len(data)} artists')
            
    with open(processed_path, 'w') as f:
        json.dump(processed, f, indent=2)
    
    
def main():
    split_into_section_all_artists(RAW_PATH, PROCESSED_PATH)
    
    
if __name__ == '__main__':
    logger.info('Starting parsing')
    main()