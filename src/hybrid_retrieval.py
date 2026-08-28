from src.config import get_logger, get_connection
from src.retrieval import retrieve
from src.metrics import reciprocal_rank_fusion
from rank_bm25 import BM25Okapi

logger = get_logger(__name__)
conn = get_connection()


def _load_corpus() -> list[dict]:
    '''Load all the chunks from the database, for building the BM25 index'''
    cursor = conn.cursor()
    cursor.execute('SELECT id, artist, section, text FROM wiki_chunks;')
    rows = cursor.fetchall()
    
    return [
        {'id': id, 'artist': artist, 'section': section, 'text': text}
        for id, artist, section, text in rows
    ]
    
#built once, at module load time
corpus = _load_corpus()
tokenized_corpus = [chunk['text'].split() for chunk in corpus]
bm25 = BM25Okapi(tokenized_corpus)


def bm25_search(query: str, top_k: int = 5) -> list[dict]:
    '''
    Search the corpus using BM25 keyword matching, return the top_k chunks
    '''
    
    tokenized_query = query.split()
    scores = bm25.get_scores(tokenized_query)
    indexed_scores = list(enumerate(scores))
    sorted_scores = sorted(indexed_scores, key=lambda x: x[1], reverse=True)
    top_results = sorted_scores[:top_k]
    
    return [corpus[index] for index, score in top_results]





def hybrid_search(query: str, top_k: int = 5, vector_weight: float = 0.7, bm25_weight: float = 0.3) -> list[dict]:
    """
    Combine vector and BM25 retrieval via Reciprocal Rank Fusion.
    """
    vector_results = retrieve(query, top_k=10)
    bm25_results = bm25_search(query, top_k=10)
    combined = reciprocal_rank_fusion(vector_results, bm25_results, vector_weight=vector_weight, bm25_weight=bm25_weight)
    return combined[:top_k]