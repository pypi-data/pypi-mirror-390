from rick.form import RequestRecord, field

from pokie.http import PokieView
from pokie_test.constants import SVC_NORTHWIND_CUSTOMER
from pokie_test.service import CustomerService


# RequestRecord class
class CustomerRequest(RequestRecord):
    fields = {
        "id": field(validators="required|maxlen:5"),
        "company_name": field(validators="required|maxlen:40"),
        "contact_name": field(validators="maxlen:30"),
        "contact_title": field(validators="maxlen:30"),
        "address": field(validators="maxlen:60"),
        "city": field(validators="maxlen:15"),
        "region": field(validators="maxlen:15"),
        "postal_code": field(validators="maxlen:15"),
        "country": field(validators="maxlen:15"),
        "phone": field(validators="maxlen:24"),
        "fax": field(validators="maxlen:24"),
    }


class CustomerController(PokieView):
    def view_customer(self, id_customer: str):
        """
        Controller-style GET endpoint

        :param id_customer:
        :return:
        """
        record = self.svc_customer().get_customer(id_customer)
        if not record:
            return self.not_found()

        return self.success(record)

    def svc_customer(self) -> CustomerService:
        return self.get_service(SVC_NORTHWIND_CUSTOMER)
