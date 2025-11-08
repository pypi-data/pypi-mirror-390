from typing import Optional

from rick.base import Di
from rick.mixin import Injectable

from pokie.constants import DI_DB
from pokie_test.dto import CustomerRecord
from pokie_test.repository import CustomerRepository


class CustomerService(Injectable):
    def __init__(self, di: Di):
        super().__init__(di)

    def get_customer(self, id_customer: str) -> Optional[CustomerRecord]:
        return self.repo_customer().fetch_pk(id_customer)

    def repo_customer(self) -> CustomerRepository:
        return CustomerRepository(self.get_di().get(DI_DB))
