// Quais filmes têm as maiores médias, com um mínimo de avaliações?
MATCH (u:User)-[r:RATED]->(m:Movie)
WITH m, u, avg(r.rating) AS rating
WITH m, avg(rating) AS average_rating, count(*) AS rating_count
WHERE rating_count >= $min_ratings
RETURN m.id AS id, m.title AS title, average_rating, rating_count
ORDER BY average_rating DESC, rating_count DESC, id
LIMIT $limit;
