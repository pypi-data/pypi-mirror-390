from flask import Flask
from rick.base import Container, Di, MapLoader
from rick.base.container import ContainerBase
from rick.event import EventManager
from rick.resource.console import ConsoleWriter

from pokie.constants import (
    DI_CONFIG,
    DI_APP,
    DI_FLASK,
    DI_SIGNAL,
    DI_TTY,
    DI_SERVICES,
    DI_EVENTS,
    DI_HTTP_ERROR_HANDLER,
)
from pokie.core import FlaskApplication, SignalManager, BaseModule
from pokie.http import HttpErrorHandler
from pokie_test.constants import SVC_NORTHWIND_CUSTOMER


class TestFlaskApplication:
    def test_init(self):
        cfg = Container({})
        app = FlaskApplication(cfg)
        self.assert_app(app)

    def test_build(self):
        cfg = Container({})
        app = FlaskApplication(cfg)
        self.assert_app(app)

        app.build([], [])

        assert app.app is not None
        assert isinstance(app.app, Flask)
        assert app.app.di is not None
        assert isinstance(app.app.di, Di)
        assert isinstance(app.di.get(DI_FLASK), Flask)

        assert isinstance(app.di.get(DI_SIGNAL), SignalManager)
        assert isinstance(app.di.get(DI_TTY), ConsoleWriter)
        assert isinstance(app.di.get(DI_SERVICES), MapLoader)
        assert isinstance(app.di.get(DI_EVENTS), EventManager)
        assert app.di.has(DI_HTTP_ERROR_HANDLER) is False

    def test_current_app(self, pokie_app):
        app = pokie_app.di.get(DI_APP)  # type: FlaskApplication
        self.assert_app(app)

        # modules
        assert app.modules is not None
        assert len(app.modules) == 3
        assert isinstance(app.modules, dict)
        for name, obj in app.modules.items():
            assert name in ["pokie.contrib.base", "pokie.contrib.auth", "pokie_test"]
            assert isinstance(obj, BaseModule)

        # services
        svc = app.di.get(DI_SERVICES)
        assert svc is not None
        assert svc.contains(SVC_NORTHWIND_CUSTOMER)

        # http error handler
        assert app.di.has(DI_HTTP_ERROR_HANDLER)
        assert isinstance(app.di.get(DI_HTTP_ERROR_HANDLER), HttpErrorHandler)

    def assert_app(self, app: FlaskApplication):
        assert app is not None

        assert app.di is not None
        assert isinstance(app.di, Di)
        assert app.di.get(DI_CONFIG) is not None
        assert isinstance(app.di.get(DI_CONFIG), ContainerBase)
        assert app.di.get(DI_APP) is not None

        assert app.modules is not None
        assert isinstance(app.modules, dict)
