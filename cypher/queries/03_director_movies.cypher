// Quais filmes esta pessoa dirigiu?
MATCH (:Person {id: $person_id})-[:DIRECTED]->(m:Movie)
RETURN DISTINCT m.id AS id, m.title AS title, m.released AS released
ORDER BY released, id
LIMIT $limit;
