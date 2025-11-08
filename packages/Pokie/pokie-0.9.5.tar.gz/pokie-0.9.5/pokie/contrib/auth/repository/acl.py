from typing import List

from rick_db import Repository
from rick_db.sql import Select, Literal, Delete, Insert

from pokie.contrib.auth.dto import (
    AclRoleRecord,
    AclUserRoleRecord,
    AclResourceRecord,
    AclRoleResourceRecord,
    UserRecord,
)
from pokie.contrib.auth.repository.user import UserRepository


class AclRoleRepository(Repository):
    def __init__(self, db):
        super().__init__(db, AclRoleRecord)

    def find_user_roles(self, id_user: int) -> List[AclRoleRecord]:
        key = "find_user_roles"
        sql = self.query_cache.get(key)
        if not sql:
            sql, _ = (
                self.select()
                .join(
                    AclUserRoleRecord,
                    AclUserRoleRecord.id_role,
                    AclRoleRecord,
                    AclRoleRecord.id,
                )
                .where(AclUserRoleRecord.id_user, "=", id_user)
                .order(AclRoleRecord.id)
                .assemble()
            )
            self.query_cache.set(key, sql)

        with self.cursor() as c:
            return c.fetchall(sql, [id_user], cls=AclRoleRecord)

    def can_remove(self, id_role: int) -> bool:
        """
        Check if a given role is empty or not in use
        :param id_role:
        :return:
        """
        # check if role references resources
        sql, values = (
            Select(self.dialect)
            .from_(
                AclRoleResourceRecord,
                cols={Literal("COUNT(*)"): "total"},
                schema=self.schema,
            )
            .where(AclRoleResourceRecord.id_role, "=", id_role)
            .assemble()
        )

        with self.cursor() as c:
            result = c.fetchone(sql, values)
            if result["total"] != 0:
                return False

        # check if role is referenced by users
        sql, values = (
            Select(self.dialect)
            .from_(
                AclUserRoleRecord,
                cols={Literal("COUNT(*)"): "total"},
                schema=self.schema,
            )
            .where(AclUserRoleRecord.id_role, "=", id_role)
            .assemble()
        )

        with self.cursor() as c:
            result = c.fetchone(sql, values)
            if result["total"] != 0:
                return False

        return True

    def truncate_resources(self, id_role: int):
        # delete role resources
        sql, values = (
            Delete(self.dialect)
            .from_(AclRoleResourceRecord)
            .where(AclRoleResourceRecord.id_role, "=", id_role)
            .assemble()
        )
        self.exec(sql, values)

    def truncate_users(self, id_role: int):
        # delete user associations
        sql, values = (
            Delete(self.dialect)
            .from_(AclUserRoleRecord)
            .where(AclUserRoleRecord.id_role, "=", id_role)
            .assemble()
        )
        self.exec(sql, values)

    def add_role_resource(self, id_role: int, id_resource: int):
        """
        Associates a resource with a role
        :param id_role:
        :param id_resource:
        :return:
        """
        # check if resource is already in role
        sql, values = (
            Select(self.dialect)
            .from_(AclRoleResourceRecord, schema=self.schema)
            .where(AclRoleResourceRecord.id_role, "=", id_role)
            .where(AclRoleResourceRecord.id_resource, "=", id_resource)
            .assemble()
        )

        with self.cursor() as c:
            result = c.fetchall(sql, values)
            if len(result) > 0:
                return

        sql, values = (
            Insert(self.dialect)
            .into(AclRoleResourceRecord(id_role=id_role, id_resource=id_resource))
            .assemble()
        )
        self.exec(sql, values)

    def remove_role_resource(self, id_role: int, id_resource: int):
        """
        Removes an association between a resource and a role
        :param id_role:
        :param id_resource:
        :return:
        """
        # check if resource is already in role
        sql, values = (
            Select(self.dialect)
            .from_(AclRoleResourceRecord, schema=self.schema)
            .where(AclRoleResourceRecord.id_role, "=", id_role)
            .where(AclRoleResourceRecord.id_resource, "=", id_resource)
            .assemble()
        )

        with self.cursor() as c:
            result = c.fetchall(sql, values)
            if len(result) == 0:
                return

        # delete resource from role association
        sql, values = (
            Delete(self.dialect)
            .from_(AclRoleResourceRecord)
            .where(AclRoleResourceRecord.id_role, "=", id_role)
            .where(AclRoleResourceRecord.id_resource, "=", id_resource)
            .assemble()
        )
        self.exec(sql, values)

    def list_role_user_id(self, id_role: int) -> List[int]:
        key = "list_role_user_id"
        sql = self.query_cache.get(key)
        if not sql:
            repo = UserRepository(self._db)
            sql, _ = (
                repo.select(UserRecord.id)
                .join(
                    AclUserRoleRecord,
                    AclUserRoleRecord.id_user,
                    UserRecord,
                    UserRecord.id,
                )
                .where(AclUserRoleRecord.id_role, "=", id_role)
                .assemble()
            )
            self.query_cache.set(key, sql)

        with self.cursor() as c:
            return [user.id for user in c.fetchall(sql, [id_role], cls=UserRecord)]

    def remove_user_role(self, id_user: int, id_role: int):
        """
        Removes an association between a user and a role
        :param id_user:
        :param id_role:
        :return:
        """
        # check if role is associated with user
        sql, values = (
            Select(self.dialect)
            .from_(AclUserRoleRecord, schema=self.schema)
            .where(AclUserRoleRecord.id_role, "=", id_role)
            .where(AclUserRoleRecord.id_user, "=", id_user)
            .assemble()
        )

        with self.cursor() as c:
            result = c.fetchall(sql, values)
            if len(result) == 0:
                return

        # delete role from user
        sql, values = (
            Delete(self.dialect)
            .from_(AclUserRoleRecord)
            .where(AclUserRoleRecord.id_role, "=", id_role)
            .where(AclUserRoleRecord.id_user, "=", id_user)
            .assemble()
        )
        self.exec(sql, values)

    def add_user_role(self, id_user, id_role):
        """
        Associates a user with a role
        :param id_user:
        :param id_role:
        :return:
        """
        # check if role is associated with user
        sql, values = (
            Select(self.dialect)
            .from_(AclUserRoleRecord, schema=self.schema)
            .where(AclUserRoleRecord.id_role, "=", id_role)
            .where(AclUserRoleRecord.id_user, "=", id_user)
            .assemble()
        )

        with self.cursor() as c:
            result = c.fetchall(sql, values)
            if len(result) > 0:
                return

        # insert association record
        sql, values = (
            Insert(self.dialect)
            .into(AclUserRoleRecord(id_role=id_role, id_user=id_user))
            .assemble()
        )
        self.exec(sql, values)


