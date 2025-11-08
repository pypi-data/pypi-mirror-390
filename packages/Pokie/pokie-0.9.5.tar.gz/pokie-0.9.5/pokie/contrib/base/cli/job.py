from pokie.constants import DI_APP
from pokie.contrib.base.cli.base import BaseCommand


class JobListCmd(BaseCommand):
    description = "list registered job workers"

    def run(self, args) -> bool:
        for name, jobs in self.get_di().get(DI_APP).get_jobs().items():
            self.tty.write("Worker Jobs for module {}:".format(name))
            for job in jobs:
                self.tty.write(
                    self.tty.colorizer.white("   {}".format(job), attr="bold")
                )

        return True


class JobRunCmd(BaseCommand):
    description = "run  all job workers"

    def run(self, args) -> bool:
        app = self.get_di().get(DI_APP)
        # run in loop
        app.job_runner()
        return True
