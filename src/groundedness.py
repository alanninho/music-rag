"""
Groundedness checking: verifies whether a generated answer is
actually supported by its retrieved context, using LLM-as-judge.
"""

import ollama
from src.config import get_logger

logger = get_logger(__name__)

client = ollama.Client(host='http://127.0.0.1:11434')


def check_groundedness(answer: str, context: str) -> dict:
    """
    Use the LLM to judge whether the answer is supported by the context.
    Returns a groundedness verdict and reasoning.
    """
    prompt = f"""You are evaluating whether an answer is factually grounded in the given context.

Context:
{context}

Answer:
{answer}

Is this answer fully supported by the context, with no unsupported claims? Respond with exactly one word first (YES or NO), followed by a brief one-sentence explanation.
"""
    response = client.chat(
    model='llama3.2',
    messages=[{'role': 'user', 'content': prompt}],
    options={'temperature': 0}
)
    verdict_text = response['message']['content']

    is_grounded = verdict_text.strip().upper().startswith('YES')

    if not is_grounded:
        logger.warning(f'Groundedness check FAILED: {verdict_text}')

    return {
        'is_grounded': is_grounded,
        'explanation': verdict_text
    }