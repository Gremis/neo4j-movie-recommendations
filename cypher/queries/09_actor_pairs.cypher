// Quais pares de atores atuaram juntos no maior número de filmes?
MATCH (a:Person)-[:ACTED_IN]->(m:Movie)<-[:ACTED_IN]-(b:Person)
WHERE a.id < b.id
RETURN a.id AS first_id, a.name AS first_name, b.id AS second_id,
       b.name AS second_name, count(DISTINCT m) AS movie_count
ORDER BY movie_count DESC, first_id, second_id
LIMIT $limit;
