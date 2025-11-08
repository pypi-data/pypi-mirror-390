from typing import Optional, Any
from flask.typing import ResponseReturnValue

from pokie.http import PokieView


class HookView(PokieView):
    MSG = "the quick brown fox jumps over the lazy dog"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # attribute to be filled by the hook
        self.sample = None
        # add hook to the hook list
        self.dispatch_hooks.append("_hook_example")

    def _hook_example(
        self, method: str, *args: Any, **kwargs: Any
    ) -> Optional[ResponseReturnValue]:
        self.sample = HookView.MSG
        # hook was successful, returns None
        return None
        # if hook was unsuccessful, it must return a Response
        # return self.forbidden()

    def get(self):
        # return value injected by hook
        return self.success(self.sample)
