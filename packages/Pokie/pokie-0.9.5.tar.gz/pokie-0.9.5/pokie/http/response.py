import json
from typing import Type
from collections.abc import Mapping
import humps
from rick.serializer.json.json import CamelCaseJsonEncoder, ExtendedJsonEncoder
from pokie.constants import HTTP_OK


class ResponseRendererInterface:
    def __init__(
        self,
        data: dict = None,
        success: bool = True,
        error: dict = None,
        code: int = HTTP_OK,
        mime_type: str = None,
        headers: list = None,
    ):
        pass

    def assemble(self, _app, **kwargs):
        pass


class JsonResponse(ResponseRendererInterface):
    """
    Default JSON response formatter

    The usual JSON response has the following format:

    success is True:
    {
        "success": True,
        "data": {...}
    }

    success is False:
    {
        "success": False,
        "error": {
            "message": "...",
            [...optional extra keys, such as formError...]
        }
    }
    """

    # mime type
    mime_type = "application/json"
    # default error message
    msg_default_error = "an error has occurred"

    def __init__(
        self,
        data: dict = None,
        success: bool = True,
        error: dict = None,
        code: int = HTTP_OK,
        mime_type: str = None,
        headers: list = None,
    ):
        """
        Constructor for standardized json response
        :param data:
        :param success:
        :param error:
        :param code:
        :param mime_type:
        :param headers:
        """
        self.headers = headers
        self.code = code
        self.response = {"success": success}

        # override default mime type
        if mime_type is not None:
            self.mime_type = mime_type

        # success always has 'data' object
        if success and data is None:
            data = {}

        # error always has 'error' object
        if not success and error is None:
            error = {"message": self.msg_default_error}
        else:
            if isinstance(error, Mapping):
                if "message" not in error.keys():
                    error["message"] = self.msg_default_error

        if data is not None:
            self.response["data"] = data

        if error is not None:
            self.response["error"] = error

    def assemble(self, _app, **kwargs):
        """
        Assemble Flask response object
        :param _app:
        :return: Response
        """
        indent = None
        separators = (",", ":")

        if _app.json.compact or _app.debug:
            indent = 2
            separators = (", ", ": ")

        data = json.dumps(
            self.response, indent=indent, separators=separators, cls=self.serializer()
        )
        return _app.response_class(
            data, status=self.code, mimetype=self.mime_type, headers=self.headers
        )

    def serializer(self) -> Type[json.JSONEncoder]:
        """
        Get JSON serializer
        :return:
        """
        return ExtendedJsonEncoder


class CamelCaseJsonResponse(JsonResponse):
    def assemble(self, _app, **kwargs):
        """
        Assemble Flask response object
        :param _app:
        :return: Response
        """
        indent = None
        separators = (",", ":")

        if _app.json.compact or _app.debug:
            indent = 2
            separators = (", ", ": ")

        data = json.dumps(
            humps.camelize(self.response),
            indent=indent,
            separators=separators,
            cls=self.serializer(),
        )
        return _app.response_class(
            data, status=self.code, mimetype=self.mime_type, headers=self.headers
        )

    def serializer(self) -> Type[json.JSONEncoder]:
        """
        Get JSON serializer
        :return:
        """
        return CamelCaseJsonEncoder
