from pokie.http import PokieView, ResponseRendererInterface


class HamburgerResponse(ResponseRendererInterface):
    def assemble(self, _app, **kwargs):
        # our custom Response only returns "hamburger"
        return "hamburger"


class CustomResponseView(PokieView):
    # custom response class to be used, intead of the default one
    response_class = HamburgerResponse

    def get(self):
        # just generate a response
        return self.success()
