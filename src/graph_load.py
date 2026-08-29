"""
Load MusicBrainz relations data into Neo4j as a knowledge graph.
"""

import json
import re
from src.config import get_neo4j_driver, get_logger, DATA_DIR, NEO4J_DATABASE

logger = get_logger(__name__)
driver = get_neo4j_driver()

def _normalize_relation_type(raw_type: str) -> str:
    """
    Convert a MusicBrainz relation type like 'member of band' into a
    valid Cypher relationship type like 'MEMBER_OF_BAND'.
    """
    return raw_type.upper().replace(' ', '_')


def load_relations_to_graph(cleaned_artists_path) -> None:
    """
    Load all artist relations from the cleaned MusicBrainz data into Neo4j.
    """
    with open(cleaned_artists_path) as f:
        artists = json.load(f)
    
    with driver.session(database=NEO4J_DATABASE) as session:
        for artist in artists:
            artist_name = artist['name']
            
            for relation in artist['relations']:
                related_name = relation['artist name']
                rel_type = _normalize_relation_type(relation['type'])
                
                # NEW SYNTAX: relationship type can't be parameterized,
                # so we build it into the query string via f-string,
                # but artist names ARE parameterized normally (safe from injection)
                query = f"""
                MERGE (a:Artist {{name: $artist_name}})
                MERGE (b:Artist {{name: $related_name}})
                MERGE (a)-[:{rel_type}]->(b)
                """
                session.run(query, artist_name=artist_name, related_name=related_name)
                
    logger.info(f'Loaded relations for {len(artists)} artists into Neo4j')


load_relations_to_graph('data/processed/mb_cleaned_artists.json')