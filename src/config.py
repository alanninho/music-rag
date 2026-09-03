''' Shared configuration and utilities for the music RAG project'''

import logging
from pathlib import Path
from dotenv import load_dotenv
import os
import psycopg2

DATA_DIR = Path(__file__).parent.parent / 'data'

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

load_dotenv()

DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')


def get_connection():
    """Create and return a new database connection."""
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def get_logger(name: str) -> logging.Logger:
    """Return a logger for the given module name."""
    return logging.getLogger(name)


from neo4j import GraphDatabase

NEO4J_URI = os.environ.get('NEO4J_URI')
NEO4J_USER = os.environ.get('NEO4J_USER')
NEO4J_PASSWORD = os.environ.get('NEO4J_PASSWORD')
NEO4J_DATABASE = os.environ.get('NEO4J_DATABASE')

def get_neo4j_driver():
    """Create and return a new Neo4j driver instance."""
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


# in config.py
from prometheus_client import Counter

groundedness_failures = Counter('groundedness_check_failures_total', 'Number of answers flagged as ungrounded')