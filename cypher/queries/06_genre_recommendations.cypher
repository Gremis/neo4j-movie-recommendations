// Quais filmes não avaliados combinam com os gêneros favoritos do usuário?
MATCH (u:User {id: $user_id})-[r:RATED]->(seen:Movie)-[:IN_GENRE]->(g:Genre)
WITH u, g, seen, avg(r.rating) AS rating
WITH u, g, avg(rating) AS preference
WHERE preference >= $min_rating
MATCH (candidate:Movie)-[:IN_GENRE]->(g)
WHERE NOT EXISTS { MATCH (u)-[:RATED]->(candidate) }
WITH DISTINCT candidate, g, preference
WITH candidate, sum(preference) AS score, count(*) AS matched_genres
RETURN candidate.id AS id, candidate.title AS title, score, matched_genres
ORDER BY score DESC, matched_genres DESC, id
LIMIT $limit;
