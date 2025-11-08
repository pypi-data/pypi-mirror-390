import uuid
from rick.resource.config import StrOrFile


class PokieConfig:
    # default HTTP Exception Handler - 404 and 500 exceptions
    HTTP_ERROR_HANDLER = "pokie.http.HttpErrorHandler"

    # if true, all endpoints are authenticated by default
    USE_AUTH = True

    # Authentication provider
    AUTH_PROVIDER = "JWTProvider"

    # If true, ACL are loaded for users
    AUTH_ACL = True

    # Secret key for flask-login hashing
    AUTH_SECRET = uuid.uuid4().hex

    # Enables cache on User and Acl Services
    AUTH_USE_CACHE = True

    # cache table-related metadata (such as primary key info)
    # development should be false
    DB_CACHE_METADATA = False

    # Postgresql Configuration
    DB_NAME = "pokie"
    DB_HOST = "localhost"
    DB_PORT = 5432
    DB_USER = StrOrFile("postgres")
    DB_PASSWORD = StrOrFile("")
    DB_SSL = True
    DB_MINPROCS = 5
    DB_MAXPROCS = 15

    # Redis Configuration
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_PASSWORD = StrOrFile("")
    REDIS_DB = 0
    REDIS_SSL = "1"

    # Pytest Configuration
    TEST_DB_NAME = "pokie_test"  # test database parameters
    TEST_DB_HOST = "localhost"
    TEST_DB_PORT = 5432
    TEST_DB_USER = StrOrFile("postgres")
    TEST_DB_PASSWORD = StrOrFile("")
    TEST_DB_SSL = False

    TEST_MANAGE_DB = (
        False  # if false, unit testing does not manage db creation/migration
    )
    TEST_SHARE_CTX = False  # if false, each test has a separate context
    TEST_DB_REUSE = False  # if true, database is not dropped/recreated
    TEST_SKIP_MIGRATIONS = False  # if true, migrations are not run when recreating db
    TEST_SKIP_FIXTURES = False  # if true, fixtures are not run when recreating db
