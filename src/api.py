from fastapi import FastAPI
from pydantic import BaseModel
from src.generation import generate_answer
from src.config import get_logger

logger = get_logger(__name__)

app = FastAPI()

class AskRequest(BaseModel):
    question: str
    top_k: int=5
    

@app.post('/ask')
def ask(request: AskRequest):
    answer = generate_answer(request.question, request.top_k)
    return {'answer': answer}

@app.get('/')
def root():
    return {'message': 'Music RAG API is running'}