from abc import ABC, abstractmethod
from typing import Any


class UserInterface(ABC):

    @abstractmethod
    def is_active(self):
        pass

    @abstractmethod
    def is_anonymous(self) -> bool:
        pass

    @abstractmethod
    def is_authenticated(self) -> bool:
        pass

    @abstractmethod
    def get_id(self):
        pass

    @abstractmethod
    def get_record(self):
        pass

    @abstractmethod
    def can_access(self, id_resource) -> bool:
        pass

    @abstractmethod
    def has_role(self, id_role):
        pass

    @abstractmethod
    def get_roles(self):
        pass

    @abstractmethod
    def get_resources(self):
        pass


class User(UserInterface):

    def __init__(
        self,
        id_user: Any = None,
        record: object = None,
        roles: list = None,
        resources: list = None,
        **kwargs
    ):
        self.id = id_user
        self.record = record
        if roles is None:
            roles = []
        self.roles = roles
        if resources is None:
            resources = []
        self.resources = resources
        # set custom parameters
        for k, v in kwargs:
            setattr(self, k, v)

    @property
    def is_active(self):
        if self.record is None:
            return self.id is not None
        active = getattr(self.record, "active", False)
        return active

    @property
    def is_anonymous(self) -> bool:
        return self.id is None

    @property
    def is_authenticated(self) -> bool:
        return self.id is not None

    def can_access(self, id_resource) -> bool:
        return id_resource in self.resources

    def has_role(self, id_role):
        return id_role in self.roles

    def get_id(self):
        if self.id:
            return str(self.id)
        return None

    def get_record(self):
        return self.record

    def get_roles(self):
        return self.roles

    def get_resources(self):
        return self.roles
