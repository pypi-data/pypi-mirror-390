from typing import List, Optional

from rick.base import Di
from rick.mixin.injectable import Injectable
from rick.resource import CacheInterface

from pokie.cache import DummyCache
from pokie.contrib.auth.constants import CFG_AUTH_USE_CACHE
from pokie.contrib.auth.dto import AclRoleRecord, AclResourceRecord
from pokie.contrib.auth.repository.acl import AclRoleRepository, AclResourceRepository
from pokie.constants import DI_DB, DI_CACHE, DI_CONFIG, TTL_1D


class AclService(Injectable):
    KEY_ROLE = "acl:role:{}"
    KEY_ROLE_RESOURCE = "acl:role:{}:resources"
    KEY_USER_ROLES = "user:{}:roles"
    TTL = TTL_1D

    def __init__(self, di: Di):
        super().__init__(di)
        self.cache = DummyCache(di)
        if di.get(DI_CONFIG).get(CFG_AUTH_USE_CACHE, False):
            if di.has(DI_CACHE):
                self.cache = di.get(DI_CACHE)

    def get_user_roles(self, id_user: int) -> dict:
        """
        Retrieve roles associated with the user
        :param id_user:
        :return: dict[int, AclRoleRecord]
        """
        key = self.KEY_USER_ROLES.format(id_user)
        id_roles = self.cache.get(key)
        if id_roles is not None:
            result = {}
            for id_role in id_roles:
                result[id_role] = self.get_role(id_role)
            return result

        result = self.role_repository.map_result_id(
            self.role_repository.find_user_roles(id_user)
        )
        user_roles = list(result.keys())

        if len(user_roles) > 0:
            # only cache if it has data
            self.cache.set(key, user_roles, self.TTL)

        return result

    def get_user_resources(self, id_user: int) -> dict:
        """
        Retrieve resources associated with the user
        :param id_user:
        :return: dict[int, AclResourceRecord]
        """
        resources = {}
        key = self.KEY_USER_ROLES.format(id_user)
        id_roles = self.cache.get(key)
        if id_roles is not None:
            for id_role in id_roles:
                for res in self.list_role_resources(id_role):
                    resources[res.id] = res
            return resources

        user_roles = []
        for _, role in self.get_user_roles(id_user).items():
            user_roles.append(role.id)
            for res in self.list_role_resources(role.id):
                resources[res.id] = res

        if len(user_roles) > 0:
            # only cache if it has data
            self.cache.set(key, user_roles, self.TTL)
        return resources

    def list_role_resources(self, id_role: int) -> List[AclResourceRecord]:
        """
        Retrieve all resources for the given role
        :param id_role:
        :return:
        """
        key = self.KEY_ROLE_RESOURCE.format(id_role)
        resource_list = self.cache.get(key)
        if resource_list is not None:
            return resource_list

        resource_list = self.resource_repository.find_by_role(id_role)
        if len(resource_list) > 0:
            # only cache if it has data
            self.cache.set(key, resource_list, self.TTL)
        return resource_list

    def list_roles(self) -> List[AclRoleRecord]:
        """
        Retrieve all roles
        :return:
        """
        return self.role_repository.fetch_all_ordered(AclRoleRecord.id)

    def list_resources(self) -> List[AclResourceRecord]:
        """
        Retrieve all resources
        :return:
        """
        return self.resource_repository.fetch_all_ordered(AclResourceRecord.id)

    def get_role(self, id_role: int) -> Optional[AclRoleRecord]:
        """
        Get Acl Role Record
        :param id_role:
        :return:
        """
        key = self.KEY_ROLE.format(id_role)
        record = self.cache.get(key)
        if record is not None:
            return record

        record = self.role_repository.fetch_pk(id_role)
        if record:
            self.cache.set(key, record, self.TTL)
        return record

    def get_resource(self, id_resource: str) -> Optional[AclResourceRecord]:
        """
        Get Acl Resource Record
        :param id_resource:
        :return:
        """
        return self.resource_repository.fetch_pk(id_resource)

    def add_role(self, description: str) -> int:
        """
        Add a new Role
        :except IntegrityError
        :param description:
        :return:
        """
        record = AclRoleRecord(description=description)
        record.id = self.role_repository.insert_pk(record)
        if record.id:
            key = self.KEY_ROLE.format(record.id)
            self.cache.set(key, record, self.TTL)
        return record.id

    def add_role_resource(self, id_role: int, id_resource: int):
        """
        Add Acl Resource to Role
        :param id_role:
        :param id_resource:
        :return:
        """
        self.role_repository.add_role_resource(id_role, id_resource)
        self.cache.remove(self.KEY_ROLE.format(id_role))
        self.cache.remove(self.KEY_ROLE_RESOURCE.format(id_role))

    def list_role_user_id(self, id_role: int) -> List[int]:
        """
        Retrieve a list of UserRecord id's associated with the role
        :param id_role:
        :return:
        """
        return self.role_repository.list_role_user_id(id_role)

    def add_user_role(self, id_user: int, id_role: int):
        """
        Add Acl Role to user
        :param id_user:
        :param id_role:
        :return:
        """
        self.role_repository.add_user_role(id_user, id_role)
        self.cache.remove(self.KEY_USER_ROLES.format(id_user))

    def remove_user_role(self, id_user: int, id_role: int):
        """
        Remove Acl role from user
        :param id_user:
        :param id_role:
        :return:
        """
        self.role_repository.remove_user_role(id_user, id_role)
        self.cache.remove(self.KEY_USER_ROLES.format(id_user))

    def remove_role(self, id_role: int):
        """
        Removes a role
        May raise DB Exception due to foreign keys
        :param id_role:
        :return:
        """
        self.role_repository.delete_pk(id_role)
        self.cache.remove(self.KEY_ROLE.format(id_role))
        self.cache.remove(self.KEY_ROLE_RESOURCE.format(id_role))

    def can_remove_role(self, id_role: int) -> bool:
        """
        Returns true if Acl Role is not associated with any user
        :param id_role:
        :return:
        """
        return self.role_repository.can_remove(id_role)

    def truncate_role_resources(self, id_role: int):
        """
        Removes Acl Resources from role
        :param id_role:
        :return:
        """
        self.role_repository.truncate_resources(id_role)
        self.cache.remove(self.KEY_ROLE_RESOURCE.format(id_role))

    def truncate_role_users(self, id_role: int):
        """
        Removes all users from role
        :param id_role:
        :return:
        """
        user_list = self.list_role_user_id(id_role)
        self.role_repository.truncate_users(id_role)
        for id_user in user_list:
            self.cache.remove(self.KEY_USER_ROLES.format(id_user))

    def remove_role_resource(self, id_role: int, id_resource: int):
        """
        Removes a Acl Resource from a Acl Role
        :param id_role:
        :param id_resource:
        :return:
        """
        self.role_repository.remove_role_resource(id_role, id_resource)
        self.cache.remove(self.KEY_ROLE_RESOURCE.format(id_role))

    @property
    def role_repository(self):
        return AclRoleRepository(self.get_di().get(DI_DB))

    @property
    def resource_repository(self):
        return AclResourceRepository(self.get_di().get(DI_DB))
