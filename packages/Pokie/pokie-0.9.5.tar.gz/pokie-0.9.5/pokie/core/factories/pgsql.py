from rick.base import Di
from rick_db.backend.pg import PgConnectionPool

from pokie.config import PokieConfig
from pokie.constants import (
    CFG_DB_NAME,
    CFG_DB_HOST,
    CFG_DB_PORT,
    CFG_DB_USER,
    CFG_DB_PASSWORD,
    CFG_DB_SSL,
    DI_DB,
    DI_CONFIG,
    CFG_DB_MINPROCS,
    CFG_DB_MAXPROCS,
)


def PgSqlFactory(_di: Di):
    """
    PostgreSQL connection factory
    Note: The connection is only created when the resource is accessed on Di
    """

    @_di.register(DI_DB)
    def _factory(_di: Di):
        cfg = _di.get(DI_CONFIG)
        db_cfg = {
            "dbname": cfg.get(CFG_DB_NAME, "postgres"),
            "host": cfg.get(CFG_DB_HOST, "localhost"),
            "port": int(cfg.get(CFG_DB_PORT, 5432)),
            "user": cfg.get(CFG_DB_USER, "postgres"),
            "password": cfg.get(CFG_DB_PASSWORD, ""),
            "sslmode": None if not cfg.get(CFG_DB_SSL, "1") else "require",
            "minconn": cfg.get(CFG_DB_MINPROCS, PokieConfig.DB_MINPROCS),
            "maxconn": cfg.get(CFG_DB_MAXPROCS, PokieConfig.DB_MAXPROCS),
        }
        return PgConnectionPool(**db_cfg)
