from fastapi import FastAPI, Depends, HTTPException, Header, Request
from pydantic import BaseModel
from src.generation import generate_answer
from src.config import get_logger

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

import os


logger = get_logger(__name__)


app = FastAPI()


limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


API_KEY = os.environ.get('API_KEY')
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

class AskRequest(BaseModel):
    question: str
    top_k: int = 5


@app.post('/ask')
@limiter.limit("5/minute")
def ask(request: Request, ask_request: AskRequest, api_key: str = Depends(verify_api_key)):
    answer = generate_answer(ask_request.question, ask_request.top_k)
    return {'answer': answer}

@app.get('/')
def root():
    return {'message': 'Music RAG API is running'}
