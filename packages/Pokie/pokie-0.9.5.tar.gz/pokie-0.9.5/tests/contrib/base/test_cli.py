import subprocess

from pokie.constants import DI_APP


class TestCli:
    """
    Tests CLI utils
    Note: mostly just test if clis actually run
    """

    def run_cmd(self, cmd: list, env: dict, retcode: int = 0):
        cmd = ["python3", "main.py"] + cmd
        if env:
            result = subprocess.run(cmd, capture_output=True, env=env)
        else:
            result = subprocess.run(cmd, capture_output=True)
        assert result.returncode == retcode

    # @todo: these tests are disabled because they currently do not detect the venv where they are run; as such,
    # no package dependencies actually exist, so all commands  fail
    #
    #    def test_list(self):
    #        self.run_cmd(["list"], {}, 0)
    #
    #    def test_help(self):
    #        self.run_cmd(["help", "version"], {}, 0)

    #    def test_version(self):
    #        self.run_cmd(["version"], {}, 0)

    #    def test_module(self, pokie_config):
    #        self.run_cmd(["module:list"], self.get_config(pokie_config))

    #    def test_route(self, pokie_config):
    #        self.run_cmd(["route:list"], self.get_config(pokie_config), 0)

    #    def test_db(self, pokie_config):
    #        self.run_cmd(["db:init"], self.get_config(pokie_config), 0)
    #        self.run_cmd(["db:check"], self.get_config(pokie_config), 0)
    #        self.run_cmd(["db:update"], self.get_config(pokie_config), 0)

    #    def test_job(self, pokie_config, pokie_di):
    #        self.run_cmd(["job:list"], self.get_config(pokie_config), 0)
    #        app = pokie_di.get(DI_APP)
    #        app.job_runner(single_run=True)
    # detect changes performed by SampleJob
    #        assert pokie_di.has("SAMPLE_JOB_KEY")
    #        assert pokie_di.get("SAMPLE_JOB_KEY") > 0

    def get_config(self, cfg) -> dict:
        result = {
            "DB_NAME": cfg.get("test_db_name"),
            "DB_HOST": cfg.get("test_db_host"),
            "DB_PORT": str(cfg.get("test_db_port")),
            "DB_USER": cfg.get("test_db_user"),
            "DB_PASSWORD": cfg.get("test_db_password"),
            "DB_SSL": str(cfg.get("test_db_ssl")),
        }
        return result

    def cleanup(self, s: str):
        for c in ["\n", " "]:
            s = s.replace(c, "")
        return c
