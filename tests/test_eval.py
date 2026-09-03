from src.evaluation.metrics import precision_at_k, recall_at_k, reciprocal_rank_fusion


def test_precision_at_k_full_overlap():
    result = precision_at_k([1, 2, 3], [1, 2, 3])
    assert result == 1.0

def test_precision_at_k_no_overlap():
    result = precision_at_k([1, 2, 3], [4, 5, 6])
    assert result == 0.0

def test_precision_at_k_partial_overlap():
    result = precision_at_k([1, 2, 3], [1, 5, 6])
    assert result != 0.0

def test_precision_at_k_empty_golden():
    result = precision_at_k([1, 2, 3], [])
    assert result == 0.0

def test_recall_at_k_full_overlap():
    result = recall_at_k([1, 2, 3], [1, 2, 3])
    assert result == 1.0

def test_recall_at_k_no_overlap():
    result = recall_at_k([1, 2, 3], [4, 5, 6])
    assert result == 0.0

def test_recall_at_k_partial_overlap():
    result = recall_at_k([1, 2, 3], [1, 5, 6])
    assert result != 0.0

def test_recall_at_k_empty_golden():
    result = recall_at_k([1, 2, 3], [])
    assert result == 0.0

def test_reciprocal_rank_fusion_combines_duplicate_chunk():
    vector_results = [{'id': 1, 'text': 'a'}, {'id': 2, 'text': 'b'}]
    bm25_results = [{'id': 2, 'text': 'b'}, {'id': 3, 'text': 'c'}]
    
    result = reciprocal_rank_fusion(vector_results, bm25_results, vector_weight=0.7, bm25_weight=0.3)
    result_ids = [r['id'] for r in result]
    
    assert len(result) == 3
    assert 2 in result_ids