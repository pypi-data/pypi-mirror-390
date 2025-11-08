# Version
POKIE_VERSION = ["0", "9", "5"]


def get_version():
    return ".".join(POKIE_VERSION)


# Http Codes
HTTP_OK = 200
HTTP_BADREQ = 400
HTTP_NOAUTH = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_NOT_ALLOWED = 405
HTTP_INTERNAL_ERROR = 500

# DI Keys
DI_CONFIG = "config"  # config object
DI_FLASK = "app"  # flask application
DI_APP = "main"  # pokie application
DI_MODULES = "modules"  # module list
DI_SERVICES = "svc_manager"  # service manager
DI_DB = "db"  # database client
DI_REDIS = "redis"  # redis client
DI_CACHE = "cache"  # generic cache client
DI_EVENTS = "event_manager"  # event manager
DI_TTY = "tty"  # console writer
DI_SIGNAL = "signal"  # signal manager
DI_HTTP_ERROR_HANDLER = "http_error_handler"  # http exception manager

# Flask error Handler configuration
CFG_HTTP_ERROR_HANDLER = "http_error_handler"

# DB Configuration
CFG_DB_NAME = "db_name"
CFG_DB_HOST = "db_host"
CFG_DB_PORT = "db_port"
CFG_DB_USER = "db_user"
CFG_DB_PASSWORD = "db_password"
CFG_DB_SSL = "db_ssl"
CFG_DB_MINPROCS = "db_minprocs"
CFG_DB_MAXPROCS = "db_maxprocs"

# Redis Configuration
CFG_REDIS_HOST = "redis_host"
CFG_REDIS_PORT = "redis_port"
CFG_REDIS_PASSWORD = "redis_password"
CFG_REDIS_DB = "redis_db"
CFG_REDIS_SSL = "redis_ssl"

# Auth Configuration
CFG_AUTH_SECRET = "auth_secret"


# default list size for DBGrid Operations
DEFAULT_LIST_SIZE = 100


# unit testing constants
POKIE_NAMESPACE = "POKIE_NAMESPACE"
POKIE_APP = "POKIE_APP"
POKIE_FACTORY = "POKIE_FACTORY"

# Testing configuration
CFG_TEST_DB_NAME = "test_db_name"
CFG_TEST_DB_HOST = "test_db_host"
CFG_TEST_DB_PORT = "test_db_port"
CFG_TEST_DB_USER = "test_db_user"
CFG_TEST_DB_PASSWORD = "test_db_password"
CFG_TEST_DB_SSL = "test_db_ssl"

CFG_TEST_MANAGE_DB = "test_manage_db"
CFG_TEST_SHARE_CTX = "test_share_ctx"
CFG_TEST_DB_REUSE = "test_db_reuse"
CFG_TEST_SKIP_MIGRATIONS = "test_skip_migrations"
CFG_TEST_SKIP_FIXTURES = "test_skip_fixtures"

# Default TTLs
TTL_1H = 3600
TTL_1D = 86400
