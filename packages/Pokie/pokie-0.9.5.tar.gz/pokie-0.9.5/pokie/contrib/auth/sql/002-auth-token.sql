CREATE TABLE user_token(
    id_user_token bigserial not null primary key,
    creation_date timestamp with time zone default NOW(),
    update_date timestamp with time zone default NULL,
    active BOOL default TRUE,
    fk_user int not null references "user",
    token varchar(255) not null unique,
    expires timestamp with time zone default null
);

CREATE INDEX user_token_idx01 on user_token(token);
CREATE INDEX user_token_idx02 on user_token(fk_user);
