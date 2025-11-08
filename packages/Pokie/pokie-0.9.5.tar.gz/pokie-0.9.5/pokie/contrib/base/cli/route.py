from tabulate import tabulate

from pokie.constants import DI_FLASK, DI_APP
from pokie.core import CliCommand


class RouteListCmd(CliCommand):
    description = "list routes"

    def run(self, args) -> bool:
        pokie_app = self.get_di().get(DI_APP)
        pokie_app.init()
        app = self.get_di().get(DI_FLASK)

        with app.app_context():
            result = []
            for rule in app.url_map.iter_rules():
                methods = ",".join(rule.methods)
                result.append([str(rule), methods])

            self.tty.write(tabulate(result, headers=["Endpoint", "Methods"]))
        return True
