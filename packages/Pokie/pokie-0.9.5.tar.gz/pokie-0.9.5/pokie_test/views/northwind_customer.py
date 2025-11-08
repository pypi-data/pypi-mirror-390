from rick.form import RequestRecord, field

from pokie.rest import RestView
from pokie_test.dto import CustomerRecord


# RequestRecord class
class CustomerRequest(RequestRecord):
    fields = {
        "id": field(validators="required|maxlen:16"),
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


class CustomerView(RestView):
    # RequestRecord class for body operations
    request_class = CustomerRequest

    # Database Record class
    record_class = CustomerRecord

    # allowed search fields to be used with the search variable
    search_fields = [
        CustomerRecord.contact_name,
        CustomerRecord.company_name,
    ]

    # optional custom service name to be used; if no service name is specified, an instance of
    # pokie.rest.RestService is automatically created
    # service_name = 'my-service-name'

    # optional limit for default listing operations
    # if list_limit > 0, the specified value will be used as default limit for unbounded listing requests
    # list_limit = -1
