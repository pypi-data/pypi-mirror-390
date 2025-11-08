from pokie.constants import HTTP_OK, HTTP_BADREQ
from pokie.test import PokieClient


class TestView:
    def test_requestrecord(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)

            # GET should not use request deserialization
            result = client.get("/views/custom-requestrecord")
            assert result.code == HTTP_OK
            assert result.success is True

            # PUT must use request deserialization
            # empty values, should fail
            result = client.put("/views/custom-requestrecord", data={})
            assert result.code == HTTP_BADREQ
            assert result.success is False
            assert isinstance(result.error, dict)
            for name in ["field1", "field2"]:
                assert name in result.form_error.keys()

            # invalid values, should fail
            result = client.put("/views/custom-requestrecord", data={"field1": "abcd"})
            assert result.code == HTTP_BADREQ
            assert result.success is False
            assert isinstance(result.error, dict)
            for name in ["field1", "field2"]:
                assert name in result.form_error.keys()

            # valid values, should pass
            result = client.put(
                "/views/custom-requestrecord", data={"field1": "123", "field2": "abc"}
            )
            assert result.code == HTTP_OK
            assert result.success is True

            # POST must use request deserialization
            # empty values, should fail
            result = client.post("/views/custom-requestrecord", data={})
            assert result.code == HTTP_BADREQ
            assert result.success is False
            assert isinstance(result.error, dict)
            for name in ["field1", "field2"]:
                assert name in result.form_error.keys()

            # invalid values, should fail
            result = client.post("/views/custom-requestrecord", data={"field1": "abcd"})
            assert result.code == HTTP_BADREQ
            assert result.success is False
            assert isinstance(result.error, dict)
            for name in ["field1", "field2"]:
                assert name in result.form_error.keys()

            # valid values, should pass
            result = client.post(
                "/views/custom-requestrecord", data={"field1": "123", "field2": "abc"}
            )
            assert result.code == HTTP_OK
            assert result.success is True

            # PATCH must use request deserialization
            # empty values, should fail
            result = client.patch("/views/custom-requestrecord", data={})
            assert result.code == HTTP_BADREQ
            assert result.success is False
            assert isinstance(result.error, dict)
            for name in ["field1", "field2"]:
                assert name in result.form_error.keys()

            # invalid values, should fail
            result = client.patch(
                "/views/custom-requestrecord", data={"field1": "abcd"}
            )
            assert result.code == HTTP_BADREQ
            assert result.success is False
            assert isinstance(result.error, dict)
            for name in ["field1", "field2"]:
                assert name in result.form_error.keys()

            # valid values, should pass
            result = client.patch(
                "/views/custom-requestrecord", data={"field1": "123", "field2": "abc"}
            )
            assert result.code == HTTP_OK
            assert result.success is True

    def test_response(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)

            # because of custom response, we need a custom handler
            result = client.client.get(
                "{}{}".format(client.base_url, "/views/custom-response")
            )
            assert result.status_code == HTTP_OK
            assert result.data == b"hamburger"

    def test_dispatch_hook(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)

            # fetch view
            result = client.get("/views/hooks")
            assert result.code == HTTP_OK
            assert result.success is True
            assert result.data == "the quick brown fox jumps over the lazy dog"

    def test_camel_case(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)

            # fetch view
            result = client.get("/views/camelcase")
            assert result.code == HTTP_OK
            assert result.success is True
            for name in ["companyName", "contactName", "contactTitle"]:
                assert name in result.data.keys()
