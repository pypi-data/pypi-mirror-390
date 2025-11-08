import pytest

from pokie.constants import DEFAULT_LIST_SIZE
from pokie.http import DbGridRequest
from pokie_test.dto import CustomerRecord


@pytest.fixture
def dbgrid_request():
    return DbGridRequest(CustomerRecord)


@pytest.fixture
def dbgridRequest():
    # camel-case DbGridRequest()
    return DbGridRequest(CustomerRecord, use_camel_case=True)


class TestDbGrid:
    def test_validate(self, dbgrid_request):
        # empty request is valid
        assert dbgrid_request.is_valid({}) is True

        # default parameters with empty request
        data = dbgrid_request.dbgrid_parameters()
        assert data["search_text"] is None
        assert data["match_fields"] is None
        assert data["limit"] is None
        assert data["sort_fields"] is None
        assert data["search_fields"] is None

        # default parameters with limit
        data = dbgrid_request.dbgrid_parameters(DEFAULT_LIST_SIZE)
        assert data["limit"] == DEFAULT_LIST_SIZE

        # default parameters with search field names
        names = ["name1", "name2", "name3"]
        data = dbgrid_request.dbgrid_parameters(DEFAULT_LIST_SIZE, names)
        assert data["limit"] == DEFAULT_LIST_SIZE
        assert data["search_fields"] == names

    def test_validate_limit(self, dbgrid_request):
        # invalid limit
        assert dbgrid_request.is_valid({"limit": "abc"}) is False
        assert len(dbgrid_request.errors) == 1
        assert "limit" in dbgrid_request.errors.keys()

        assert dbgrid_request.is_valid({"limit": "-1"}) is False
        assert len(dbgrid_request.errors) == 1
        assert "limit" in dbgrid_request.errors.keys()

        assert dbgrid_request.is_valid({"limit": ""}) is False
        assert len(dbgrid_request.errors) == 1
        assert "limit" in dbgrid_request.errors.keys()

        # valid limits
        assert dbgrid_request.is_valid({"limit": None}) is True
        assert dbgrid_request.is_valid({"limit": "3"}) is True
        assert dbgrid_request.is_valid({"limit": 3}) is True

    def test_validate_offset(self, dbgrid_request):
        # invalid offset
        assert dbgrid_request.is_valid({"offset": "abc"}) is False
        assert len(dbgrid_request.errors) == 1
        assert "offset" in dbgrid_request.errors.keys()

        assert dbgrid_request.is_valid({"offset": "-1"}) is False
        assert len(dbgrid_request.errors) == 1
        assert "offset" in dbgrid_request.errors.keys()

        assert dbgrid_request.is_valid({"offset": ""}) is False
        assert len(dbgrid_request.errors) == 1
        assert "offset" in dbgrid_request.errors.keys()

        # valid offsets
        assert dbgrid_request.is_valid({"offset": None}) is True
        assert dbgrid_request.is_valid({"offset": "3"}) is True
        assert dbgrid_request.is_valid({"offset": 3}) is True

    def test_match_fields(self, dbgrid_request):
        assert dbgrid_request.is_valid({"match": "|"}) is False
        assert len(dbgrid_request.errors) == 1
        assert "match" in dbgrid_request.errors.keys()

        assert dbgrid_request.is_valid({"match": ""}) is True

        # match error - invalid clauses
        for clause in [
            "abc",
            "abc|",
            "abc:|",
            ":|",
            "|:",
            "|abc:",
            "|:def",
            "id:3|applied|abc",
        ]:
            assert dbgrid_request.is_valid({"match": clause}) is False
            assert len(dbgrid_request.errors) == 1
            assert "match" in dbgrid_request.errors.keys()

        # match error - invalid names
        for clause in ["abc:def", "123:4", "a:1|b:2|c:3"]:
            assert dbgrid_request.is_valid({"match": clause}) is False
            assert len(dbgrid_request.errors) == 1
            assert "match" in dbgrid_request.errors.keys()

        # match success - names
        # Note that no type validation is performed
        for clause in [
            "id:def",
            "id:1|contact_name:true",
            "id:1|contact_name:true|country:john",
        ]:
            assert dbgrid_request.is_valid({"match": clause}) is True

        # match fail - names are camelCased
        for clause in ["id:1|contactName:abc|contactTitle:xyz|postalCode:4400"]:
            assert dbgrid_request.is_valid({"match": clause}) is False
            # @todo: fix this

    def test_validate_match_fields_camelcase(self, dbgridRequest):
        # empty request is valid
        assert dbgridRequest.is_valid({}) is True

        # match success - names
        # Note that no type validation is performed
        for clause in [
            "id:def",
            "id:1|contactName:abc|contactTitle:xyz|postalCode:4400",
        ]:
            assert dbgridRequest.is_valid({"match": clause}) is True

    def test_validate_sort_fields(self, dbgrid_request):
        assert dbgrid_request.is_valid({"sort": "|"}) is False
        assert len(dbgrid_request.errors) == 1
        assert "sort" in dbgrid_request.errors.keys()

        assert dbgrid_request.is_valid({"osrt": ""}) is True

        # sort error - invalid clauses
        for clause in [
            "abc,",
            "abc:,",
            ":,",
            ",:",
            ",abc:",
            ",:def",
            "id:3,applied,abc",
        ]:
            assert dbgrid_request.is_valid({"sort": clause}) is False
            assert len(dbgrid_request.errors) == 1
            assert "sort" in dbgrid_request.errors.keys()

        # sort error - invalid names
        for clause in ["abc", "abc:asc" "123:4", "a:1,b:2,c:3"]:
            assert dbgrid_request.is_valid({"sort": clause}) is False
            assert len(dbgrid_request.errors) == 1
            assert "sort" in dbgrid_request.errors.keys()

        # sort success - names
        for clause in [
            "id",
            "id:asc,contact_name:desc",
            "id:asc,contact_name:desc,postal_code",
        ]:
            assert dbgrid_request.is_valid({"sort": clause}) is True

        # sort fail - camelCase names
        for clause in ["id:asc,contactName:desc", "id:asc,contactName:desc,postalCode"]:
            assert dbgrid_request.is_valid({"sort": clause}) is False
            assert len(dbgrid_request.errors) == 1
            assert "sort" in dbgrid_request.errors.keys()

    def test_validate_sort_fields_camelcase(self, dbgridRequest):
        # empty request is valid
        assert dbgridRequest.is_valid({}) is True

        # sort success
        for clause in ["contactName:asc,contactTitle:desc,postalCode", "contactName"]:
            assert dbgridRequest.is_valid({"sort": clause}) is True
