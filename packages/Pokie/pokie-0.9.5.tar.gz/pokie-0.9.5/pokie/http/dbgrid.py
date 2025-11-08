from typing import Type

from rick_db import Record
from rick.form import RequestRecord, field
from rick.mixin import Translator
import humps

from pokie.constants import DEFAULT_LIST_SIZE


class DbGridRequest(RequestRecord):
    FIELD_OFFSET = "offset"
    FIELD_LIMIT = "limit"
    FIELD_SORT = "sort"
    FIELD_MATCH = "match"
    FIELD_SEARCH = "search"

    fields = {
        FIELD_OFFSET: field(validators="numeric", value=0),
        FIELD_LIMIT: field(validators="numeric", value=DEFAULT_LIST_SIZE),
        FIELD_SORT: field(),
        FIELD_MATCH: field(),
        FIELD_SEARCH: field(),
    }

    def __init__(
        self, record: Type[Record], translator: Translator = None, use_camel_case=False
    ):
        super().__init__(translator)
        self.record = record
        self.use_camel_case = use_camel_case

    def _normalize(self, name) -> str:
        return humps.decamelize(name) if self.use_camel_case else name

    def validator_match(self, data, t: Translator):
        match_fields = data.get(self.FIELD_MATCH, None)
        if match_fields is not None:
            # if string is empty, ignore it
            if len(match_fields.strip()) == 0:
                match_fields = None
            else:
                match_fields = match_fields.split("|")
                # convert field names to column names
                result = {}
                for f in match_fields:
                    f = f.split(":", 1)
                    if len(f) != 2:
                        self.add_error(
                            self.FIELD_MATCH, t.t("invalid field match expression")
                        )
                        return False
                    name = self._normalize(f[0])
                    if name not in self.record._fieldmap.keys():
                        self.add_error(
                            self.FIELD_MATCH, t.t("invalid field name: {}").format(f)
                        )
                        return False
                    result[self.record._fieldmap[name]] = f[1]

                # replace original dict with result
                match_fields = result

        self.fields[self.FIELD_MATCH].value = match_fields

        return True

    def validator_sort(self, data, t: Translator):
        sort = data.get(self.FIELD_SORT, None)

        if sort is not None:
            sort = sort.split(",")
            result = {}
            # convert field, field:desc -> db_field:asc, db_field:desc
            for expr in sort:
                expr = expr.split(":")
                expr[0] = self._normalize(expr[0])
                if expr[0] not in self.record._fieldmap.keys():
                    self.add_error(
                        self.FIELD_SORT,
                        t.t("invalid sort field name: {}").format(expr[0]),
                    )
                    return False

                name = self.record._fieldmap[expr[0]]

                if len(expr) > 1:
                    if expr[1].lower() not in ["asc", "desc"]:
                        self.add_error(
                            self.FIELD_SORT,
                            t.t("invalid sort order: {}").format(expr[1]),
                        )
                        return False

                    result[name] = expr[1]
                else:
                    result[name] = "asc"

        self.fields[self.FIELD_SORT].value = sort
        return True

    def validator_offset(self, data, t: Translator):
        offset = data.get(self.FIELD_OFFSET, None)
        if offset is not None:
            offset = int(offset)
            if offset < 0:
                self.add_error(self.FIELD_OFFSET, t.t("invalid offset value"))
                return False
        self.fields[self.FIELD_OFFSET].value = offset
        return True

    def validator_limit(self, data, t: Translator):
        limit = data.get(self.FIELD_LIMIT, None)
        if limit is not None:
            limit = int(limit)
            if limit < 1:
                self.add_error(self.FIELD_LIMIT, t.t("invalid limit value"))
                return False

        self.fields[self.FIELD_LIMIT].value = limit
        return True

    def dbgrid_parameters(
        self, list_limit: int = 0, search_fields: list = None
    ) -> dict:
        """
        Return a list of parameters to be used as argument for DbGrid.run()
        :param list_limit:
        :param search_fields:
        :return:
        """
        offset = self.fields[self.FIELD_OFFSET].value
        limit = self.fields[self.FIELD_LIMIT].value

        # automatically cap records
        if offset is None and limit is None and list_limit > 0:
            limit = list_limit

        return {
            "search_text": self.fields[self.FIELD_SEARCH].value,
            "match_fields": self.fields[self.FIELD_MATCH].value,
            "limit": limit,
            "offset": offset,
            "sort_fields": self.fields[self.FIELD_SORT].value,
            "search_fields": search_fields,
        }
