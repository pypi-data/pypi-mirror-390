class AutoRouter:
    # predefined method names and route rule expansions
    controller_action_map = {
        "list": ["/{slug}", ["GET"], "_list"],
        "show": ["/{slug}/<{type}:id_record>", ["GET"], "_show"],
        "create": ["/{slug}", ["POST"], "_create"],
        "update": ["/{slug}/<{type}:id_record>", ["PUT", "PATCH"], "_update"],
        "delete": ["/{slug}/<{type}:id_record>", ["DELETE"], "_delete"],
    }

    # predefined resource methods and route rule expansions
    resource_action_map = {
        # method_name: [rule, rule, ...]
        "get": [
            ["/{slug}", ["GET"], "_list"],
            ["/{slug}/<{type}:id_record>", ["GET"], "_show"],
        ],
        "post": [["/{slug}", ["POST"], "_create"]],
        "put": [["/{slug}/<{type}:id_record>", ["PUT", "PATCH"], "_update"]],
        "delete": [["/{slug}/<{type}:id_record>", ["DELETE"], "_delete"]],
    }

    @staticmethod
    def controller(app, slug: str, cls, id_type: str = "int"):
        """
        Register default routes for a controller class

        :param app: Flask app or blueprint
        :param slug: route slug
        :param cls: class to map
        :param id_type: optional datatype for id
        :return:
        """
        for method_name, opts in AutoRouter.controller_action_map.items():
            route, methods, suffix = opts
            if callable(getattr(cls, method_name, None)):
                app.add_url_rule(
                    route.format(slug=slug, type=id_type),
                    methods=methods,
                    view_func=cls.view_method(method_name),
                )

    @staticmethod
    def resource(app, slug, cls, id_type: str = None, prefix: str = ""):
        """
        Register default routes for a resource class

        Note: due to the simplistic nature of prefix hashing, if prefixes are used for multiple routes for the
        same class with different prefixes, there is a small chance of collision

        :param app: Flask app or blueprint
        :param slug: route slug
        :param cls: class to map
        :param id_type: optional datatype for id
        :return:
        """
        name = ".".join([cls.__module__, cls.__name__]).replace(".", "_")
        if not id_type:
            id_type = "int"
        for view_name, routes in AutoRouter.resource_action_map.items():
            for item in routes:
                route, methods, suffix = item
                if getattr(cls, view_name, None) is not None:
                    app.add_url_rule(
                        route.format(slug=slug, type=id_type),
                        methods=methods,
                        view_func=cls.as_view("{}{}".format(name, suffix)),
                    )
