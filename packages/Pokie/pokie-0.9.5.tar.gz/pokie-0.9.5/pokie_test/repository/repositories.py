from rick_db import Repository

from pokie_test.dto import CustomerRecord


class CustomerRepository(Repository):
    def __init__(self, db):
        super().__init__(db, CustomerRecord)
