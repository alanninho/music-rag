"""
Rewrites follow-up queries into self-contained ones using conversation
history, so retrieval doesn't fail on pronouns or implicit references.

Uses a deterministic heuristic rather than an LLM call: if the query
doesn't mention any known artist, substitute the most recently
discussed artist from history.
"""

from src.generation.memory import get_history
from src.retrieval.graph_search import find_mentioned_artists


def rewrite_query_with_history(query: str, session_id: str) -> str:
    """
    If the query mentions no known artist but prior history exists,
    prepend the most recently discussed artist's name for retrieval purposes.
    Returns the original query unchanged if it already names an artist,
    or if no relevant history is found.
    """
    if find_mentioned_artists(query):
        return query

    history = get_history(session_id)
    if not history:
        return query

    for message in reversed(history):
        if message['role'] != 'user':
            continue
        mentioned = find_mentioned_artists(message['content'])
        if mentioned:
            return f"{mentioned[0]}: {query}"

    return query