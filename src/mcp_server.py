from mcp.server.mcpserver import MCPServer
from src.retrieval.hybrid import hybrid_search
from src.voice.stt import record_and_transcribe
from src.voice.tts import text_to_speech
from src.generation.generate import generate_answer

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

if __name__ == "__main__":
    mcp.run()