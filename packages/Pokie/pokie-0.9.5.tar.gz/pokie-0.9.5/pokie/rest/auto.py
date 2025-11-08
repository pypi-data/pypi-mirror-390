import secrets
import token
from typing import List, Optional

from rick.base import Di
from rick.form import RequestRecord
from rick_db.mapper import ATTR_RECORD_MAGIC, ATTR_TABLE, ATTR_SCHEMA, BaseRecord
from rick_db.backend.pg import PgInfo

import pokie.codegen.pg
from pokie.codegen import RequestGenerator
from pokie.codegen.pg import PgTableSpec
from pokie.constants import DI_DB
from pokie.http import PokieView, AutoRouter

from pokie.rest import RestView


class Auto:
    @staticmethod
    def rest(
        app: object,
        slug: str,
        dto_record: object,
        request_class: RequestRecord = None,
        service: str = None,
        id_type: str = None,
        search_fields: list = None,
        allow_methods: list = None,
        base_cls: tuple = None,
        mixins: tuple = None,
        **kwargs
    ):
        """
        Assemble and register a RESTView for the specified DTO Record

        A View class is generated programmatically, based on RestView (by default). The View class may inherit other
        mixins, e.g. to provide authentication or custom business logic.
        The generated View class is registered with the application, using the slug as endpoint.


        - If service is specified, it is used instead of the automatically generated service;
        - For search to work on listing operations, search_fields must contain the field names;
        - The base View class is RestView, but it can be overridden by the base_cls parameter;
        - If other base class is used, it must extend from PokieView;

        :param app: Flask object
        :param dto_record: Record to use
        :param request_class: optional Request class
        :param service: optional service name
        :param id_type: optional id type for the parameter (to be passed to Flask, e.g. "int"-> id:<int:id_value>)
        :param search_fields: optional list of field names to perform search
        :param allow_methods: optional list of http methods to allow
        :param base_cls: optional base class to use instead of RestView
        :param mixins: optional list of mixins to include
        :param kwargs: optional extra parameters
        :return:
        """

        view = Auto._view_factory(
            app.di,
            dto_record,
            request_class,
            service,
            search_fields,
            allow_methods,
            base_cls,
            mixins,
            **kwargs
        )
        AutoRouter.resource(app, slug, view, id_type=id_type)
        return view

    @staticmethod
    def view(
        app: object,
        table_name: str,
        schema: str = None,
        search_fields: List = None,
        camel_case: bool = False,
        allow_methods: list = None,
        base_cls: tuple = None,
        mixins: tuple = None,
        **kwargs
    ) -> PokieView:
        if not schema:
            schema = PgInfo.SCHEMA_DEFAULT

        db = app.di.get(DI_DB)
        info = PgInfo(db)
        if not info.table_exists(table_name, schema=schema):
            raise ValueError(
                "Auto.view(): table name '{}' not found in schema '{}'".format(
                    table_name, schema
                )
            )

        spec = PgTableSpec(db).generate(table_name, schema)
        if search_fields is None:
            search_fields = [
                f.name for f in spec.fields if f.dtype in ["varchar", "text"]
            ]

        request_class = pokie.codegen.RequestGenerator().generate_class(
            spec, camelcase=camel_case
        )
        record_class = pokie.codegen.RecordGenerator().generate_class(
            spec, camelcase=camel_case
        )

        if not base_cls:
            base_cls = (RestView,)

        if not isinstance(
            base_cls,
            (
                tuple,
                list,
            ),
        ):
            base_cls = (base_cls,)

        if not mixins:
            mixins = ()
        extends = base_cls + mixins
        cls_attrs = {
            "request_class": request_class,
            "record_class": record_class,
            "search_fields": search_fields,
        }
        if allow_methods:
            cls_attrs["allow_methods"] = allow_methods

        cls = type("AutoView_{}".format(secrets.token_hex(8)), extends, cls_attrs)
        return Auto._patch_view_class(cls, mixins)

    @staticmethod
    def _view_factory(
        di: Di,
        dto_record: BaseRecord,
        request_class: RequestRecord,
        service: str = None,
        search_fields: list = None,
        allow_methods: list = None,
        base_cls: tuple = None,
        mixins: tuple = None,
        **kwargs
    ):
        if not base_cls:
            base_cls = (RestView,)
        if not mixins:
            mixins = ()
        if not isinstance(
            base_cls,
            (
                tuple,
                list,
            ),
        ):
            base_cls = (base_cls,)
        extends = base_cls + mixins
        cls_attrs = {
            "record_class": dto_record,
            "search_fields": search_fields,
        }
        if not request_class:
            # no request_class provided, attempt to build one from dto_record
            request_class = Auto._assemble_request_class(di, dto_record)

        if not request_class:
            raise ValueError(
                "Auto._view_factory(): could not assemble a request_class class; a explicit class is required"
            )
        cls_attrs["request_class"] = request_class

        # disable automatic service creation, use custom one instead
        if service:
            cls_attrs["service_name"] = service

        # only override if value specified
        if allow_methods:
            cls_attrs["allow_methods"] = allow_methods

        cls_attrs = {**cls_attrs, **kwargs}
        view_class = type(
            "AutoRestClass_{}".format(secrets.token_hex(8)), extends, cls_attrs
        )
        if not issubclass(view_class, PokieView):
            raise ValueError(
                "Automatic REST classing must use a base class inherited from RestView"
            )
        return Auto._patch_view_class(view_class, mixins)

    @staticmethod
    def _assemble_request_class(
        di: Di, dto_record: BaseRecord
    ) -> Optional[RequestRecord]:
        if getattr(dto_record, ATTR_RECORD_MAGIC) is True:
            table = getattr(dto_record, ATTR_TABLE)
            schema = getattr(dto_record, ATTR_SCHEMA)

            # found a table name, lets assume it is actually a db table
            if table:
                pg_spec = PgTableSpec(di.get(DI_DB))
                spec = pg_spec.generate(table, schema)
                return RequestGenerator().generate_class(spec)
        return None

    @staticmethod
    def _patch_view_class(view_class, mixins):
        """
        Compose mixin dispatch hooks, internal hooks and init_methods to final class
        :param view_class:
        :param mixins:
        :return:
        """
        for item in mixins:
            if getattr(item, "dispatch_hooks", None):
                view_class.dispatch_hooks.extend(item.dispatch_hooks)
            if getattr(item, "internal_hooks", None):
                view_class.internal_hooks.extend(item.internal_hooks)
            if getattr(item, "init_methods", None):
                view_class.init_methods.extend(item.init_methods)
        return view_class
