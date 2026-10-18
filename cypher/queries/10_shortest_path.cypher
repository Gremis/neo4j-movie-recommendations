// Qual caminho mínimo conecta duas pessoas por atuação ou direção em até 10 saltos?
MATCH (a:Person {id: $source_id}), (b:Person {id: $target_id})
WHERE a <> b
MATCH p = allShortestPaths((a)-[:ACTED_IN|DIRECTED*1..10]-(b))
WITH p, [n IN nodes(p) | n.id] AS path_ids,
     [r IN relationships(p) | type(r)] AS relationship_types
RETURN [n IN nodes(p) | {id: n.id, name: n.name, title: n.title}] AS nodes,
       relationship_types, length(p) AS hops
ORDER BY hops, path_ids, relationship_types
LIMIT $limit;
