from pokie.http import PokieView
from pokie_test.dto import CustomerRecord


class CamelCaseResponseView(PokieView):
    camel_case = True

    def get(self):
        record = CustomerRecord(
            company_name="company_name",
            contact_name="contact_name",
            contact_title="contact_title",
            address="address",
        )
        return self.success(record)
