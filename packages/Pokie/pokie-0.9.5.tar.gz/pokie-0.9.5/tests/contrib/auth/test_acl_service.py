import pytest
from psycopg2.errors import UniqueViolation, ForeignKeyViolation

from pokie.cache.memory import MemoryCache
from pokie.constants import DI_CACHE
from pokie.contrib.auth.constants import SVC_ACL, SVC_USER
from pokie.contrib.auth.dto import AclResourceRecord, UserRecord
from pokie.contrib.auth.service import AclService, UserService


class TestAclService:
    def test_acl_role(self, pokie_service_manager):
        svc_role = pokie_service_manager.get(SVC_ACL)  # type: AclService
        svc_user = pokie_service_manager.get(SVC_USER)  # type: UserService

        id_role = svc_role.add_role("role 1")
        assert id_role is not None
        role1 = svc_role.get_role(id_role)
        assert role1 is not None

        id_role = svc_role.add_role("role 2")
        assert id_role is not None
        role2 = svc_role.get_role(id_role)
        assert role2 is not None

        # test unique constraint
        with pytest.raises(UniqueViolation):
            svc_role.add_role("role 2")

        # add resource to role
        resource = AclResourceRecord(id="resource:foo", description="resource foo")
        svc_role.resource_repository.insert_pk(resource)

        # test unique constraint
        with pytest.raises(UniqueViolation):
            svc_role.resource_repository.insert_pk(resource)

        # add resource to role
        svc_role.add_role_resource(role1.id, resource.id)
        resources = svc_role.list_role_resources(role1.id)
        assert len(resources) == 1
        assert svc_role.can_remove_role(role1.id) is False

        resources = svc_role.list_role_resources(role2.id)
        assert len(resources) == 0
        assert svc_role.can_remove_role(role2.id) is True

        # remove resource from role
        svc_role.remove_role_resource(role1.id, resource.id)
        resources = svc_role.list_role_resources(role1.id)
        assert len(resources) == 0

        user = UserRecord(username="user1", password="")
        user.id = svc_user.add_user(user)
        assert user.id is not None

        # add user to role
        svc_role.add_user_role(user.id, role1.id)
        assert svc_role.can_remove_role(role1.id) is False

        users = svc_role.list_role_user_id(role1.id)
        assert len(users) == 1
        assert user.id in users

        # remove role
        svc_role.remove_role(role2.id)
        assert svc_role.get_role(role2.id) is None
        resources = svc_role.list_role_resources(role2.id)
        assert len(resources) == 0

        with pytest.raises(ForeignKeyViolation):
            svc_role.remove_role(role1.id)

        # remove user from role the hard way
        svc_role.truncate_role_users(role1.id)
        users = svc_role.list_role_user_id(role1.id)
        assert len(users) == 0
        # add it again
        svc_role.add_user_role(user.id, role1.id)

        # remove user from role
        svc_role.remove_user_role(user.id, role1.id)
        # remove role
        svc_role.remove_role(role1.id)
        assert svc_role.get_role(role1.id) is None

    def test_acl_resources(self, pokie_service_manager):
        svc_role = pokie_service_manager.get(SVC_ACL)  # type: AclService
        svc_user = pokie_service_manager.get(SVC_USER)  # type: UserService

        id_role = svc_role.add_role("role 1")
        assert id_role is not None
        role1 = svc_role.get_role(id_role)
        assert role1 is not None

        # create resources
        res1 = AclResourceRecord(id="resource:foo", description="resource foo")
        res2 = AclResourceRecord(id="resource:bar", description="resource bar")
        svc_role.resource_repository.insert_pk(res1)
        svc_role.resource_repository.insert_pk(res2)

        # add res1 to role
        svc_role.add_role_resource(role1.id, res1.id)

        # create user
        user = UserRecord(username="user1", password="")
        user.id = svc_user.add_user(user)
        assert user.id is not None

        # add user to role
        svc_role.add_user_role(user.id, role1.id)
        role_list = svc_role.get_user_roles(user.id)
        assert len(role_list) == 1
        assert user.id in role_list.keys()

        # some extra repository functions not exposed in service
        assert svc_role.resource_repository.can_remove(res1.id) is False
        assert svc_role.resource_repository.can_remove(res2.id) is True

        # list user resources
        resource_list = svc_role.get_user_resources(user.id)
        assert len(resource_list) == 1
        assert res1.id in resource_list.keys()

        # list user roles and resources again for cache hit
        role_list = svc_role.get_user_roles(user.id)
        assert len(role_list) == 1
        resource_list = svc_role.get_user_resources(user.id)
        assert len(resource_list) == 1
        assert res1.id in resource_list.keys()

        # truncate role resources
        svc_role.truncate_role_resources(role1.id)
        resource_list = svc_role.get_user_resources(user.id)
        assert len(resource_list) == 0


class TestCachedAclService(TestAclService):
    def test_cached_acl_role(self, pokie_di, pokie_service_manager):
        pokie_di.add(DI_CACHE, MemoryCache)
        self.test_acl_role(pokie_service_manager)

    def test_cached_acl_resources(self, pokie_di, pokie_service_manager):
        pokie_di.add(DI_CACHE, MemoryCache)
        self.test_acl_resources(pokie_service_manager)
