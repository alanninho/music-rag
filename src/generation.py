import ollama
from src.config import get_connection, get_logger
from src.retrieval import retrieve
from src.hybrid_retrieval import hybrid_search
from src.rerank import rerank


def generate_answer(query: str, top_k: int=10) -> str:
    '''
    Retrieve relevant chunks and generate an answer grounded in them.
    '''
    candidates = hybrid_search(query, top_k)
    chunks = rerank(query, candidates, top_k=top_k)
    
    context = ''
    for chunk in chunks:
        context += f"[{chunk['artist']}] {chunk['text']}\n\n\n"
        
    full_prompt = f'''
    Answer the question using the context below. If the context doesn't contain enough information to answer, say so.
    
    Context:
    {context}
    
    Question:
    {query}'''
    
    response = ollama.chat(model='llama3.2', messages=[
    {'role': 'user', 'content': full_prompt}
])
    return response['message']['content']