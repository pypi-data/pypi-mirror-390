from rick.base import Di
from rick.mixin import Injectable, Runnable


class SampleJob(Injectable, Runnable):
    KEY = "SAMPLE_JOB_KEY"

    def __init__(self, di: Di):
        super().__init__(di)
        self.counter = 0

    def run(self, di: Di):
        self.counter += 1
        di.add(self.KEY, self.counter, replace=di.has(self.KEY))
