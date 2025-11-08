from rick_db import fieldmapper


@fieldmapper(tablename="user_token", pk="id_user_token")
class UserTokenRecord:
    id = "id_user_token"
    creation_date = "creation_date"
    update_date = "update_date"
    active = "active"
    user = "fk_user"
    token = "token"
    expires = "expires"
