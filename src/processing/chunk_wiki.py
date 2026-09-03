
import json
import time
import logging
import re
import tiktoken
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / 'data'
SECTIONS_PATH = DATA_DIR / 'processed' / 'wiki_cleaned_artists.json'
CHUNKS_OUTPUT_PATH = DATA_DIR / 'chunks' / 'wiki_chunks.json'

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

def chunk_section(text: str, max_tokens: int= 350, overlap_tokens: int = 50) -> list[str]:
    encoding = tiktoken.get_encoding("cl100k_base")
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk_sentences = []
    current_token_count = 0
    
    for sentence in sentences:
        sentence_tokens = len(encoding.encode(sentence))
        
        if current_token_count + sentence_tokens > max_tokens and current_chunk_sentences:
            # finalize the current chunk
            chunks.append(' '.join(current_chunk_sentences))
            
            # carry over overlap: keep trimming from the front until
            # what's left is <= overlap_tokens
            while current_token_count > overlap_tokens and current_chunk_sentences:  # your logic here - a while loop, popping from the front
                first_sentence = current_chunk_sentences.pop(0)     # of current_chunk_sentences and recalculating token count,
                current_token_count -= len(encoding.encode(first_sentence)) # until it's small enough
        current_chunk_sentences.append(sentence)
        current_token_count += sentence_tokens
            
    if current_chunk_sentences:
        chunks.append(' '.join(current_chunk_sentences))

    return chunks


def chunk_all_artists(sections_path: Path, output_path: Path) -> None:
    with open(sections_path) as f:
        data = json.load(f)
    
    all_chunks = []
    
    for i, artist in enumerate(data):
        logger.info(f'Chunking artist #{i} out of {len(data)}: {artist["name"]}')
        
        for section in artist['sections']:
            section_chunks = chunk_section(section['text'])
            
            for chunk_text in section_chunks:
                all_chunks.append({
                    'artist' : artist['name'],
                    'section' : section['section'],
                    'text' :  chunk_text # what fields does each chunk record need?
                         # think about what you'd need later to retrieve
                         # and display this chunk meaningfully
                })
    
    logger.info(f'Produced {len(all_chunks)} total chunks from {len(data)} artists')
    
    with open(output_path, 'w') as f:
        json.dump(all_chunks, f, indent=2)


def main():
    chunk_all_artists(SECTIONS_PATH, CHUNKS_OUTPUT_PATH)
    

if __name__ == '__main__':
    main()