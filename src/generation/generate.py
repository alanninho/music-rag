import ollama
from src.config import get_connection, get_logger
from src.retrieval.vector import retrieve
from src.retrieval.hybrid import hybrid_search
from src.retrieval.rerank import rerank
from src.retrieval.router import route_query
from src.generation.groundedness import check_groundedness
from src.config import groundedness_failures

client = ollama.Client(host='http://127.0.0.1:11434')

def generate_answer(query: str, top_k: int=5) -> str:
    '''
    Retrieve relevant chunks and generate an answer grounded in them.
    '''
    #candidates = hybrid_search(query, top_k)
    #chunks = rerank(query, candidates, top_k=top_k)
    
    chunks = route_query(query, top_k)
    
    context = ''
    for chunk in chunks:
        context += f"[{chunk['artist']}] {chunk['text']}\n\n\n"
        
    full_prompt = f'''
    Answer the question using the context below. If the context doesn't contain enough information to answer, say so.
    
    Context:
    {context}
    
    Question:
    {query}'''
    
    response = client.chat(model='llama3.2', messages=[
    {'role': 'user', 'content': full_prompt}
])
    answer = response['message']['content']
    
    groundedness = check_groundedness(answer, context)
    print(f"DEBUG: is_grounded = {groundedness['is_grounded']}")
    if not groundedness['is_grounded']:
        answer += "\n\nNote: this answer may not be fully supported by the retrieved context."
        groundedness_failures.inc()
    print(f"DEBUG: final answer = {answer[-100:]}")

    return answer