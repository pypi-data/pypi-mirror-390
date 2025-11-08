from rick.base import Di
from rick.mixin import Injectable


class TokenProvider(Injectable):
    def __init__(self, di: Di):
        super().__init__(di)
