// Quais filmes compartilham mais gêneros com o filme informado?
MATCH (source:Movie {id: $movie_id})-[:IN_GENRE]->(g:Genre)<-[:IN_GENRE]-(candidate:Movie)
WHERE candidate <> source
RETURN candidate.id AS id, candidate.title AS title, count(DISTINCT g) AS shared_genres
ORDER BY shared_genres DESC, id
LIMIT $limit;