class AclResourceRepository(Repository):
    def __init__(self, db):
        super().__init__(db, AclResourceRecord)

    def find_user_resources(self, id_user: int) -> List[AclResourceRecord]:
        key = "find_user_resources"
        sql = self.query_cache.get(key)
        if not sql:
            sql, _ = (
                self.select()
                .join(
                    AclRoleResourceRecord,
                    AclRoleResourceRecord.id_resource,
                    AclResourceRecord,
                    AclResourceRecord.id,
                )
                .join(
                    AclUserRoleRecord,
                    AclUserRoleRecord.id_role,
                    AclRoleResourceRecord,
                    AclRoleResourceRecord.id_role,
                )
                .where(AclUserRoleRecord.id_user, "=", id_user)
                .assemble()
            )
            self.query_cache.set(key, sql)

        with self.cursor() as c:
            return c.fetchall(sql, [id_user], cls=AclResourceRecord)

    def find_by_role(self, id_role: int) -> List[AclResourceRecord]:
        """
        List resources for a given role
        :param id_role:
        :return:
        """
        key = "find_by_role"
        sql = self.query_cache.get(key)
        if not sql:
            sql, _ = (
                self.select()
                .join(
                    AclRoleResourceRecord,
                    AclRoleResourceRecord.id_resource,
                    AclResourceRecord,
                    AclResourceRecord.id,
                )
                .where(AclRoleResourceRecord.id_role, "=", id_role)
                .order(AclResourceRecord.id)
                .assemble()
            )
            self.query_cache.set(key, sql)

        with self.cursor() as c:
            return c.fetchall(sql, [id_role], cls=AclResourceRecord)

    def can_remove(self, id_resource: str):
        """
        Check if a given resource can be removed
        :param id_resource:
        :return:
        """
        # check if role references resources
        sql, values = (
            Select(self.dialect)
            .from_(
                AclRoleResourceRecord,
                cols={Literal("COUNT(*)"): "total"},
                schema=self.schema,
            )
            .where(AclRoleResourceRecord.id_resource, "=", id_resource)
            .assemble()
        )

        with self.cursor() as c:
            result = c.fetchone(sql, values)
            return result["total"] == 0
