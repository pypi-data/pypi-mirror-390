from pokie.contrib.base.dto import FixtureRecord
from pokie.contrib.base.repository.fixture import FixtureRepository
from pokie_test.repository import CustomerRepository


class TestFixtures:
    def test_load_fixtures(self, pokie_db):
        # check if table/record exists
        repo = FixtureRepository(pokie_db)
        f_list = repo.fetch_where(
            [
                (FixtureRecord.name, "=", "pokie_test.fixtures.ExampleFixture"),
            ]
        )
        assert f_list is not None
        assert len(f_list) == 1

        # fixture should have been loaded
        repo = CustomerRepository(pokie_db)
        assert repo.fetch_pk("FIXTURE") is not None
