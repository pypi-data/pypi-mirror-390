import secrets
from datetime import datetime, timezone
from typing import Optional, List

from rick.base import Di
from rick.crypto.hasher import HasherInterface
from rick.crypto.hasher.bcrypt import BcryptHasher
from rick.mixin import Injectable

from pokie.cache import DummyCache
from pokie.contrib.auth.constants import CFG_AUTH_USE_CACHE
from pokie.contrib.auth.repository import UserTokenRepository
from pokie.contrib.auth.repository.user import UserRepository
from pokie.constants import DI_DB, DI_CACHE, TTL_1D, DI_CONFIG
from rick.util.datetime import iso8601_now
from pokie.contrib.auth.dto import UserRecord, UserTokenRecord


class UserService(Injectable):
    KEY_USERNAME = "user:username:{}"
    KEY_USER = "user:{}"
    KEY_TOKEN = "user:token:{}"
    TTL = TTL_1D

    def __init__(self, di: Di):
        super().__init__(di)
        self.cache = DummyCache(di)
        if di.get(DI_CONFIG).get(CFG_AUTH_USE_CACHE, False):
            if di.has(DI_CACHE):
                self.cache = di.get(DI_CACHE)

    def authenticate(self, username: str, password: str) -> Optional[UserRecord]:
        """
        Attempts to authenticate a user

        :param username:
        :param password:
        :return:
        """
        record = self.get_by_username(username)
        if record is None:
            return None

        if not record.active:
            return None

        if self.hasher.is_valid(password, record.password):
            if self.hasher.need_rehash(record.password):
                # update weak password hash
                self.update_password(record.id, self.hasher.hash(password))

            # update lastlogin
            self.update_lastlogin(record.id)
            return self.load_id(record.id)
        return None

    def sanitize_record(self, record: UserRecord) -> UserRecord:
        """
        Remove sensitive attributes from a UserRecord
        :param record:
        :return:
        """
        record.password = None
        return record

    def load_id(self, id_user: int) -> Optional[UserRecord]:
        """
        Loads a UserRecord with the password cleared out
        :param id_user:
        :return:
        """
        record = self.get_by_id(id_user)
        if record:
            return self.sanitize_record(record)
        return None

    def get_by_id(self, id_user: int) -> Optional[UserRecord]:
        """
        Find user by id
        :param id_user:
        :return:
        """
        key = self.KEY_USER.format(id_user)
        record = self.cache.get(key)
        if record:
            return record

        record = self.user_repository.fetch_pk(id_user)
        if record:
            self.cache.set(key, record, self.TTL)
        return record

    def get_by_username(self, username: str) -> Optional[UserRecord]:
        """
        Find user by username
        :param username:
        :return:
        """
        key = self.KEY_USERNAME.format(username)
        id_user = self.cache.get(key)
        if id_user is not None:
            return self.get_by_id(id_user)

        record = self.user_repository.find_by_username(username)
        if not record:
            return None

        # store username -> id map
        self.cache.set(key, record.id, self.TTL)

        # store user
        key = self.KEY_USER.format(record.id)
        self.cache.set(key, record, self.TTL)
        return record

    def update_lastlogin(self, id_user: int):
        """
        Update user last login timestamp
        :param id_user:
        :return:
        """
        now = datetime.now(timezone.utc)
        self.user_repository.update(UserRecord(id=id_user, last_login=now))
        key = self.KEY_USER.format(id_user)
        record = self.cache.get(key)
        if record:
            record.last_login = now
            self.cache.set(key, record, self.TTL)

    def update_password(self, id_user: int, password_hash: str):
        """
        Update user password
        :param id_user:
        :param password_hash:
        :return:
        """
        self.user_repository.update(UserRecord(id=id_user, password=password_hash))
        self.cache.remove(self.KEY_USER.format(id_user))

    def add_user(self, record: UserRecord) -> int:
        """
        Creates a new user
        :param record:
        :return:
        """
        return self.user_repository.insert_pk(record)

    def list_users(self, offset, limit, sort_field=None, sort_order=None) -> tuple:
        """
        Returns a tuple with a list of users

        :param offset:
        :param limit:
        :param sort_field:
        :param sort_order:
        :return: (total user count, [records])
        """
        return self.user_repository.list_users(offset, limit, sort_field, sort_order)

    def update_user(self, record: UserRecord):
        """
        Update UserRecord
        :param record:
        :return:
        """
        self.user_repository.update(record)
        self.cache.remove(self.KEY_USER.format(record.id))

    def get_user_by_token(self, token: str) -> Optional[UserRecord]:
        """
        Find UserRecord by token
        Expired tokens and inactive tokens are ignored

        :param token:
        :return:
        """
        now = datetime.now(timezone.utc)
        key = self.KEY_TOKEN.format(token)
        record = self.cache.get(key)
        if not record:
            record = self.user_token_repository.find_by_token(token)
            if not record:
                return None
            self.cache.set(key, record, self.TTL)

        if not record.active:
            return None

        if record.expires:
            if record.expires < now:
                return None
        return self.get_by_id(record.user)

    def get_token(self, token: str) -> Optional[UserTokenRecord]:
        """
        Find UserTokenRecord by token
        :param token:
        :return:
        """
        return self.user_token_repository.find_by_token(token)

    def add_user_token(self, id_user: int, expires: datetime = None) -> UserTokenRecord:
        """
        Creates a new Token for the given user
        :param id_user:
        :param expires:
        :return:
        """
        record = UserTokenRecord(
            creation_date=iso8601_now(),
            active=True,
            user=id_user,
            token=secrets.token_hex(64),
            expires=expires,
        )
        record.id = self.user_token_repository.insert_pk(record)
        return record

    def disable_user_token(self, id_user_token: int) -> bool:
        """
        Disable a UserTokenRecord
        :param id_user_token:
        :return:
        """
        record = self.user_token_repository.fetch_pk(id_user_token)
        if not record:
            return False
        key = self.KEY_TOKEN.format(record.token)
        if record.expires:
            if record.expires < datetime.now(timezone.utc).now():
                self.cache.remove(key)

        if not record.active:
            return True

        record.active = False
        self.user_token_repository.update(record)
        self.cache.set(key, record, self.TTL)
        return True

    def remove_user_token(self, id_user_token: int):
        """
        Removes a UserTokenRecord
        :param id_user_token:
        :return:
        """
        record = self.user_token_repository.fetch_pk(id_user_token)
        if not record:
            return None

        key = self.KEY_TOKEN.format(record.token)
        if self.cache.get(key):
            self.cache.remove(key)
        return self.user_token_repository.delete_pk(id_user_token)

    def list_user_tokens(self, id_user: int) -> List[UserTokenRecord]:
        """
        List UserTokenRecord for a given user
        :param id_user:
        :return:
        """
        return self.user_token_repository.find_by_user(id_user)

    def prune_tokens(self):
        """
        Remove all expired tokens
        :return:
        """
        now = datetime.now(timezone.utc)
        self.user_token_repository.prune(now)

    @property
    def user_repository(self) -> UserRepository:
        return UserRepository(self._di.get(DI_DB))

    @property
    def user_token_repository(self) -> UserTokenRepository:
        return UserTokenRepository(self._di.get(DI_DB))

    @property
    def hasher(self) -> HasherInterface:
        return BcryptHasher()
