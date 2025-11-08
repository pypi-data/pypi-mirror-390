create table jwt_revoked(
    id_jwt_revoked BIGSERIAL NOT NULL PRIMARY KEY,
    token_type CHAR(1) DEFAULT 'A',
    jti VARCHAR(128),
    expires TIMESTAMP,
    sub TEXT
);