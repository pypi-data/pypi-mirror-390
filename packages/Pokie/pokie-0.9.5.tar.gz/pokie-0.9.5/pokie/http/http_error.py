# HttpErrorHandler
#
# This class provides Flask with JSON-enabled global error handler responses for common errors, such as 400,404,405 and
# 500.
# The HTTP Error Handler class mechanism is pluggable, and a custom one can be provided instead of the default one.
# To override the default one, just change the HTTP_ERROR_HANDLER config setting to point to a new custom class that
# extends *Injectable*
#
from rick.base import Di
from rick.mixin import Injectable

from pokie.constants import (
    HTTP_BADREQ,
    HTTP_NOT_FOUND,
    HTTP_INTERNAL_ERROR,
    DI_FLASK,
    HTTP_NOT_ALLOWED,
)
from .response import JsonResponse


class HttpErrorHandler(Injectable):
    ERROR_400 = "400 Bad Request: The browser (or proxy) sent a request that this server could not understand."
    ERROR_404 = "404 Not Found: The requested URL was not found on the server."
    ERROR_405 = (
        "405 Method Not Allowed: The method is not allowed for the requested URL."
    )
    ERROR_500 = "500 Internal Server Error"

    def __init__(self, di: Di):
        super().__init__(di)
        _app = di.get(DI_FLASK)

        def wrapper_400(e):
            return self.error_400(_app, e)

        def wrapper_404(e):
            return self.error_404(_app, e)

        def wrapper_405(e):
            return self.error_500(_app, e)

        def wrapper_500(e):
            return self.error_500(_app, e)

        # register global error handler
        _app.register_error_handler(400, wrapper_400)
        _app.register_error_handler(404, wrapper_404)
        _app.register_error_handler(405, wrapper_405)
        _app.register_error_handler(500, wrapper_500)

    def error_400(self, _app, e):
        r = self.response(
            error={"message": self.ERROR_400}, success=False, code=HTTP_BADREQ
        )
        return r.assemble(_app)

    def error_404(self, _app, e):
        r = self.response(
            error={"message": self.ERROR_404}, success=False, code=HTTP_NOT_FOUND
        )
        return r.assemble(_app)

    def error_405(self, _app, e):
        r = self.response(
            error={"message": self.ERROR_405}, success=False, code=HTTP_NOT_ALLOWED
        )
        return r.assemble(_app)

    def error_500(self, _app, e):
        r = self.response(
            error={"message": self.ERROR_500}, success=False, code=HTTP_INTERNAL_ERROR
        )
        return r.assemble(_app)

    def response(self, **kwargs):
        return JsonResponse(**kwargs)
