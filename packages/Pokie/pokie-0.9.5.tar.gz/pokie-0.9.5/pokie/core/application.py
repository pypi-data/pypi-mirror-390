import os
import sys
import threading
from argparse import ArgumentParser
from typing import List

from flask import Flask
from rick.base import Di, Container, MapLoader
from rick.event import EventManager
from rick.mixin import Injectable, Runnable
from rick.util.loader import load_class
from rick.resource.console import ConsoleWriter

from pokie.constants import (
    DI_CONFIG,
    DI_SERVICES,
    DI_FLASK,
    DI_APP,
    DI_EVENTS,
    DI_TTY,
    DI_SIGNAL,
    CFG_HTTP_ERROR_HANDLER,
    DI_HTTP_ERROR_HANDLER,
)
import signal
from .signal_manager import SignalManager
from .middleware import ModuleRunnerMiddleware
from .module import BaseModule
from .command import CliCommand
from pokie.util.cli_args import ArgParser


class FlaskApplication:
    CLI_CMD_SUCCESS = 0
    CLI_CMD_FAILED = 1
    CLI_CMD_NOT_FOUND = 2

    module_file_name = "module"  # module class file name
    module_class_name = "Module"  # default module class name

    system_modules = [
        "pokie.contrib.base",
    ]  # system modules to always be included

    def __init__(self, cfg: Container):
        self.di = Di()
        self.app = None
        self.modules = {}  # app module list

        self.di.add(DI_CONFIG, cfg)
        self.di.add(DI_APP, self)
        self.cfg = cfg
        self.lock = threading.Lock()
        self.tty = ConsoleWriter()
        self.initialized = False

        self.pre_http_hooks = (
            []
        )  # list of hooks to run before initializing http operations
        self.pre_cli_hooks = (
            []
        )  # list of hooks to run before initializing cli operations

    def build(self, module_list: list, factories: List = None) -> Flask:
        """
        Build the application

        Factories is a list of optional callables to assemble functionality on top of Di, eg. database connection,
        cache, logging, etc. Factories are called *before* modules are initialized, to ensure all required dependencies
        are available

        :param module_list: list of module names to initialize
        :param factories: optional list of callables to be initialized with the application
        :return:
        """
        if not factories:
            factories = []

        self.app = Flask(type(self).__name__, static_folder=None)

        self.app.di = self.di
        self.di.add(DI_FLASK, self.app)

        # initialize signal manager
        self.di.add(DI_SIGNAL, SignalManager(self.di))

        # initialize TTY
        self.di.add(DI_TTY, self.tty)

        # run factories
        for factory in factories:
            if type(factory) is str:
                # if factory is string, assume it is a path to a callable
                factory = load_class(factory, raise_exception=True)
            if not callable(factory):
                raise RuntimeError("build(): non-callable or non-existing factory")
            else:
                factory(self.di)

        # load modules
        self.modules = {}
        module_list = [*self.system_modules, *module_list]
        for name in module_list:
            cls = load_class(
                "{}.{}.{}".format(name, self.module_file_name, self.module_class_name),
                raise_exception=True,
            )
            if cls is None:
                raise RuntimeError(
                    "build(): cannot load module '{}' - Module() class not found".format(
                        name
                    )
                )
            if not issubclass(cls, BaseModule):
                raise RuntimeError(
                    "build(): Class Module on '{}' must extend BaseModule".format(name)
                )
            if name in self.modules.keys():
                raise ValueError(
                    "build(): Module named '{}' already exists".format(name)
                )
            self.modules[name] = cls(self.di)

        # build service map
        svc_map = {}
        for name, m in self.modules.items():
            services = getattr(m, "services", {})
            if type(services) is dict:
                svc_map.update(services)
            else:
                raise RuntimeError(
                    "build(): cannot load service map from module '{}'; attribute must be of type dict".format(
                        name
                    )
                )
        # register service mapper
        self.di.add(DI_SERVICES, MapLoader(self.di, svc_map))

        # parse events from modules
        evt_mgr = EventManager()
        for _, module in self.modules.items():
            module_events = getattr(module, "events", None)
            if isinstance(module_events, dict):
                for evt_name, evt_details in module_events.items():
                    for priority, handlers in evt_details.items():
                        for handler in handlers:
                            evt_mgr.add_handler(evt_name, handler, int(priority))

        self.di.add(DI_EVENTS, evt_mgr)

        # register exception handler
        if self.cfg.has(CFG_HTTP_ERROR_HANDLER):
            handler = load_class(
                self.cfg.get(CFG_HTTP_ERROR_HANDLER), raise_exception=True
            )
            if not issubclass(handler, Injectable):
                raise RuntimeError(
                    "build(): HTTP_ERROR_HANDLER class does not extend Injectable"
                )
            # initialize & register handler
            handler = handler(self.di)
            self.di.add(DI_HTTP_ERROR_HANDLER, handler)

        self.app.wsgi_app = ModuleRunnerMiddleware(self.app.wsgi_app, self)
        return self.app

    def register_pre_http_hook(self, f):
        """
        Register a hook to be executed during the init() of the webserver

        the hook must have the following interface:

        callable(app:FlaskApplication)

        :param f:
        :return:
        """
        self.pre_http_hooks.append(f)

    def register_pre_cli_hook(self, f):
        """
        Register a hook to be executed before any cli operation

        the hook must have the following interface:

        callable(app:FlaskApplication)

        :param f:
        :return:
        """
        self.pre_cli_hooks.append(f)

    def init(self):
        with self.lock:
            if not self.initialized:
                # initialize modules
                for _, module in self.modules.items():
                    module.build(self)
                self.initialized = True

                # call pre-http hooks
                for fn in self.pre_http_hooks:
                    fn(self)

            def stub(**kwargs):
                pass

            # instead of flag, we empty the method
            setattr(self, "init", stub)

    def http(self, **kwargs):
        self.app.run(**kwargs)

    def cli_runner(self, command: str, args: list = None, **kwargs) -> int:
        # run pre-cli hooks
        for fn in self.pre_cli_hooks:
            fn(self)

        # either console or inline commands
        if args is None:
            args = []

        # parameter parser
        parser = ArgParser(**kwargs)

        if "writer" in kwargs.keys():
            tty = kwargs["writer"]
        else:
            tty = ConsoleWriter()

        # lookup handler
        for _, module in self.modules.items():
            if command in module.cmd.keys():
                # load_class may raise ModuleNotFoundError if path not found
                handler = load_class(module.cmd[command], raise_exception=True)

                if not handler:
                    raise RuntimeError(
                        "cli(): handler class '{}' not found".format(
                            module.cmd[command]
                        )
                    )

                if not issubclass(handler, CliCommand):
                    raise RuntimeError(
                        "cli(): command handler does not extend CliCommand"
                    )

                handler = handler(self.di, writer=tty)  # type: CliCommand
                if not handler.skipargs:  # skipargs controls usage of argparser
                    handler.arguments(parser)
                    args = parser.parse_args(args)
                    if parser.failed:
                        # invalid/insufficient args
                        tty.error(parser.error_message)
                        parser.print_help(tty.stderr)
                        return self.CLI_CMD_FAILED
                else:
                    # skipargs is true, all argparsing is ignored
                    # this allow for custom cli arg handling
                    args = None

                if handler.run(args):
                    return self.CLI_CMD_SUCCESS
                return self.CLI_CMD_FAILED

        # command not found
        tty.error("error executing '{}': command not found".format(command))
        return self.CLI_CMD_NOT_FOUND

    def cli(self, **kwargs):
        """
        Execute CLI commands
        :param kwargs: optional parameters for ArgumentParse
        :return:
        """
        # default command when no args detected
        command = "list"
        # extract command if specified
        if len(sys.argv) > 1:
            command = str(sys.argv[1])

        if "add_help" not in kwargs.keys():
            kwargs["add_help"] = False
        if "usage" not in kwargs.keys():
            kwargs["usage"] = "{} {} [OPTIONS...]".format(
                os.path.basename(sys.argv[0]), command
            )

        # exit code directly maps return codes
        exit(self.cli_runner(command, sys.argv[2:], **kwargs))

    def get_jobs(self) -> dict:
        result = {}
        for module_name, module in self.modules.items():
            jobs = getattr(module, "jobs", [])
            if len(jobs) > 0:
                result[module_name] = jobs
        return result

    def job_runner(self, single_run=False, silent=False):
        # prepare job list
        job_list = []
        for module_name, jobs in self.get_jobs().items():
            for job_name in jobs:
                if not silent:
                    self.tty.write("Preparing job  '{}'...".format(job_name))
                job = load_class(job_name)
                if job is None:
                    if not silent:
                        raise ValueError(
                            "Non-existing job class '{}' in module {}".format(
                                job_name, module_name
                            )
                        )
                    else:
                        return False
                if not issubclass(job, (Injectable, Runnable)):
                    if not silent:
                        raise RuntimeError(
                            "Class '{}' must implement Injectable, Runnable interfaces".format(
                                job_name
                            )
                        )
                    else:
                        return False
                job_list.append(job(self.di))

        # run job list
        job_list.reverse()

        if single_run:
            # single run, runs all jobs once
            for job in job_list:
                job.run(self.di)
        else:
            # continuous run, run jobs in loop
            # abort method
            def abort_jobs(di, signal_no, stack_trace):
                if not silent:
                    di.get(DI_TTY).write("\nCtrl+C pressed, exiting...")
                exit(0)

            if not silent:
                self.tty.write("\nRunning jobs, press CTRL+C to abort...")

            # register clean shutdown
            self.di.get(DI_SIGNAL).add_handler(signal.SIGINT, abort_jobs)

            while True:
                for job in job_list:
                    job.run(self.di)
