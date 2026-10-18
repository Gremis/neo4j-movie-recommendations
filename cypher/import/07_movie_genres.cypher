UNWIND $rows AS row
MATCH (movie:Movie {id: row.movie_id})
MATCH (genre:Genre {name: row.genre_name})
MERGE (movie)-[:IN_GENRE]->(genre);
