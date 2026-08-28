from sentence_transformers import SentenceTransformer
from pathlib import Path
import logging
import json

DATA_DIR = Path(__file__).parent.parent / 'data'
CHUNKS_PATH = DATA_DIR / 'chunks' / 'wiki_chunks.json'
EMBED_PATH = DATA_DIR / 'embedding' / 'embedding_wiki.json'

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def embed_all_chunks(chunks_path: Path, output_path: Path) -> None:
    with open(chunks_path) as f:
        chunks = json.load(f)
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # build the list of embedding inputs, one per chunk, in the SAME order as `chunks`
    embedding_inputs = [f"{chunk['artist']}: {chunk['text']}" for chunk in chunks]  # your logic here - a list comprehension building
                              # f"{artist}: {text}" for each chunk
    
    logger.info(f'Encoding {len(embedding_inputs)} chunks...')
    embeddings = model.encode(embedding_inputs, show_progress_bar=True)
    
    # pair each chunk with its embedding - same order guarantee matters here
    for i, (chunk, embed) in enumerate(zip(chunks, embeddings)):  # your logic - loop through chunks and embeddings together, attach
        chunk['embedding'] = embed.tolist()    # each embedding to its chunk's 'embedding' field
    
    with open(output_path, 'w') as f:
        json.dump(chunks, f)  # note: no indent - embeddings make files huge, skip pretty-printing
    
    logger.info(f'Saved {len(chunks)} embedded chunks to {output_path}')
    

def main():
    embed_all_chunks(CHUNKS_PATH, EMBED_PATH)
    
if __name__ == '__main__':
    main()