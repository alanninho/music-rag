from sentence_transformers import CrossEncoder

reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def rerank(query: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
    '''
    Re-score candidate chunks against the query using a cross encoder,
    return the top k most relevant
    '''

    pairs = [(query, candidate['text']) for candidate in candidates]
    scores = reranker.predict(pairs) # list of floats per pair
    
    scores_pair = list(enumerate(scores))
    sorted_pairs = sorted(scores_pair, key=lambda x : x[1], reverse=True)
    top_results = sorted_pairs[:top_k]
    
    return [candidates[i] for i, score in top_results]
