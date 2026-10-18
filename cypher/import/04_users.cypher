UNWIND $rows AS row
MERGE (user:User {id: row.id})
SET user.name = row.name;
