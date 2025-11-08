from typing import Any, Optional

from flask.typing import ResponseReturnValue
from pokie.http import PokieView


class MyInitView(PokieView):
    init_methods = ["foo"]

    def foo(self, **kwargs):
        self.test = [1]
        # add custom hook
        self.internal_hooks.append("myhook")

    def myhook(
        self, method: str, *args: Any, **kwargs: Any
    ) -> Optional[ResponseReturnValue]:
        self.test.append(2)
        return None

    def get(self):
        pass


class TestViewAdvanced:
    def test_view_init(self, pokie_app):
        with pokie_app.app_context():
            view = MyInitView()
            assert getattr(view, "test", None) is not None
            assert getattr(view, "test", None) == [1]

    def test_view_dispatch(self, pokie_app):
        with pokie_app.app_context():
            with pokie_app.test_request_context():
                view = MyInitView()
                view.dispatch_request()
                assert getattr(view, "test", None) == [1, 2]
