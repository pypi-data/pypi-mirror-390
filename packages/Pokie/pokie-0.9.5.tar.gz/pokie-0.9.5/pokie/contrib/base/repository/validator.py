from rick_db import ConnectionInterface
from rick_db.repository import GenericRepository
from rick_db.sql import Select


class ValidatorRepository(GenericRepository):
    def __init__(self, db: ConnectionInterface):
        """
        Constructor
        This class is a stub repository; it doesn't have Record class, table name or schema
        :param db:
        """
        super(ValidatorRepository, self).__init__(db, "")

    def pk_exists(self, pk_value, pk_name, table_name, schema=None) -> bool:
        sql, values = (
            Select(self.dialect)
            .from_(table_name, cols=[pk_name], schema=schema)
            .where(pk_name, "=", pk_value)
            .assemble()
        )
        with self.cursor() as c:
            record = c.fetchone(sql, values)
            return record is not None
