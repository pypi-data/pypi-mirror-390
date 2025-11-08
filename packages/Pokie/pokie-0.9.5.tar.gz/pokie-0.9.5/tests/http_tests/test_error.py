from flask import Response

from pokie.constants import DI_APP
from pokie.http import HttpErrorHandler


class TestErrorHandler:
    def test_errorhandler(self, pokie_app):
        app = pokie_app.di.get(DI_APP)
        obj = HttpErrorHandler(pokie_app.di)

        err = obj.error_400(pokie_app, None)
        assert isinstance(err, Response)
        assert err.status == "400 BAD REQUEST"
        assert err.json["success"] == False

        err = obj.error_404(pokie_app, None)
        assert isinstance(err, Response)
        assert err.status == "404 NOT FOUND"
        assert err.json["success"] == False

        err = obj.error_405(pokie_app, None)
        assert isinstance(err, Response)
        assert err.status == "405 METHOD NOT ALLOWED"
        assert err.json["success"] == False

        err = obj.error_500(pokie_app, None)
        assert isinstance(err, Response)
        assert err.status == "500 INTERNAL SERVER ERROR"
        assert err.json["success"] == False
