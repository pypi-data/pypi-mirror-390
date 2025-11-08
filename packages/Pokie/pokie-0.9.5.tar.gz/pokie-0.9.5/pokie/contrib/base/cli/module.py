import inspect
import json
from argparse import ArgumentParser

from tabulate import tabulate

from pokie.constants import DI_APP
from pokie.core import CliCommand


class ModuleListCmd(CliCommand):
    description = "list loaded modules"

    def arguments(self, parser: ArgumentParser):
        parser.add_argument(
            "--json",
            help="output JSON instead of tabular format",
            action="store_true",
            default=False,
        )

    def run(self, args) -> bool:
        table = []
        for module_name, module in self.get_di().get(DI_APP).modules.items():
            table.append(
                [
                    module_name,
                    inspect.getfile(module.__class__),
                    module.description,
                ]
            )

        if not args.json:
            self.tty.write(
                tabulate(table, headers=["Name", "Module class path", "Description"])
            )
        else:
            result = []
            for row in table:
                result.append(
                    {"name": row[0], "moduleClassPath": row[1], "description": row[2]}
                )
            self.tty.write(json.dumps(result, indent=2))
        return True
