import json
import logging
from typing import Any, Optional, Callable
from flask import request
from flask.views import MethodView
from flask.typing import ResponseReturnValue
from flask import current_app
from flask_login import current_user
from rick.form import RequestRecord

from .response import JsonResponse, CamelCaseJsonResponse
from pokie.constants import (
    HTTP_OK,
    HTTP_BADREQ,
    HTTP_INTERNAL_ERROR,
    HTTP_NOAUTH,
    HTTP_FORBIDDEN,
    DI_SERVICES,
    HTTP_NOT_FOUND,
)


class PokieView(MethodView):
    # allowed HTTP methods
    allow_methods = ["get", "post", "put", "patch", "delete", "head"]

    # optional RequestRecord class for request body unmarshall
    # see self.request below
    request_class = None  # type: RequestRecord

    # default response class
    response_class = None  # default will use JsonResponse

    # if true, responses are camelCased
    camel_case = False

    # default error message
    msg_error_default = "request failed"

    # mixin constructors, to be called at the end of __init__
    init_methods = []

    def __init__(self, *args, **kwargs):
        self.di = current_app.di
        self.logger = current_app.logger

        # if no specific response class, use generic one
        # based on camelCase options
        if self.response_class is None:
            self.response_class = (
                CamelCaseJsonResponse if self.camel_case else JsonResponse
            )

        # methods where automatic body deserialization is attempted
        #
        # names must be lowercase
        self.methods_unmarshall_request = ["post", "put", "patch"]

        # automatic request de-serialization
        #
        # if request.method is in self.methods_unmarshall_request, we will attempt to de-serialize the body
        # and validate it using the request_class data type
        self.request = None

        # pre-dispatch hooks
        # these are called before performing the actual dispatch, with the following interface:
        # (method:str, *args: t.Any, **kwargs: t.Any) -> Optional[ResponseReturnValue]
        # if they generate a response other than None, dispatch is aborted and that response is used
        # Note: they are not chained - eg. the first one to return something aborts dispatching
        self.dispatch_hooks = []

        # pre-dispatch internal hooks
        # these hooks are appended to the dispatch hooks to be executed lastly
        self.internal_hooks = [
            "_hook_request",
        ]

        # optional override of internal options
        for name, value in kwargs.items():
            attr = getattr(self, name, None)
            if attr is not None and not callable(attr):
                setattr(self, name, value)

        # perform mixin initialization
        for name in self.init_methods:
            fn = getattr(self, name, None)
            if callable(fn):
                fn(**kwargs)

    def _hook_request(
        self, method: str, *args: Any, **kwargs: Any
    ) -> Optional[ResponseReturnValue]:
        """
        Dispatch hook: de-serialize request
        If body is not json, will use flask form data

        :param method: method name in lowercase
        :param args:
        :param kwargs:
        :return: ResponseReturnValue or None
        """
        if self.request_class is None:
            return None

        if method not in self.methods_unmarshall_request:
            return None

        # unmarshall
        data = None
        if request.is_json:
            if request.content_length is not None:
                data = request.json
        else:
            # form-data
            data = request.form.items()

        if data is None:
            return self.error("empty body")

        # validate request body
        self.request = self.request_class()
        if not isinstance(self.request, RequestRecord):
            raise ValueError(
                "_pre_request(): invalid request class; class must extend RequestRecord"
            )
        if self.request.is_valid(data):
            return None
        return self.request_error(self.request)

    def dispatch_request(self, *args: Any, **kwargs: Any) -> ResponseReturnValue:
        """
        Main request dispatcher

        Extends the Flask implementation by providing pre-dispatch hooks

        :param args:
        :param kwargs:
        :return: ResponseReturnValue
        """
        method = request.method.lower()
        handler = getattr(self, method, None)

        if method not in self.allow_methods:
            return self.exception_handler(None)

        # If the request method is HEAD and we don't have a handler for it
        # retry with GET.
        if handler is None and method == "head":
            handler = getattr(self, "get", None)

        # support for named views
        if "_action_method_" in kwargs.keys():
            handler = getattr(self, kwargs["_action_method_"], None)
            del kwargs["_action_method_"]

        assert handler is not None, "Cannot resolve handler method for dispatch"

        try:
            # run pre-dispatch hooks
            hook_list = self.dispatch_hooks
            hook_list.extend(self.internal_hooks)  # add system hooks
            for name in hook_list:
                hook = getattr(self, name, None)
                assert hook is not None, f"non-existing dispatch hook {name!r}"
                pre = hook(method, *args, **kwargs)
                if pre is not None:
                    return pre

            return current_app.ensure_sync(handler)(*args, **kwargs)
        except Exception as e:
            return self.exception_handler(e)

    @classmethod
    def view_method(
        cls, action_method: str, name=None, *class_args: Any, **class_kwargs: Any
    ) -> Callable:
        """
        Variant of Flask's as_view that supports custom handlers for actions
        :param action_method: method to be called on dispatch 
        :param name: optional route name
        :param class_args: 
        :param class_kwargs: 
        :return: Callable
        """ """
        """
        if name is None:
            name = ".".join([cls.__module__, cls.__name__, action_method]).replace(
                ".", "_"
            )

        def view(*args: Any, **kwargs: Any) -> ResponseReturnValue:
            self = view.view_class(*class_args, **class_kwargs)  # type: ignore
            # add the action method to the dispatch arguments
            kwargs["_action_method_"] = action_method
            return current_app.ensure_sync(self.dispatch_request)(*args, **kwargs)

        if cls.decorators:
            view.__name__ = name
            view.__module__ = cls.__module__
            for decorator in cls.decorators:
                view = decorator(view)

        # We attach the view class to the view function for two reasons:
        # first of all it allows us to easily figure out what class-based
        # view this thing came from, secondly it's also used for instantiating
        # the view class so you can actually replace it with something else
        # for testing purposes and debugging.
        view.view_class = cls  # type: ignore
        view.__name__ = name
        view.__doc__ = cls.__doc__
        view.__module__ = cls.__module__
        view.methods = cls.methods  # type: ignore
        view.provide_automatic_options = cls.provide_automatic_options  # type: ignore
        return view

    def exception_handler(self, e) -> ResponseReturnValue:
        """
        Generic exception handler for dispatch
        :param e:
        :return:
        """
        if e is not None:
            self.logger.exception(e)
        return self.error("bad request")

    def success(self, data=None, code: int = HTTP_OK):
        """
        Returns a success response with optional data payload
        :param data: optional response data
        :param code: int
        :return: Response
        """
        cls = self.response_class(data=data, success=True, code=code)
        return cls.assemble(current_app)

    def success_message(self, message: str):
        """
        Returns a success response with a string message
        :param message: str
        :return: Response
        """
        return self.success({"message": message})

    def error(self, message=None, code=HTTP_BADREQ):
        """
        Returns an error response with an optional string message
        if no message is provided, defaults to PokieView.msg_error_default
        :param message: str
        :param code: int
        :return: Response
        """

        if message is None:
            message = self.msg_error_default

        cls = self.response_class(error={"message": message}, success=False, code=code)
        return cls.assemble(current_app)

    def request_error(self, request_object: RequestRecord, code=HTTP_BADREQ):
        """
        Returns a RequestRecord error response

        :param request_object: RequestRecord
        :param code: int
        :return: Response
        """
        error = {
            "message": self.msg_error_default,
            "formError": request_object.get_errors(),
        }
        cls = self.response_class(error=error, success=False, code=code)
        return cls.assemble(current_app)

    def empty_body(self):
        """
        Error: empty body
        :return: Request
        """
        return self.error("empty body", code=HTTP_BADREQ)

    def not_found(self):
        """
        Error: not found
        :return: Request
        """
        return self.error("record not found", code=HTTP_NOT_FOUND)

    def forbidden(self):
        """
        Error: access denied
        :return: Request
        """
        return self.error("access denied", code=HTTP_FORBIDDEN)

    def denied(self):
        """
        Error: access denied
        :return: Request
        """
        return self.error("access denied", code=HTTP_NOAUTH)

    def get_service(self, service_name):
        """
        Service helper
        :param service_name:
        :return:
        """
        return self.di.get(DI_SERVICES).get(service_name)


class PokieAuthView(PokieView):
    # list of acls to check for current user
    # if list is empty, no acl control is used
    acl = []
    user = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # auth hook
        self.dispatch_hooks.append("_hook_auth")
        self.user = current_user

    def _hook_auth(
        self, method: str, *args: Any, **kwargs: Any
    ) -> Optional[ResponseReturnValue]:
        if not current_user.is_authenticated:
            return self.denied()

        for acl in self.acl:
            if not self.user.can_access(acl):
                return self.forbidden()

        return None
