from pokie.constants import HTTP_OK, HTTP_BADREQ, HTTP_NOT_FOUND
from pokie.rest import RestService
from pokie.test import PokieClient
from pokie_test.dto import CustomerRecord
from pokie_test.repository import CustomerRepository


class TestRestView:
    base_url = "/customers"

    def test_view_get(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)

            # list all items
            result = client.get(self.base_url)
            assert result.code == HTTP_OK
            assert result.success is True

            assert result.data["total"] > 50
            assert isinstance(result.data["items"], list)

            # get one item
            url = "{}/{}".format(self.base_url, "FIXTURE")
            result = client.get(url)
            assert result.code == HTTP_OK
            assert result.success is True

            assert isinstance(result.data, dict)
            for name in [
                "company_name",
                "contact_name",
                "contact_title",
                "address",
                "city",
                "region",
                "postal_code",
                "country",
                "phone",
                "fax",
            ]:
                assert name in result.data.keys()

    def test_view_post(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)

            record = CustomerRecord(
                id="TEST_",
                company_name="company_name",
                contact_name="contact_name",
                contact_title="contact_title",
                address="address",
                city="city",
                region="region",
                postal_code="pc",
                country="country",
                phone="phone",
                fax="fax",
            )

            # create new item
            result = client.post(self.base_url, data=record.asdict())
            assert result.code == HTTP_OK
            assert result.success is True

            # get one item
            url = "{}/{}".format(self.base_url, record.id)
            result = client.get(url)
            assert result.code == HTTP_OK
            assert result.success is True

            assert isinstance(result.data, dict)
            for name in [
                "company_name",
                "contact_name",
                "contact_title",
                "address",
                "city",
                "region",
                "postal_code",
                "country",
                "phone",
                "fax",
            ]:
                assert name in result.data.keys()

            # create invalid record
            record = CustomerRecord(
                id="FIXTURE",
                company_name="company_name",
                contact_name="contact_name",
                contact_title="contact_title",
                address="address",
                city="city",
                region="region",
                postal_code="pc",
                country="country",
                phone="phone",
                fax="fax",
            )

            # create new item with duplicate key
            result = client.post(self.base_url, data=record.asdict())
            assert result.code == HTTP_BADREQ
            assert result.success is False

    def test_view_put(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)

            # get one item
            url = "{}/{}".format(self.base_url, "FIXTURE")
            result = client.get(url)
            assert result.code == HTTP_OK
            assert result.success is True

            record = result.data
            record["company_name"] = "UPDATED"
            # update item
            result = client.put(url, data=record)
            assert result.code == HTTP_OK
            assert result.success is True

            # get item again
            result = client.get(url)
            assert result.code == HTTP_OK
            assert result.success is True
            assert result.data["company_name"] == "UPDATED"

            # update record with too long data
            record = result.data
            record["postal_code"] = "ABCDEFGHIJK"
            # update item
            result = client.put(url, data=record)
            assert result.code == HTTP_BADREQ
            assert result.success is False

    def test_view_delete(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)

            url = "{}/{}".format(self.base_url, "FIXTURE")
            result = client.delete(url)
            assert result.code == HTTP_OK
            assert result.success is True

            result = client.get(url)
            assert result.code == HTTP_NOT_FOUND
            assert result.success is False
