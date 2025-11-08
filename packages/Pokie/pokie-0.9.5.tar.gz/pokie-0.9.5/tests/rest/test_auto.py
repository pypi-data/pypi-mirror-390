from pokie.constants import HTTP_OK, HTTP_BADREQ, HTTP_NOT_FOUND, DI_DB
from pokie.rest import RestService
from pokie.test import PokieClient
from pokie_test.dto import CustomerRecord
from pokie_test.repository import CustomerRepository


class TestAuto:
    def test_tablespec(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)

            # insert item
            record = {
                "field_bigint": 12,
                "field_bit": "1",
                "field_varbit": "10101",
                "field_bytea": "string",
                "field_char": "b",
            }
            result = client.post("/tablespec", data=record)
            assert result.code == HTTP_OK
            assert result.success is True

            # list all items
            result = client.get("/tablespec")
            assert result.code == HTTP_OK
            assert result.success is True
            assert result.data["total"] == 1
            assert len(result.data["items"]) == 1

    def test_category(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)

            # list all items
            result = client.get("/catalog/category")
            assert result.code == HTTP_OK
            assert result.success is True
            assert result.data["total"] == 8
            assert len(result.data["items"]) == 8
            record = result.data["items"][0]

            # get first item
            result = client.get("/catalog/category/{}".format(record["id"]))
            assert result.code == HTTP_OK
            assert result.success is True

    def test_shipper(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)

            # list all items
            result = client.get("/catalog/shipper")
            assert result.code == HTTP_OK
            assert result.success is True
            assert result.data["total"] == 6
            assert len(result.data["items"]) == 6
            record = result.data["items"][0]

            # get first item
            result = client.get("/catalog/shipper/{}".format(record["id"]))
            assert result.code == HTTP_OK
            assert result.success is True

            # add new item
            record = {"id": 999, "name": "sample", "phone": "0000"}
            result = client.post("/catalog/shipper", data=record)
            assert result.code == HTTP_OK
            assert result.success is True

            # remove item
            result = client.delete("/catalog/shipper/{}".format(999))
            assert result.code == HTTP_OK
            assert result.success is True

    def test_states(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)

            # list all items
            result = client.get("/region/states")
            assert result.code == HTTP_OK
            assert result.success is True
            assert result.data["total"] == 51
            assert len(result.data["items"]) == 51
            record = result.data["items"][0]

            # get first item
            result = client.get("/region/states/{}".format(record["id"]))
            assert result.code == HTTP_OK
            assert result.success is True

            # insert item
            record = {"id": 128, "abbr": "NN", "name": "Narnia", "region": "closet"}
            result = client.post("/region/states", data=record)
            assert result.code == HTTP_OK
            assert result.success is True

            # remove item
            result = client.delete("/region/states/{}".format(128))
            assert result.code == HTTP_OK
            assert result.success is True

    def test_territories(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)

            # list all items
            result = client.get("/region/territories")
            assert result.code == HTTP_OK
            assert result.success is True

            assert result.data["total"] == 53
            assert len(result.data["items"]) == 53
            record = result.data["items"][0]

            # get first item
            result = client.get("/region/territories/{}".format(record["id"]))
            assert result.code == HTTP_OK
            assert result.success is True
            assert result.data["territory_description"] == "hamburger"

            # insert item
            id_record = "09999"
            record = {
                "id": id_record,
                "territory_description": "description",
                "region_id": 1,
            }
            result = client.post("/region/territories", data=record)
            assert result.code == HTTP_OK
            assert result.success is True

            # remove item
            result = client.delete("/region/territories/{}".format(id_record))
            assert result.code == HTTP_OK
            assert result.success is True

    def test_suppliers(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)

            # list all items
            result = client.get("/catalog/supplier")
            assert result.code == HTTP_OK
            assert result.success is True

            assert result.data["total"] == 29
            assert len(result.data["items"]) == 29
            record = result.data["items"][0]

            # get first item
            result = client.get("/catalog/supplier/{}".format(record["id"]))
            assert result.code == HTTP_OK
            assert result.success is True

            # insert item
            id_record = "09999"
            record = {
                "id": 9999,
                "company_name": "supplier 9999",
                "contact_name": "john connor",
                "homepage": "http://google.com",
            }

            result = client.post("/catalog/supplier", data=record)
            assert result.code == HTTP_OK
            assert result.success is True

            # remove item
            result = client.delete("/catalog/supplier/{}".format(id_record))
            assert result.code == HTTP_OK
            assert result.success is True
