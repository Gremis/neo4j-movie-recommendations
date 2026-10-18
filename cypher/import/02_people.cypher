UNWIND $rows AS row
MERGE (person:Person {id: row.id})
SET person.name = row.name;
