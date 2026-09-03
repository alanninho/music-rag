def precision_at_k(retrieved_ids: list[int], golden_ids: list[int]) -> float:
    """
    What fraction of retrieved chunks are actually relevant?
    """
    if not golden_ids:
        return 0.0
    else:
        retrieved_set = set(retrieved_ids)
        golden_set = set(golden_ids)
        overlap = retrieved_set & golden_set
        return len(overlap) / len(retrieved_set)


def recall_at_k(retrieved_ids: list[int], golden_ids: list[int]) -> float:
    """
    What fraction of relevant chunks were actually retrieved?
    """
    if not golden_ids:
        return 0.0
    else:
        retrieved_set = set(retrieved_ids)
        golden_set = set(golden_ids)
        overlap = retrieved_set & golden_set
        return len(overlap) / len(golden_set)

def reciprocal_rank_fusion(vector_results: list[dict], bm25_results: list[dict], vector_weight: int, bm25_weight: int, k: int=60) -> list[dict]:
    '''
    Combine two ranked result lists using Reciprocal Rank Fusion
    '''
    scores = {}
    
    for rank, chunk in enumerate(vector_results, start=1):
        chunk_id = chunk['id']
        contribution = 1 / (k + rank)
        
        if chunk_id not in scores:
            scores[chunk_id] = {'score': 0, 'chunk': chunk}
        
        scores[chunk_id]['score'] += vector_weight*contribution
        
    for rank, chunk in enumerate(bm25_results, start=1):
        chunk_id = chunk['id']
        contribution = 1 / (k + rank)
        
        if chunk_id not in scores:
            scores[chunk_id] = {'score': 0, 'chunk': chunk}
        
        scores[chunk_id]['score'] += bm25_weight*contribution
        
    sorted_results = sorted(scores.values(), key=lambda x: x['score'], reverse=True)
    return [entry['chunk'] for entry in sorted_results]