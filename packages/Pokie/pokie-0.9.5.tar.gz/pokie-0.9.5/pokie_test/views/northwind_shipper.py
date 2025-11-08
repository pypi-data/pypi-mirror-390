from rick.form import RequestRecord, field


class ShipperRequest(RequestRecord):
    fields = {
        "id": field(validators="required|id"),
        "name": field(validators="required|maxlen:40"),
        "phone": field(validators="maxlen:24"),
    }
