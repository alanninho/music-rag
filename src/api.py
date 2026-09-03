from fastapi import FastAPI, Depends, HTTPException, Header, Request
from pydantic import BaseModel, Field
from src.generation.generate import generate_answer
from src.config import get_logger

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

import os

from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter


logger = get_logger(__name__)


app = FastAPI()



Instrumentator().instrument(app).expose(app)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


API_KEY = os.environ.get('API_KEY')
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

class AskRequest(BaseModel):
    question: str = Field(..., max_length=500)
    top_k: int = 5
    session_id: str = "default"


@app.post('/ask')
@limiter.limit("5/minute")
def ask(request: Request, ask_request: AskRequest, api_key: str = Depends(verify_api_key)):
    result = generate_answer(ask_request.question, session_id=ask_request.session_id, top_k=ask_request.top_k)
    return result  # already has 'answer' and 'sources' keys

@app.get('/')
def root():
    return {'message': 'Music RAG API is running'}
