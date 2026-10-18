UNWIND $rows AS row
MATCH (user:User {id: row.user_id})
MATCH (movie:Movie {id: row.movie_id})
MERGE (user)-[r:RATED]->(movie)
SET r.rating = row.rating;
