from mcp.server.mcpserver import MCPServer
from src.retrieval.hybrid import hybrid_search
from src.voice.stt import record_and_transcribe
from src.voice.tts import text_to_speech
from src.generation.generate import generate_answer
from src.retrieval.image_search import search_covers_by_text
from mcp.server.mcpserver import Image
import requests



mcp = MCPServer("music-rag-server")

@mcp.tool()
def search_music_database(query: str, top_k: int = 5) -> str:
    """
    Search the music knowledge base for information about 90s hip-hop artists.
    Returns relevant text passages about artists, albums, and events.
    """
    results = hybrid_search(query, top_k=top_k)
    return "\n\n".join(f"[{r['artist']}] {r['text']}" for r in results)


@mcp.tool()
def ask_by_voice(duration_seconds: int = 5) -> str:
    """
    Record a spoken question from the microphone for the given duration,
    transcribe it, and correct common artist name misspellings.
    Returns the corrected question text.
    """
    return record_and_transcribe(duration_seconds)


@mcp.tool()
def speak_answer(text: str) -> str:
    """
    Convert text into spoken audio, saved as a .wav file.
    Returns the path to the generated audio file.
    """
    return text_to_speech(text)


@mcp.tool()
def get_answer(query: str):
    return generate_answer(query)



@mcp.tool()
def find_similar_covers(description: str, top_k: int = 1) -> Image:
    """
    Find the album cover most visually similar to a text description
    (e.g. 'dark and gritty', 'colorful and vibrant') using CLIP
    cross-modal search, and return the actual image.
    """
    results = search_covers_by_text(description, top_k=top_k)
    if not results:
        raise ValueError("No matching cover found")

    best = results[0]
    response = requests.get(best['cover_url'], timeout=15)
    response.raise_for_status()
    return Image(data=response.content, format='jpg')

if __name__ == "__main__":
    mcp.run()