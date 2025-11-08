from pokie.http import AutoRouter, PokieView
from pokie.rest import RestView


class IncompleteResourceView(PokieView):
    def get(self, id_record=None):
        pass


class CompleteResourceView(RestView):
    pass


class IncompleteControllerView(PokieView):
    def show(self, id_record):
        pass

    def create(self):
        pass


class CompleteControllerView(IncompleteControllerView):
    def list(self):
        pass

    def update(self, id_record):
        pass

    def delete(self, id_record):
        pass


class TestAutoRouter:
    def test_incomplete_resource(self, pokie_app):
        slug = "test_operation"
        # register incomplete resource class
        AutoRouter.resource(pokie_app, slug, IncompleteResourceView)

        result = {}
        with pokie_app.app_context():
            for rule in pokie_app.url_map.iter_rules():
                methods = rule.methods
                rule_name = str(rule)
                if rule_name.startswith("/" + slug):
                    result[rule_name] = sorted(methods)

        # should only have 2 endpoints - get and list
        assert len(result) == 2
        key = "/" + slug
        assert key in result.keys()
        assert result[key] == sorted({"HEAD", "GET", "OPTIONS"})
        key = "/" + slug + "/<int:id_record>"
        assert key in result.keys()
        assert result[key] == sorted({"HEAD", "GET", "OPTIONS"})

    def test_complete_resource(self, pokie_app):
        slug = "test_operation"
        # register complete
        AutoRouter.resource(pokie_app, slug, CompleteResourceView)

        result = []
        with pokie_app.app_context():
            for rule in pokie_app.url_map.iter_rules():
                methods = rule.methods
                rule_name = str(rule)
                if rule_name.startswith("/" + slug):
                    result.append([rule_name, sorted(methods)])

        expected = [
            ["/test_operation", ["GET", "HEAD", "OPTIONS"]],
            ["/test_operation/<int:id_record>", ["GET", "HEAD", "OPTIONS"]],
            ["/test_operation", ["OPTIONS", "POST"]],
            ["/test_operation/<int:id_record>", ["OPTIONS", "PATCH", "PUT"]],
            ["/test_operation/<int:id_record>", ["DELETE", "OPTIONS"]],
        ]

        # should only have 2 endpoints - get and list
        assert len(result) == len(expected)
        for rule in expected:
            assert rule in result

    def test_incomplete_controller(self, pokie_app):
        slug = "test_operation"
        # register incomplete controller class
        AutoRouter.controller(pokie_app, slug, IncompleteControllerView, "string")

        result = {}
        with pokie_app.app_context():
            for rule in pokie_app.url_map.iter_rules():
                methods = rule.methods
                rule_name = str(rule)
                if rule_name.startswith("/" + slug):
                    result[rule_name] = sorted(methods)

        # should only have 2 endpoints - get and list
        assert len(result) == 2
        key = "/" + slug
        assert key in result.keys()
        assert result[key] == sorted({"OPTIONS", "POST"})
        key = "/" + slug + "/<string:id_record>"
        assert key in result.keys()
        assert result[key] == sorted({"HEAD", "GET", "OPTIONS"})

    def test_complete_controller(self, pokie_app):
        slug = "test_operation"
        # register complete controller
        AutoRouter.controller(pokie_app, slug, CompleteControllerView)

        result = []
        with pokie_app.app_context():
            for rule in pokie_app.url_map.iter_rules():
                methods = rule.methods
                rule_name = str(rule)
                if rule_name.startswith("/" + slug):
                    result.append([rule_name, sorted(methods)])

        expected = [
            ["/test_operation", ["GET", "HEAD", "OPTIONS"]],
            ["/test_operation/<int:id_record>", ["GET", "HEAD", "OPTIONS"]],
            ["/test_operation", ["OPTIONS", "POST"]],
            ["/test_operation/<int:id_record>", ["OPTIONS", "PATCH", "PUT"]],
            ["/test_operation/<int:id_record>", ["DELETE", "OPTIONS"]],
        ]
        # should only have 2 endpoints - get and list
        assert len(result) == len(expected)
        for rule in expected:
            assert rule in result
