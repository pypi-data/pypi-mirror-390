from rick.form import RequestRecord, field
from pokie.http import PokieView


class SampleRequestRecord(RequestRecord):
    fields = {
        "field1": field(validators="required|numeric|maxlen:3"),
        "field2": field(validators="required|maxlen:3"),
    }


class CustomRequestRecordView(PokieView):
    # RequestRecord class for body operations
    # the view will automatically use this class to process the body and - if successful - make the results available
    # at self.request
    request_class = SampleRequestRecord

    def get(self):
        # just used for testing purposes
        return self.success()

    def post(self):
        # if SampleRequestRecord validation is successful, the object is available in self.request;
        # if validation is not successful, this method isn't even executed
        #
        # generate a result based on the self.request RequestRecord object
        result = {
            "field1_contents": self.request.get("field1"),
            "field2_contents": self.request.get("field2"),
        }
        return self.success(result)

    def put(self):
        # if SampleRequestRecord validation is successful, the object is available in self.request;
        # if validation is not successful, this method isn't even executed
        #
        # generate a result based on the self.request RequestRecord object
        result = {
            "field1_contents": self.request.get("field1"),
            "field2_contents": self.request.get("field2"),
        }
        return self.success(result)

    def patch(self):
        # if SampleRequestRecord validation is successful, the object is available in self.request;
        # if validation is not successful, this method isn't even executed
        #
        # generate a result based on the self.request RequestRecord object
        result = {
            "field1_contents": self.request.get("field1"),
            "field2_contents": self.request.get("field2"),
        }
        return self.success(result)
