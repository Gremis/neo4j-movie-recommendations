// Quais favoritos de usuários com gostos em comum o alvo ainda não avaliou?
MATCH (u:User {id: $user_id})-[mine:RATED]->(common:Movie)<-[theirs:RATED]-(peer:User)
WHERE peer <> u AND mine.rating >= $min_rating AND theirs.rating >= $min_rating
WITH u, peer, count(DISTINCT common) AS shared_positive
MATCH (peer)-[r:RATED]->(candidate:Movie)
WHERE r.rating >= $min_rating
  AND NOT EXISTS { MATCH (u)-[:RATED]->(candidate) }
WITH candidate, peer, shared_positive, avg(r.rating) AS peer_rating
RETURN candidate.id AS id, candidate.title AS title,
       sum(shared_positive) AS score, count(*) AS supporting_users,
       avg(peer_rating) AS average_peer_rating
ORDER BY score DESC, supporting_users DESC, average_peer_rating DESC, id
LIMIT $limit;
