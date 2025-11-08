import secrets
from datetime import datetime, timezone, timedelta

import pytest
from psycopg2.errors import UniqueViolation

from pokie.cache.memory import MemoryCache
from pokie.constants import DI_CACHE
from pokie.contrib.auth.constants import SVC_USER
from pokie.contrib.auth.dto import UserRecord
from pokie.contrib.auth.service import UserService


class TestUserService:
    def test_user(self, pokie_service_manager):
        svc_user = pokie_service_manager.get(SVC_USER)  # type: UserService

        # create users
        user1 = UserRecord(username="user1", password="")
        user1.id = svc_user.add_user(user1)
        assert user1.id is not None

        # exception with duplicate username
        with pytest.raises(UniqueViolation):
            _ = svc_user.add_user(user1)

        user2 = UserRecord(username="user2", password="abc")
        user2.id = svc_user.add_user(user2)
        assert user1.id is not None

        # find by username
        record = svc_user.get_by_username(user2.username)
        assert record is not None
        assert record.id == user2.id

        # list users
        user_list = svc_user.list_users(0, 100)
        assert len(user_list) == 2

        pwd = svc_user.hasher.hash("somePassword")
        svc_user.update_password(user1.id, pwd)
        for record in [svc_user.get_by_id(user1.id), svc_user.get_by_username("user1")]:
            assert record is not None
            assert record.id == user1.id
            assert len(record.password) > 0

        # test authentication
        user1 = svc_user.get_by_id(user1.id)
        assert user1.last_login is None
        valid_user = svc_user.authenticate(user1.username, "somePassword")
        assert valid_user is not None
        assert valid_user.id == user1.id
        assert valid_user.password is None
        assert valid_user.last_login is not None

        invalid_user = svc_user.authenticate(user1.username, "someInvalidPassword")
        assert invalid_user is None

        # test load_id and sanitization
        record = svc_user.load_id(user1.id)
        assert record is not None
        assert record.password is None

        # test update user
        data = {"key": "value"}
        user1.first_name = "john"
        user1.last_name = "connor"
        user1.attributes = data
        svc_user.update_user(user1)
        record = svc_user.get_by_id(user1.id)
        assert len(record.attributes) == 1
        assert record.attributes["key"] == "value"
        assert record.first_name == "john"
        assert record.last_name == "connor"

    def test_user_token(self, pokie_service_manager):
        svc_user = pokie_service_manager.get(SVC_USER)  # type: UserService

        # create users
        user1 = UserRecord(username="user1", password="")
        user1.id = svc_user.add_user(user1)
        user2 = UserRecord(username="user2", password="")
        user2.id = svc_user.add_user(user2)

        # create tokens
        tok1 = svc_user.add_user_token(user1.id)
        assert tok1 is not None
        assert len(tok1.token) > 0
        assert tok1.expires is None
        assert tok1.user == user1.id
        assert tok1.active == True
        later = datetime.now(timezone.utc) + timedelta(minutes=10)
        tok2 = svc_user.add_user_token(user2.id, later)
        assert tok2 is not None
        assert len(tok2.token) > 0
        assert tok2.expires is not None
        assert tok2.user == user2.id
        assert tok2.active == True

        # find user by non-existing tokens
        for i in range(0, 10):
            user = svc_user.get_user_by_token(secrets.token_hex())
            assert user is None

        # find user from existing token
        user = svc_user.get_user_by_token(tok1.token)
        assert user is not None
        assert user.id == user1.id
        user = svc_user.get_user_by_token(tok2.token)
        assert user is not None
        assert user.id == user2.id

        # disable token
        assert svc_user.disable_user_token(4927) is False
        assert svc_user.disable_user_token(tok1.id) is True

        # token inactive, should fail
        user = svc_user.get_user_by_token(tok1.token)
        assert user is None
        tok = svc_user.get_token(tok1.token)
        assert tok.active is False

        # list tokens
        token_list = svc_user.list_user_tokens(user2.id)
        assert len(token_list) == 1
        assert token_list[0].user == user2.id

        # remove token
        user = svc_user.get_user_by_token(tok2.token)
        assert user is not None
        svc_user.remove_user_token(tok2.id)
        user = svc_user.get_user_by_token(tok2.token)
        assert user is None

        # add a new token, force expiry
        later = datetime.now(timezone.utc) + timedelta(minutes=10)
        tok1 = svc_user.add_user_token(user2.id, later)
        user = svc_user.get_user_by_token(tok1.token)
        assert user is not None

        # warning: this will cause cache inconsistency
        tok1.expires = datetime.now(timezone.utc) - timedelta(minutes=10)
        svc_user.user_token_repository.update(tok1)
        svc_user.prune_tokens()
        tok = svc_user.user_token_repository.find_by_token(tok1.token)
        assert tok is None


class TestCachedUserService(TestUserService):
    def test_cached_user(self, pokie_di, pokie_service_manager):
        pokie_di.add(DI_CACHE, MemoryCache(pokie_di))
        self.test_user(pokie_service_manager)

    def test_cached_user_token(self, pokie_di, pokie_service_manager):
        pokie_di.add(DI_CACHE, MemoryCache(pokie_di))
        self.test_user_token(pokie_service_manager)
