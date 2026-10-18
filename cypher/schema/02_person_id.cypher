CREATE CONSTRAINT person_id_unique IF NOT EXISTS
FOR (person:Person) REQUIRE person.id IS UNIQUE;
