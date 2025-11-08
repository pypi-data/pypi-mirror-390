CREATE TABLE _fixture (
    id_fixture SERIAL NOT NULL PRIMARY KEY,
    applied TIMESTAMP default Now(),
    name TEXT NOT NULL UNIQUE
);
