from rick.base import Di
from rick.mixin import Injectable
from rick_db import Repository

from pokie.constants import DI_DB
from pokie.rest import RestServiceMixin
from pokie_test.dto import UsStatesRecord


class StatesService(Injectable, RestServiceMixin):
    record_class = UsStatesRecord
    repository_class = None  # optional custom repository class

    def __init__(self, di: Di):
        super().__init__(di)
        self._record_cls = self.record_class
        self._repository_cls = self.repository_class

    @property
    def repository(self) -> Repository:
        if self._record_cls is None:
            raise RuntimeError("Missing record class for repository")
        if self._repository_cls is None:
            return Repository(self.get_di().get(DI_DB), self._record_cls)
        else:
            return self._repository_cls(self.get_di().get(DI_DB))
