CREATE CONSTRAINT genre_name_unique IF NOT EXISTS
FOR (genre:Genre) REQUIRE genre.name IS UNIQUE;
