from typing import Any

from typing_extensions import override

from adsdatahub.client import Client
from adsdatahub.types import CustomerId


class MockClient(Client):
    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        pass

    @override
    def customer(self, customer_id: CustomerId):
        from adsdatahub.client.customer.mock_customer import MockCustomerClient

        return MockCustomerClient(self, customer_id)
