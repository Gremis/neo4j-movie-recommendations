UNWIND $rows AS row
MERGE (genre:Genre {name: row.name});
