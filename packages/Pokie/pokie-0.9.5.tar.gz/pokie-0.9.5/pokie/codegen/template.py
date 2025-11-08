import os
from pathlib import Path
from typing import Optional


class TemplateProcessor:
    def __init__(self, template_paths: list = None):
        if template_paths is None:
            self.template_paths = template_paths
        self.template_paths = template_paths

    def get_template_path(self, name: str) -> Optional[Path]:
        for p in self.template_paths:
            d = Path(p)
            if d.exists() and d.is_dir():
                for item in d.iterdir():
                    if item.is_dir() and d.name == name:
                        return item
        return None

    def process(self, src_path: Path, dest_path: Path, vars: dict, tty=None):
        if not src_path.exists():
            raise ValueError(
                "TemplateProcessor::process() invalid source directory '{}'".format(
                    str(src_path)
                )
            )
        if not src_path.is_dir():
            raise ValueError(
                "TemplateProcessor::process() path '{}' is not a directory".format(
                    str(src_path)
                )
            )
        if dest_path.exists() and not dest_path.is_dir():
            raise ValueError(
                "TemplateProcessor::process() path '{}' is not a directory".format(
                    str(src_path)
                )
            )

        if not dest_path.exists():
            dest_path.mkdir()
        self._process_dir(src_path, dest_path, vars, tty)

    def _process_dir(self, src: Path, dest: Path, vars: dict, tty=None):
        for f in src.iterdir():
            if f.is_file():
                contents = self.read_tpl(f)
                for var, replacement in vars.items():
                    contents = contents.replace(var, replacement)
                fname = f.name.replace(".tpl", "")
                dest_file = dest / Path(fname)
                with open(dest_file, "w") as outfile:
                    outfile.write(contents)
                if tty:
                    tty.write("created '{}' file".format(str(dest_file)))
            elif f.is_dir():
                new_dest = dest / Path(f.name)
                new_dest.mkdir()
                if tty:
                    tty.write("created '{}' directory".format(str(new_dest)))
                self._process_dir(f, new_dest, vars, tty)
            else:
                raise RuntimeError(
                    "something went wrong processing path '{}'".format(f)
                )

    def read_tpl(self, src_file: Path) -> str:
        with open(src_file, "r") as f:
            return f.read()
