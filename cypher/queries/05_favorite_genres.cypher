// Quais gêneros têm as maiores médias nas avaliações deste usuário?
MATCH (:User {id: $user_id})-[r:RATED]->(m:Movie)-[:IN_GENRE]->(g:Genre)
WITH g, m, avg(r.rating) AS rating
RETURN g.name AS genre, avg(rating) AS average_rating, count(*) AS rating_count
ORDER BY average_rating DESC, rating_count DESC, genre
LIMIT $limit;
