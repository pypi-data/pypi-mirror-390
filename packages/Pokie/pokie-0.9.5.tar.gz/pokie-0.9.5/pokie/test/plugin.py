import sys
import pytest
import os

from rick_db.backend.pg import PgConnection, PgManager

from .client import PokieClient
from pokie.constants import (
    POKIE_NAMESPACE,
    POKIE_APP,
    POKIE_FACTORY,
    DI_CONFIG,
    DI_DB,
    DI_SERVICES,
    CFG_TEST_DB_REUSE,
    CFG_TEST_SKIP_MIGRATIONS,
    CFG_TEST_SKIP_FIXTURES,
    CFG_TEST_DB_NAME,
    CFG_TEST_MANAGE_DB,
    CFG_TEST_SHARE_CTX,
    CFG_TEST_DB_HOST,
    CFG_TEST_DB_PORT,
    CFG_TEST_DB_USER,
    CFG_TEST_DB_PASSWORD,
    CFG_TEST_DB_SSL,
    DI_APP,
)


@pytest.hookimpl()
def pytest_addoption(parser) -> None:
    group = parser.getgroup("pokie")
    group.addoption(
        "--reuse-db",
        action="store_true",
        dest="reuse_db",
        default=False,
        help="Do not re-create test database between tests, and re-use database if already exists.",
    )
    group.addoption(
        "--no_migrations",
        action="store_true",
        dest="skip_migrations",
        default=False,
        help="Do not run database migrations",
    )
    group.addoption(
        "--no_fixtures",
        action="store_true",
        dest="skip_fixtures",
        default=False,
        help="Do not run fixtures",
    )


@pytest.fixture(scope="session")
def pokie_factory():
    """
    Base pokie initialization

    attempts to extract the Flask 'app' object and the optional factory 'build_pokie()' from the main scope of the
    application
    """
    # attempt to extract Flask application from the main namespace
    pokie_ns = os.getenv(POKIE_NAMESPACE, "__main__")
    pokie_app = os.getenv(POKIE_APP, "app")
    pokie_factory = os.getenv(POKIE_FACTORY, "build_pokie")

    # validate namespace
    if pokie_ns not in sys.modules.keys():
        raise RuntimeError("Error: cannot find pokie namespace '{}'".format(pokie_ns))

    app = getattr(sys.modules[pokie_ns], pokie_app)
    # validate object
    if app is None:
        raise RuntimeError(
            "Error: cannot find flask object '{}' in namespace '{}'".format(
                pokie_app, pokie_ns
            )
        )

    # validate factory if exists
    factory = getattr(sys.modules[pokie_ns], pokie_factory)
    if factory is not None:
        if not callable(factory):
            raise RuntimeError("Error: attribute named 'build_pokie' is not callable")

    return app, factory


@pytest.fixture()
def pokie_config(pokie_app):
    """
    Application config fixture
    """
    yield pokie_app.di.get(DI_CONFIG)


@pytest.fixture()
def pokie_di(pokie_app):
    """
    Application Di fixture
    """
    yield pokie_app.di


@pytest.fixture()
def pokie_db(pokie_app):
    """
    Database Connection fixture
    """
    yield pokie_app.di.get(DI_DB)


@pytest.fixture()
def pokie_service_manager(pokie_app):
    """
    Service Manager fixture
    """
    yield pokie_app.di.get(DI_SERVICES)


@pytest.fixture()
def pokie_client(pokie_app):
    """
    Barebones REST client
    """
    with pokie_app.test_client() as client:
        yield PokieClient(client)


@pytest.fixture(autouse=True)
def pokie_app(request, pokie_factory):
    """
    App initialization fixture

    Pokie config parameters are extracted from TestConfigTemplate
    """
    app, factory = pokie_factory
    cfg = app.di.get(DI_CONFIG)

    # pytest arguments can override the base setup
    if request.config.getvalue("reuse_db"):
        reuse_db = True
    else:
        reuse_db = cfg.get(CFG_TEST_DB_REUSE)

    if request.config.getvalue("skip_migrations"):
        skip_migrations = True
    else:
        skip_migrations = cfg.get(CFG_TEST_SKIP_MIGRATIONS)

    if request.config.getvalue("skip_fixtures"):
        skip_fixtures = True
    else:
        skip_fixtures = cfg.get(CFG_TEST_SKIP_FIXTURES)

    # -- app context
    if not cfg.get(CFG_TEST_SHARE_CTX):
        # if context isn't shared, create whole new application
        _, app = factory()

    # if db management is disabled, skip db management altogether
    if not cfg.get(CFG_TEST_MANAGE_DB):
        yield app
        return

    # -- db stuff
    test_db = cfg.get(CFG_TEST_DB_NAME, "test_pokie")
    try:
        # DI_DB container is replaced automatically
        _init_db(app, test_db, reuse_db, skip_migrations, skip_fixtures)

    except Exception as e:
        raise RuntimeError(
            "Error initializing database; does the test user has database create/drop privileges? Error: {}".format(
                str(e)
            )
        )

    yield app

    # cleanup
    if not reuse_db:
        conn = app.di.get(DI_DB)
        if conn:
            # discard old connection
            conn.close()
            # redo connection for drop purposes
            conn = _db_connection(app)
            mgr = PgManager(conn)
            mgr.drop_database(test_db)


def _db_connection(app, db_name: str = None):
    cfg = app.di.get(DI_CONFIG)
    db_cfg = {
        "dbname": "postgres" if db_name is None else db_name,
        "host": cfg.get(CFG_TEST_DB_HOST, "localhost"),
        "port": int(cfg.get(CFG_TEST_DB_PORT, 5432)),
        "user": cfg.get(CFG_TEST_DB_USER, "postgres"),
        "password": cfg.get(CFG_TEST_DB_PASSWORD, ""),
        "sslmode": None if not cfg.get(CFG_TEST_DB_SSL, "1") else "require",
    }
    return PgConnection(**db_cfg)


def _init_db(app, test_db, reuse_db, skip_migrations, skip_fixtures):
    if not test_db:
        # if test database name is empty, skip database handling altogether
        app.di.add(DI_DB, None)
        return None

    # first connection for administrative purposes
    conn = _db_connection(app, None)
    mgr = PgManager(conn)

    db_exists = mgr.database_exists(test_db)
    if db_exists and not reuse_db:
        mgr.drop_database(test_db)
        db_exists = False

    if not db_exists:
        mgr.create_database(test_db)

    # actual final connection
    conn = _db_connection(app, test_db)
    app.di.add(DI_DB, conn, replace=True)

    if not db_exists:
        pokie_main = app.di.get(DI_APP)
        pokie_main.cli_runner("db:init")

        if not skip_migrations:
            pokie_main.cli_runner("db:update")

        if not skip_fixtures:
            pokie_main.cli_runner("fixture:run")
