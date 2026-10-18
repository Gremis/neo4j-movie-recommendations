// Quais filmes pertencem ao gênero informado?
MATCH (m:Movie)-[:IN_GENRE]->(:Genre {name: $genre_name})
RETURN DISTINCT m.id AS id, m.title AS title, m.released AS released
ORDER BY title, id
LIMIT $limit;
