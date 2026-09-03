import json, logging, psycopg2
from pathlib import Path
from dotenv import load_dotenv
import os

DATA_DIR = Path(__file__).parent.parent / 'data'
EMBED_PATH = DATA_DIR / 'embedding' / 'embedding_wiki.json'

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

db_password = os.environ.get('DB_PASSWORD')
db_host = os.environ.get('DB_HOST')
db_name = os.environ.get('DB_NAME')
db_user = os.environ.get('DB_USER')

conn = psycopg2.connect(
    host=db_host,
    dbname=db_name,
    user=db_user,
    password=db_password
)

cursor = conn.cursor()

def load_chunks_to_db(embed_path: Path) -> None:
    with open(embed_path) as f:
        chunks = json.load(f)
    
    logger.info(f'Inserting {len(chunks)} chunks into wiki_chunks table...')
    
    failed = []
    
    for i, chunk in enumerate(chunks):
        try:
            cursor.execute(
                'INSERT INTO wiki_chunks (artist, section, text, embedding) VALUES (%s, %s, %s, %s)',
                (chunk['artist'], chunk['section'], chunk['text'], chunk['embedding'])
            )
        except Exception as e:
            logger.warning(f'Failed to insert chunk {i} ({chunk["artist"]} - {chunk["section"]}): {e}')
            failed.append(chunk)
            conn.rollback()  # reset the connection to a clean state after a failed insert
            continue

        if (i + 1) % 100 == 0:
            logger.info(f'Inserted {i + 1}/{len(chunks)}')
        
    conn.commit()

    logger.info(f'Committed {len(chunks) - len(failed)}/{len(chunks)} chunks to database')
    if failed:
        logger.warning(f'{len(failed)} chunks failed to insert')
    
    
    cursor.close()
    conn.close()
    

def main():
    load_chunks_to_db(EMBED_PATH)
    
if __name__ == '__main__':
    main()