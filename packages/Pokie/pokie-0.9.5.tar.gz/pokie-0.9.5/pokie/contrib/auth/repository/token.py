from typing import List, Optional

from rick_db import Repository

from pokie.contrib.auth.dto.token import UserTokenRecord


class UserTokenRepository(Repository):
    def __init__(self, db):
        super().__init__(db, UserTokenRecord)

    def find_by_token(self, token: str) -> Optional[UserTokenRecord]:
        result = self.fetch_where(
            [
                (UserTokenRecord.token, "=", token),
            ]
        )
        if not len(result):
            return None
        return result.pop(0)

    def find_by_user(self, id_user: int) -> List[UserTokenRecord]:
        return self.fetch_where(
            [
                (UserTokenRecord.user, "=", id_user),
            ]
        )

    def prune(self, now) -> List[UserTokenRecord]:
        return self.delete_where(
            [
                (UserTokenRecord.expires, "<", now),
            ]
        )
