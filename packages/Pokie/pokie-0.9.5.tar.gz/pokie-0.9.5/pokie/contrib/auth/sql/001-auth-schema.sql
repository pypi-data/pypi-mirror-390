CREATE TABLE "user"(
    id_user SERIAL NOT NULL PRIMARY KEY,
    active BOOL DEFAULT True,
    admin BOOL DEFAULT False,
    username VARCHAR(200) NOT NULL UNIQUE,
    first_name VARCHAR(100) DEFAULT '',
    last_name VARCHAR(100) DEFAULT '',
    email VARCHAR(200) DEFAULT '',
    password TEXT NOT NULL,
    creation_date timestamp with time zone default NOW(),
    last_login TIMESTAMP WITH TIME ZONE default NULL,
    external BOOL DEFAULT False,
    attributes JSONB DEFAULT '{}'
);

CREATE TABLE acl_role(
    id_acl_role SERIAL NOT NULL PRIMARY KEY,
    description VARCHAR(200) NOT NULL UNIQUE
);

CREATE TABLE acl_resource(
    id_acl_resource VARCHAR NOT NULL UNIQUE PRIMARY KEY,
    description VARCHAR(200) NOT NULL
);

CREATE TABLE acl_role_resource(
    id_acl_role_resource SERIAL NOT NULL PRIMARY KEY,
    fk_acl_role INT NOT NULL REFERENCES acl_role,
    fk_acl_resource VARCHAR NOT NULL REFERENCES acl_resource
);

CREATE TABLE acl_user_role (
    id_acl_user_role SERIAL NOT NULL PRIMARY KEY,
    fk_acl_role INT NOT NULL REFERENCES acl_role,
    fk_user INT NOT NULL REFERENCES "user"
);

CREATE INDEX acl_user_role_idx01 on acl_user_role(fk_user);


