from pokie.contrib.base.constants import SVC_SETTINGS
from pokie.contrib.base.service import SettingsService


class TestSettings:
    def test_settings(self, pokie_service_manager):
        svc = pokie_service_manager.get(SVC_SETTINGS)  # type: SettingsService

        assert len(svc.list()) == 0
        for i in range(1, 10):
            svc.upsert("module1", "setting_{}".format(i), str(i))
        assert len(svc.list()) == 9

        record = svc.by_key("module1", "setting_5")
        assert record is not None
        assert record.value == "5"

        svc.upsert(record.module, record.key, "foo")
        record = svc.by_key("module1", "setting_5")
        assert record is not None
        assert record.value == "foo"
