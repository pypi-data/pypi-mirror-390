CREATE TABLE settings (
    id_settings SERIAL NOT NULL PRIMARY KEY,
    module    TEXT   NOT NULL,
    key       TEXT   NOT NULL,
    value     TEXT   NOT NULL
);
ALTER TABLE settings ADD UNIQUE (module, key);