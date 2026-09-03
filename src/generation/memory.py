"""
Simple in-memory conversation history storage, keyed by session ID.
"""

conversation_store: dict[str, list[dict]] = {}


def get_history(session_id: str) -> list[dict]:
    """
    Return the conversation history for a given session, or an empty
    list if no history exists yet.
    """
    return conversation_store.get(session_id, [])


def add_to_history(session_id: str, role: str, content: str) -> None:
    """
    Append a message to a session's conversation history.
    """
    if session_id not in conversation_store:
        conversation_store[session_id] = []
    conversation_store[session_id].append({'role': role, 'content': content})