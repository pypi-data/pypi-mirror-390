from pokie.constants import DI_DB
from rick.base import Di
from rick.mixin import Injectable, Runnable

from pokie_test.dto import CustomerRecord
from pokie_test.repository import CustomerRepository


class ExampleFixture(Injectable, Runnable):
    def run(self, di: Di):
        db = di.get(DI_DB)
        repo = CustomerRepository(db)

        # insert a customer with "FIXTURE" as id
        if repo.fetch_pk("FIXTURE") is None:
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
            repo.insert(record)
