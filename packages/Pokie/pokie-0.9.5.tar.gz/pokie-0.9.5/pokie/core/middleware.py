from threading import Lock


class ModuleRunnerMiddleware:
    def __init__(self, app, pokie_app):
        self.app = app
        self.pokie_app = pokie_app
        self.lock = Lock()

    def __call__(self, environ, start_response):
        self.pokie_app.init()
        return self.app(environ, start_response)
