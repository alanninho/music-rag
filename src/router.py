"""
Query routing logic: decides whether to use graph search or
hybrid+rerank retrieval based on query intent.
"""

from src.graph_search import graph_search
from src.hybrid_retrieval import hybrid_search
from src.rerank import rerank
from src.config import get_logger

logger = get_logger(__name__)

RELATIONSHIP_KEYWORDS = [
    'collaborate', 'collaboration', 'member', 'band', 'group',
    'feud', 'married', 'relationship', 'related', 'sibling',
    'brother', 'sister', 'parent', 'child', 'family'
]


def is_relationship_query(query: str) -> bool:
    """
    Check if a query is likely asking about artist relationships,
    based on keyword signals.
    """
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in RELATIONSHIP_KEYWORDS)


def route_query(query: str, top_k: int = 5) -> list[dict]:
    """
    Route a query to the appropriate retrieval strategy: graph search
    for relationship questions, hybrid+rerank otherwise.
    """
    if is_relationship_query(query) is True:
        graph_results = graph_search(query)
        
        if graph_results:
            logger.info(f"Routed to graph search: {len(graph_results)} results")
            return [{
                'artist': r['artist'],
                'text': f"{r['artist']} has relationship {r['relationship']} with {r['related_artist']}"
            }
            for r in graph_results
            ]
            
    logger.info(f"Routed to hybrid search + rerank")
    candidates = hybrid_search(query, top_k=10)
    return rerank(query, candidates, top_k=top_k)