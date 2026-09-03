import ollama
from src.config import get_connection, get_logger
from src.retrieval.vector import retrieve
from src.retrieval.hybrid import hybrid_search
from src.retrieval.rerank import rerank
from src.retrieval.router import route_query
from src.generation.groundedness import check_groundedness
from src.config import groundedness_failures
from src.generation.memory import get_history, add_to_history
from src.generation.query_rewriter import rewrite_query_with_history

client = ollama.Client(host='http://127.0.0.1:11434')


def generate_answer(query: str, session_id: str = "default", top_k: int = 5) -> dict:
    rewritten_query = rewrite_query_with_history(query, session_id)
    chunks = route_query(rewritten_query, top_k=top_k)
    
    if not chunks:
        answer = "I don't have information about that in my knowledge base. Try asking about a specific 90s hip-hop artist, their albums, or their collaborations."
        add_to_history(session_id, 'user', query)
        add_to_history(session_id, 'assistant', answer)
        return {'answer': answer, 'sources': []}
    
    history = get_history(session_id)
    context = ''
    sources = []
    for chunk in chunks:
        context += f"[{chunk['artist']}] {chunk['text']}\n\n\n"
        sources.append({'artist': chunk.get('artist', 'unknown'), 'section': chunk.get('section', 'N/A')})
    
    messages = [{'role': 'system', 'content': f"Answer using only the context below.\n\nContext:\n{context}"}]
    messages.extend(history)
    messages.append({'role': 'user', 'content': query})
    
    response = client.chat(model='llama3.2', messages=messages)
    answer = response['message']['content']
    
    groundedness = check_groundedness(answer, context)
    if not groundedness['is_grounded']:
        groundedness_failures.inc()
        answer = "I found some related information, but I'm not confident enough in the answer to state it as fact. Here's what I found:\n\n" + answer
    
    add_to_history(session_id, 'user', query)
    add_to_history(session_id, 'assistant', answer)
    
    return {'answer': answer, 'sources': sources}
