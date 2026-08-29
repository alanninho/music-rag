from src.config import get_neo4j_driver, NEO4J_DATABASE

driver = get_neo4j_driver()

with driver.session(database=NEO4J_DATABASE) as session:
    result = session.run('RETURN "Hello from python" AS message')
    print(result.single()['message'])

driver.close()