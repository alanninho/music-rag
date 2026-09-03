"""
Redis-backed conversation history storage, keyed by session ID.
"""

import json
import redis

r = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)


def get_history(session_id: str) -> list[dict]:
    """
    Return the conversation history for a given session, or an empty
    list if no history exists yet.
    """
    raw = r.get(f"history:{session_id}")
    if raw is None:
        return []
    return json.loads(raw)


def add_to_history(session_id: str, role: str, content: str) -> None:
    """
    Append a message to a session's conversation history.
    Sessions expire after 1 hour of inactivity.
    """
    history = get_history(session_id)
    history.append({'role': role, 'content': content})
    r.set(f"history:{session_id}", json.dumps(history), ex=3600)