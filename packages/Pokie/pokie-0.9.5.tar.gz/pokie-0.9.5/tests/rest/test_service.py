from pokie.constants import HTTP_OK, HTTP_BADREQ
from pokie.rest import RestService
from pokie.test import PokieClient
from pokie_test.dto import CustomerRecord
from pokie_test.repository import CustomerRepository


class TestRestService:
    def test_service(self, pokie_app):
        # build RestService based on pokie_test Customer
        svc = RestService(pokie_app.di)
        svc.set_record_class(CustomerRecord)
        svc.set_repository_class(CustomerRepository)

        assert isinstance(svc.repository, CustomerRepository)
        assert svc._record_cls == CustomerRecord

        # existing record
        assert svc.get("FIXTURE") is not None
        # non-existing record
        assert svc.get("ABCD") is None

        my_key = "ABCD"
        record = CustomerRecord(
            id=my_key,
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
        # create
        assert svc.exists(my_key) is False
        assert svc.insert(record) == my_key
        assert svc.exists(my_key) is True

        # update key from ABCD to DEF
        record.company_name = "XYZ"
        svc.update(my_key, record)
        tmp = svc.get(my_key)
        assert tmp is not None
        assert tmp.company_name == record.company_name

        # delete
        svc.delete(my_key)
        assert svc.exists(my_key) is False

        # list
        total, rows = svc.list()
        assert total is not None
        assert total > 0
        assert len(rows) > 50
