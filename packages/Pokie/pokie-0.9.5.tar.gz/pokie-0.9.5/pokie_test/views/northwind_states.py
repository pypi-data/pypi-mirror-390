from rick.form import RequestRecord, field


class StatesRequest(RequestRecord):
    fields = {
        "id": field(validators="required|id"),
        "name": field(validators="required|maxlen:100"),
        "abbr": field(validators="required|maxlen:2"),
        "region": field(validators="required|maxlen:50"),
    }
