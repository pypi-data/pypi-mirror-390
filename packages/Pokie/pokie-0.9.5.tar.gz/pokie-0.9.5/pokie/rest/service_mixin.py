from rick_db import DbGrid, Repository


class RestServiceMixin:
    def get(self, id_record):
        return self.repository.fetch_pk(id_record)

    def delete(self, id_record):
        return self.repository.delete_pk(id_record)

    def insert(self, record):
        return self.repository.insert_pk(record)

    def update(self, id_record, record):
        return self.repository.update(record, id_record)

    def exists(self, id_record):
        return self.repository.valid_pk(id_record)

    def list(
        self,
        search_fields: list = None,
        search_text: str = None,
        match_fields: dict = None,
        limit: int = None,
        offset: int = None,
        sort_fields: dict = None,
        search_filter: list = None,
    ):
        grid = DbGrid(self.repository, search_fields, DbGrid.SEARCH_ANY)
        return grid.run(
            None,
            search_text=search_text,
            match_fields=match_fields,
            limit=limit,
            offset=offset,
            sort_fields=sort_fields,
            search_fields=search_filter,
        )

    @property
    def repository(self) -> Repository:
        raise RuntimeError("RestServiceMixin::repository must be overridden")
