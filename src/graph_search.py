from src.config import get_neo4j_driver, get_logger, NEO4J_DATABASE

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
