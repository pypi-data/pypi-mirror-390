import os
from argparse import ArgumentParser
from pathlib import Path
from pokie.codegen.template import TemplateProcessor
from pokie.core import CliCommand


class TplGenCommand(CliCommand):
    def arguments(self, parser: ArgumentParser):
        parser.add_argument("name", type=str, help="new module name")
        parser.add_argument("path", type=str, help="where to create the module")

    def get_template_path(self, args) -> Path:
        raise RuntimeError("abstract method")

    def get_vars(self, args):
        return {}

    def run(self, args) -> bool:
        base_path = Path(args.path)
        if not base_path.exists() or not base_path.is_dir():
            self.tty.error(
                "error: directory '{}' does not exist".format(str(base_path))
            )
            return False

        dest_path = base_path / Path(args.name)
        if dest_path.exists():
            self.tty.error(
                "error: directory '{}' already exists".format(str(dest_path))
            )
            return False

        tpl_path = self.get_template_path(args)
        vars = self.get_vars(args)

        self.tty.write(self.tty.colorizer.white("generating structure..."))
        processor = TemplateProcessor([tpl_path])
        processor.process(tpl_path, dest_path, vars, self.tty)
        self.tty.write(self.tty.colorizer.green("template processed sucessfully!"))
        return True


class ModuleGenCmd(TplGenCommand):
    description = "create module structure"

    def get_template_path(self, args) -> Path:
        return (
            Path(os.path.dirname(__file__))
            / Path("..")
            / Path("template")
            / Path("module")
        )

    def get_vars(self, args):
        return {"{module_name}": args.name, "{ModuleName}": args.name.capitalize()}


class AppGenCmd(ModuleGenCmd):
    description = "create Pokie application"

    def get_main_path(self) -> Path:
        return (
            Path(os.path.dirname(__file__))
            / Path("..")
            / Path("template")
            / Path("application")
        )

    def arguments(self, parser: ArgumentParser):
        parser.add_argument("name", type=str, help="application name")
        parser.add_argument("path", type=str, help="where to create the application")

    def run(self, args) -> bool:
        base_path = Path(args.path)
        if not base_path.exists() or not base_path.is_dir():
            self.tty.error(
                "error: directory '{}' does not exist".format(str(base_path))
            )
            return False

        dest_path = base_path / Path(args.name)
        if dest_path.exists():
            self.tty.error(
                "error: directory '{}' already exists".format(str(dest_path))
            )
            return False

        tpl_path = self.get_template_path(args)
        vars = self.get_vars(args)

        # generate module
        self.tty.write(self.tty.colorizer.white("generating module structure..."))
        processor = TemplateProcessor([tpl_path])
        processor.process(tpl_path, dest_path, vars, self.tty)

        # generate app
        tpl_path = self.get_main_path()
        self.tty.write(self.tty.colorizer.white("generating main.py..."))
        processor = TemplateProcessor([tpl_path])
        processor.process(tpl_path, base_path, vars, self.tty)

        self.tty.write(self.tty.colorizer.green("operation completed sucessfully!"))
        return True
