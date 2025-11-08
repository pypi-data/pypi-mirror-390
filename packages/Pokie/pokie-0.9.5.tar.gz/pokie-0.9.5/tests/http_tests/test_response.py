import pytest
from rick.serializer.json import ExtendedJsonEncoder

from pokie.constants import DI_DB
from pokie.http import DbGridRequest, JsonResponse, CamelCaseJsonResponse
from pokie_test.dto import CustomerRecord
from pokie_test.repository import CustomerRepository


@pytest.fixture
def result_dict():
    return {
        "field_a": "123",
        "field_b": "456",
    }


@pytest.fixture
def result_str():
    return "the quick brown fox jumps over the lazy dog"


@pytest.fixture
def result_list():
    return ["item_1", "item_2", "item_3"]


@pytest.fixture
def result_object(pokie_di):
    repo = CustomerRepository(pokie_di.get(DI_DB))
    return repo.fetch_pk("DUMON")


class TestResponse:
    def test_serializer(self):
        obj = JsonResponse()
        serializer = obj.serializer()()
        assert isinstance(serializer, ExtendedJsonEncoder)

    def test_response(self, result_dict):
        # success response
        obj = JsonResponse(result_dict)
        assert "error" not in obj.response.keys()
        assert result_dict == obj.response["data"]

        # error response, no specific error
        obj = JsonResponse(result_dict, success=False)
        assert "error" in obj.response.keys()
        assert isinstance(obj.response["error"], dict)
        assert obj.msg_default_error == obj.response["error"]["message"]

        # error response, override error
        # in this case, error has the payload of the parameter
        obj = JsonResponse(result_dict, success=False, error="some error")
        assert "error" in obj.response.keys()
        assert isinstance(obj.response["error"], str)
        assert "some error" == obj.response["error"]

    def test_dict(self, pokie_app, result_dict):
        obj = JsonResponse(result_dict)

        result = obj.assemble(pokie_app)
        assert (
            result.get_data(True)
            == '{"success":true,"data":{"field_a":"123","field_b":"456"}}'
        )

    def test_str(self, pokie_app, result_str):
        obj = JsonResponse(result_str)

        result = obj.assemble(pokie_app)
        assert (
            result.get_data(True)
            == '{"success":true,"data":"the quick brown fox jumps over the lazy dog"}'
        )

    def test_list(self, pokie_app, result_list):
        obj = JsonResponse(result_list)

        result = obj.assemble(pokie_app)
        assert (
            result.get_data(True)
            == '{"success":true,"data":["item_1","item_2","item_3"]}'
        )

    def test_object(self, pokie_app, result_object):
        obj = JsonResponse(result_object)

        result = obj.assemble(pokie_app)
        assert (
            result.get_data(True)
            == '{"success":true,"data":{"address":"67, rue des Cinquante Otages","city":"Nantes","company_name":"Du monde entier","contact_name":"Janine Labrune","contact_title":"Owner","country":"France","fax":"40.67.89.89","id":"DUMON","phone":"40.67.88.88","postal_code":"44000","region":null}}'
        )

    def test_compact(self, pokie_app, result_list):
        # test debug mode
        obj = JsonResponse(result_list)
        pokie_app.json.compact = True
        result = obj.assemble(pokie_app)
        assert (
            result.get_data(True)
            == '{\n  "success": true, \n  "data": [\n    "item_1", \n    "item_2", \n    "item_3"\n  ]\n}'
        )


class TestCamelCaseResponse:
    def serializer(self):
        obj = CamelCaseJsonResponse()
        serializer = obj.serializer()()
        assert isinstance(serializer, ExtendedJsonEncoder)

    def test_response(self, result_dict):
        # success response
        obj = CamelCaseJsonResponse(result_dict)
        assert "error" not in obj.response.keys()
        assert result_dict == obj.response["data"]

        # error response, no specific error
        obj = CamelCaseJsonResponse(result_dict, success=False)
        assert "error" in obj.response.keys()
        assert isinstance(obj.response["error"], dict)
        assert obj.msg_default_error == obj.response["error"]["message"]

        # error response, override error
        # in this case, error has the payload of the parameter
        obj = CamelCaseJsonResponse(result_dict, success=False, error="some error")
        assert "error" in obj.response.keys()
        assert isinstance(obj.response["error"], str)
        assert "some error" == obj.response["error"]

    def test_dict(self, pokie_app, result_dict):
        obj = CamelCaseJsonResponse(result_dict)

        result = obj.assemble(pokie_app)
        assert (
            result.get_data(True)
            == '{"success":true,"data":{"fieldA":"123","fieldB":"456"}}'
        )

    def test_str(self, pokie_app, result_str):
        obj = CamelCaseJsonResponse(result_str)

        result = obj.assemble(pokie_app)
        assert (
            result.get_data(True)
            == '{"success":true,"data":"the quick brown fox jumps over the lazy dog"}'
        )

    def test_list(self, pokie_app, result_list):
        obj = CamelCaseJsonResponse(result_list)

        result = obj.assemble(pokie_app)
        assert (
            result.get_data(True)
            == '{"success":true,"data":["item_1","item_2","item_3"]}'
        )

    def test_object(self, pokie_app, result_object):
        obj = CamelCaseJsonResponse(result_object)

        result = obj.assemble(pokie_app)
        assert (
            result.get_data(True)
            == '{"success":true,"data":{"address":"67, rue des Cinquante Otages","city":"Nantes","companyName":"Du monde entier","contactName":"Janine Labrune","contactTitle":"Owner","country":"France","fax":"40.67.89.89","id":"DUMON","phone":"40.67.88.88","postalCode":"44000","region":null}}'
        )

    def test_compact(self, pokie_app, result_list):
        # test debug mode
        obj = CamelCaseJsonResponse(result_list)
        pokie_app.json.compact = True
        result = obj.assemble(pokie_app)
        assert (
            result.get_data(True)
            == '{\n  "success": true, \n  "data": [\n    "item_1", \n    "item_2", \n    "item_3"\n  ]\n}'
        )
