from src.config import get_neo4j_driver, get_logger, NEO4J_DATABASE
from difflib import get_close_matches

driver = get_neo4j_driver()

def graph_search(query: str) -> list[dict]:
    """
    Extract an artist name from the query and return their known
    relationships via graph traversal.
    """
    with driver.session(database=NEO4J_DATABASE) as session:
        # step 1: find which known artist is mentioned in the query
        # step 2: run the Cypher traversal for that artist
        # step 3: format results as list[dict], consistent with your other retrieval functions
        ...
        result = session.run("MATCH (a:Artist) RETURN a.name AS name")
        known_artists = [record["name"] for record in result]
    
        matched_artist = None
        for artist in known_artists:
            if artist.lower() in query.lower():
                matched_artist = artist
                break
        
        if matched_artist is None:
            return []
        else:
            result = session.run(
                "MATCH (a:Artist {name:$name})-[r]->(b:Artist) RETURN type(r) AS relationship, b.name AS related_artist",
                name=matched_artist
            )
            return [{
                'artist': matched_artist,
                'relationship': record['relationship'],
                'related_artist': record['related_artist']
            } for record in result]


def get_known_artists() -> list[str]:
    """
    Fetch all known artist names from the graph
    """
    with driver.session(database=NEO4J_DATABASE) as session:
        result = session.run("MATCH (a:Artist) RETURN a.name AS name")
        return [record['name'] for record in result]


def correct_artist_names(text: str) -> str:
    """
    Fuzzy-match words in transcribed text against known artist names,
    correcting near-misses from STT.
    """
    known_artists = get_known_artists()
    
    for artist in known_artists:
        matches = get_close_matches(artist, text.split(), n=1, cutoff=0.8)
        if matches:
            text = text.replace(matches[0], artist)
    
    return text

def find_connection_path(artist1: str, artist2: str, max_hops: int = 3) -> str:
    """
    Find the shortest connection path between two known artists,
    up to max_hops relationship steps.
    """
    with driver.session(database=NEO4J_DATABASE) as session:
        result = session.run(
            f"""
            MATCH path = shortestPath((a:Artist {{name: $artist1}})-[*1..{max_hops}]-(b:Artist {{name: $artist2}}))
            RETURN [node in nodes(path) | node.name] AS names,
                   [rel in relationships(path) | type(rel)] AS relationship_types
            """,
            artist1=artist1, artist2=artist2
        )
        record = result.single()
    
    if record is None:
        return f"No connection found between {artist1} and {artist2} within {max_hops} hops."
    
    names = record['names']
    rel_types = record['relationship_types']
    
    path_description = names[0]
    for i, rel_type in enumerate(rel_types):
        path_description += f" --[{rel_type}]--> {names[i+1]}"
    
    return path_description

def find_mentioned_artists(query: str) -> list[str]:
    """
    Return all known artists mentioned in the query (substring match).
    """
    known_artists = get_known_artists()
    return [artist for artist in known_artists if artist.lower() in query.lower()]


def get_artist_graph_context(query: str) -> str:
    """
    If a known artist is mentioned in the query, return a short
    text summary of their known relationships, for use as
    supplementary context. Returns an empty string if no artist found.
    """
    known_artists = get_known_artists()
    
    matched_artist = None
    for artist in known_artists:
        if artist.lower() in query.lower():
            matched_artist = artist
            break
    
    if matched_artist is None:
        return ''
    
    with driver.session(database=NEO4J_DATABASE) as session:
        result = session.run(
            "MATCH (a:Artist {name: $name})-[r]->(b:Artist) RETURN type(r) AS relationship, b.name AS related_artist",
            name=matched_artist
        )
        relationships = [f"{matched_artist} has relationship {r['relationship']} with {r['related_artist']}" for r in result]
    
    if not relationships:
        return ''
    
    return "Known relationships:\n" + "\n".join(relationships)