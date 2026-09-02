"""
Query routing logic: enriches retrieval with knowledge-graph context
(single-artist relationships or multi-artist connection paths) alongside
hybrid+rerank text retrieval.
"""

from src.graph_search import find_mentioned_artists, find_connection_path, get_artist_graph_context
from src.hybrid_retrieval import hybrid_search
from src.rerank import rerank
from src.config import get_logger

logger = get_logger(__name__)


def route_query(query: str, top_k: int = 5) -> list[dict]:
    """
    Route a query: use multi-hop graph path-finding when two artists
    are mentioned, single-artist graph context enrichment when one is
    mentioned, and pure hybrid+rerank retrieval otherwise.
    """
    mentioned_artists = find_mentioned_artists(query)

    if len(mentioned_artists) >= 2:
        logger.info(f'Routed to connection path search: {mentioned_artists[0]} <-> {mentioned_artists[1]}')
        path = find_connection_path(mentioned_artists[0], mentioned_artists[1])
        return [{'artist': 'graph', 'text': f"Connection path: {path}"}]

    logger.info('Routed to hybrid search + rerank')
    candidates = hybrid_search(query, top_k=10)
    text_chunks = rerank(query, candidates, top_k=top_k)

    if len(mentioned_artists) == 1:
        graph_context = get_artist_graph_context(query)
        if graph_context:
            logger.info('Enriched with single-artist graph context')
            text_chunks.append({'artist': 'graph', 'text': graph_context})

    return text_chunks