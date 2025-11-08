import importlib
import os
import sys
from pokie.core import CliCommand


class PyTestCmd(CliCommand):
    description = "run pytest"
    skipargs = True

    def run(self, args) -> bool:
        if importlib.util.find_spec("pytest") is None:
            self.tty.error(
                "Pytest package not found; to use this command please install pytest"
            )
            return False

        args = []
        if len(sys.argv) > 2:
            args = sys.argv[2:]
        self.tty.write(
            self.tty.colorizer.white("[Pokie]", attr="bold")
            + " Running pytest with: {}".format(str(args))
        )
        import pytest

        sys.exit(pytest.main(args, plugins=["pokie.test"]))
