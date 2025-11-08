from pokie.core import BaseModule
from pokie.http import AutoRouter, PokieView
from pokie.rest.auto import Auto
from pokie_test.constants import SVC_NORTHWIND_CUSTOMER, SVC_NORTHWIND_STATES
from pokie_test.dto import (
    CategoryRecord,
    ShipperRecord,
    UsStatesRecord,
    TerritoriesRecord,
)
from pokie_test.views import (
    CustomerController,
    CustomRequestRecordView,
    CustomResponseView,
    CamelCaseResponseView,
)
from pokie_test.views.dispatch_hook import HookView
from pokie_test.views.northwind_customer import CustomerView

from pokie_test.views.northwind_shipper import ShipperRequest
from pokie_test.views.northwind_states import StatesRequest
from pokie_test.views.northwind_territories import TerritoriesView


class Module(BaseModule):
    # internal module name
    name = "pokie_test"

    # internal module description
    description = "mock module for pokie unit testing"

    # service map
    #
    # this map registers existing module services, and makes them available to the application. Services are lazy-loaded
    # upon first invocation, to reduce overhead. A service class must inherit the Injectable mixin.
    #
    # The service mapper will load services by service name; As such, service names should be unique, unless the goal
    # is to explicitly override already-registered services
    #
    services = {
        # service entries are defined as {'service_name': 'path_to_class'}
        SVC_NORTHWIND_CUSTOMER: "pokie_test.service.CustomerService",
        SVC_NORTHWIND_STATES: "pokie_test.service.StatesService",
    }

    # cli command map
    #
    # this map registers existing cli commands exposed by the module. Cli commands are classes that inherit from
    # CliCommand. Cli command names should be unique, unless the goal is to explicitly override existing commands
    #
    cmd = {
        # cli commands are defined as {'command': 'path_to_class'}
        # 'cli_cmd': 'path.to.class'
    }

    # events map
    #
    # Pokie has a concept similar to signals in other framework., but with different capabilities, called Events. Events
    # are classes that extend from EventHandler, and implement a method with the name of the event. Event handler objects
    # are short-lived - they are created upon dispatched of a given event, and de-referenced afterwards.
    #
    # Events have a priority number - handler execution follows the priority number in descending order (lower numbers get
    # executed first)
    #
    # Events also have optional in and out objects, typically used for dictionary composition. A common use case is to add
    # extra information to the response generated on a given information, such as login
    #
    # Event names are unique strings that identify the event; there is no specific requirements for naming, but common
    # convention suggests the usage of snakecase (eg. some_event).
    #
    #
    # events are refined as a two-level structure, containing zero or more events, and then handlers and priorities:
    # events = {
    #   'event_name': {
    #       numeric_priority: [path_to_handler, path_to_handler, ...]
    #   }
    # }
    #
    events = {}

    # worker jobs list
    #
    # jobs are tasks that are executed continuously and cooperatively, in a closed loop; their purpose is to execute
    # background operations such as sending emails or resizing images. What makes them different from cron approaches
    # is their continuous execution - there is an idle job with a default 15s pause, and then all other jobs are run
    # sequentially, in a closed loop. If a given job takes too much time to execute, it will delay subsequent jobs, so
    # this approach may not fit all workloads.
    #
    # Jobs are long-lived objects whose class must extend Injectable and Runnable mixins.
    # The job list is a list of strings with the full path for each job class, similar to other existing referencing structures
    #
    jobs = [
        "pokie_test.job.SampleJob",
    ]

    fixtures = [
        "pokie_test.fixtures.ExampleFixture",
    ]

    def build(self, parent=None):
        # This method is called when modules are initialized; At this point, all other dependencies have already been
        # initialized, including the Service Manager, Event Manager and even registered factories
        #
        # All Flask-related routing calls should reside here
        app = parent.app
        AutoRouter.resource(app, "customers", CustomerView, id_type="string")

        app.add_url_rule(
            "/mycustomer/<string:id_customer>",
            methods=["GET"],
            view_func=CustomerController.view_method("view_customer"),
        )

        app.add_url_rule(
            "/views/custom-requestrecord",
            methods=["GET", "POST", "PUT", "PATCH"],
            view_func=CustomRequestRecordView.as_view("view_customrequestrecord"),
        )

        app.add_url_rule(
            "/views/custom-response",
            methods=["GET"],
            view_func=CustomResponseView.as_view("view_customresponse"),
        )

        app.add_url_rule(
            "/views/hooks",
            methods=["GET"],
            view_func=HookView.as_view("view_hooks", di=app.di),
        )

        app.add_url_rule(
            "/views/camelcase",
            methods=["GET"],
            view_func=CamelCaseResponseView.as_view("view_camelcase"),
        )

        # Auto Rest - category
        Auto.rest(
            app, "catalog/category", CategoryRecord, search_fields=[CategoryRecord.name]
        )

        # Auto Rest with custom RequestRecord class
        Auto.rest(
            app,
            "catalog/shipper",
            ShipperRecord,
            ShipperRequest,
            search_fields=[ShipperRecord.name],
        )

        # Auto Rest with custom RequestRecord and custom service
        Auto.rest(
            app,
            "region/states",
            UsStatesRecord,
            StatesRequest,
            SVC_NORTHWIND_STATES,
            search_fields=[
                UsStatesRecord.name,
                UsStatesRecord.abbr,
                UsStatesRecord.region,
            ],
        )

        # Auto Rest with custom base Class
        Auto.rest(
            app,
            "region/territories",
            TerritoriesRecord,
            base_cls=TerritoriesView,
            id_type="string",
            search_fields=[
                TerritoriesRecord.id,
                TerritoriesRecord.territory_description,
            ],
        )

        # Auto View - suppliers
        view = Auto.view(app, "suppliers")
        AutoRouter.resource(app, "catalog/supplier", view)

        # Auto View - products
        view = Auto.view(app, "products")
        AutoRouter.resource(app, "catalog/product", view)

        # Auto View - tablespec
        view = Auto.view(app, "tablespec_serial")
        AutoRouter.resource(app, "tablespec", view)
