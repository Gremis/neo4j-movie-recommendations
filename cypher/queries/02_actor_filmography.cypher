// Em quais filmes esta pessoa atuou?
MATCH (:Person {id: $person_id})-[:ACTED_IN]->(m:Movie)
RETURN DISTINCT m.id AS id, m.title AS title, m.released AS released
ORDER BY released, id
LIMIT $limit;
