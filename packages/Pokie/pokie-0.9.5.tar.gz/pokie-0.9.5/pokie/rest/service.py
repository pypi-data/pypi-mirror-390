from rick.base import Di

from pokie.constants import DI_DB
from rick.mixin import Injectable
from rick_db import Repository
from .service_mixin import RestServiceMixin


class RestService(Injectable, RestServiceMixin):
    record_class = None  # record class
    repository_class = None  # optional custom repository class

    def __init__(self, di: Di):
        super().__init__(di)
        # copy class-attributes to instance-attributes
        # this allows usage of multiple instances of RestService with different record and repository classes
        self._record_cls = self.record_class
        self._repository_cls = self.repository_class

    def set_record_class(self, cls):
        self._record_cls = cls

    def set_repository_class(self, cls):
        self._repository_cls = cls

    @property
    def repository(self) -> Repository:
        if self._record_cls is None:
            raise RuntimeError("Missing record class for repository")
        if self._repository_cls is None:
            return Repository(self.get_di().get(DI_DB), self._record_cls)
        else:
            return self._repository_cls(self.get_di().get(DI_DB))
