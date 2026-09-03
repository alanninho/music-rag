from src.config import DATA_DIR, get_connection, get_logger
from sentence_transformers import SentenceTransformer

logger = get_logger(__name__)
conn = get_connection()
model = SentenceTransformer('all-MiniLM-L6-v2')

def retrieve(query: str, top_k: int=5) -> list[dict]:
    """
    Embed the query and return the top_k most similar chunks from pgvector.
    """
    results = []
    embed_query = model.encode(query).tolist()
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT id, artist, section, text, embedding <=> %s::vector AS distance '
        'FROM wiki_chunks '
        'ORDER BY embedding <=> %s::vector '
        'LIMIT %s;',
        (embed_query, embed_query, top_k)
    )
    
    results_sql = cursor.fetchall()
    
    for id, artist, section, text, distance in results_sql:
        results.append({
            'id': id,
            'artist': artist,
            'section': section,
            'text': text,
            'distance': distance
        })
        
    return results
