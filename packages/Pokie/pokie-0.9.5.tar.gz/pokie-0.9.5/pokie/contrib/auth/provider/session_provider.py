from typing import Optional

from flask import Request
from rick.mixin import Injectable
import uuid

from flask_login import LoginManager, logout_user, login_user
from rick.base import Di

from pokie.constants import DI_CONFIG, DI_SERVICES, CFG_AUTH_SECRET, DI_FLASK
from pokie.contrib.auth import User
from pokie.contrib.auth.constants import SVC_USER, SVC_ACL
from pokie.contrib.auth.dto import UserRecord
from pokie.contrib.auth.service import AclService
from pokie.contrib.auth.user import UserInterface


def build_user_acl(di, user_record: UserRecord):
    svc_acl = di.get(DI_SERVICES).get(SVC_ACL)  # type: AclService
    roles = list(svc_acl.get_user_roles(user_record.id).keys())
    resources = list(svc_acl.get_user_resources(user_record.id).keys())
    return User(
        id_user=user_record.id, record=user_record, roles=roles, resources=resources
    )


class SessionProvider(Injectable):
    def __init__(self, di: Di):
        super().__init__(di)

        cfg = di.get(DI_CONFIG)
        app = di.get(DI_FLASK)
        app.secret_key = cfg.get(CFG_AUTH_SECRET, uuid.uuid4().hex)
        login_manager = LoginManager()
        login_manager.init_app(app)

        @login_manager.user_loader
        def load_user(user_id):
            # restores user profile from user service
            user_id = int(user_id)
            svc_manager = di.get(DI_SERVICES)
            user_record = svc_manager.get(SVC_USER).load_id(user_id)
            if not user_record:
                return None  # this will clear session
            return build_user_acl(di, user_record)

    def login(self, username, password, **kwargs) -> Optional[UserInterface]:
        svc_user = self.get_di().get(DI_SERVICES).get(SVC_USER)
        user_record = svc_user.authenticate(username, password)
        if not user_record:
            return None

        remember = False
        if "remember" in kwargs.keys():
            remember = bool(kwargs["remember"])
        user = build_user_acl(self.get_di(), user_record)

        # create user session
        login_user(user, remember)
        return user

    def get_user(self, req: Request, **kwargs) -> User:
        raise RuntimeError("SessionProvider: get_user() is not available directly")

    def logout(self, **kwargs):
        # remove user session
        logout_user()
