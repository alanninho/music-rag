from src.hybrid_retrieval import hybrid_search
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("music-rag-server")

@mcp.tool()
def search_music_database(query: str, top_k: int = 5) -> str:
    """
    Search the music knowledge base for information about 90s hip-hop artists.
    Returns relevant text passages about artists, albums, and events.
    """
    results = hybrid_search(query, top_k=top_k)
    return "\n\n".join(f"[{r['artist']}] {r['text']}" for r in results)

if __name__ == "__main__":
    mcp.run()