UNWIND $rows AS row
MATCH (person:Person {id: row.person_id})
MATCH (movie:Movie {id: row.movie_id})
MERGE (person)-[:DIRECTED]->(movie);
