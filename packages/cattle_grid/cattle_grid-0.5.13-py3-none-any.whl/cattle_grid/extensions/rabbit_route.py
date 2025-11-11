from collections.abc import Callable
from dataclasses import dataclass


from faststream.rabbit import RabbitRoute

from cattle_grid.app import access_methods

from .util import rabbit_queue_for_name_and_routing_key


@dataclass
class Route:
    func: Callable
    routing_key: str
    name: str
    exchange_name: str

    def build(self):
        if self.exchange_name == "activity":
            exchange = access_methods.get_activity_exchange()
        elif self.exchange_name == "account":
            exchange = access_methods.get_account_exchange()
        else:
            raise Exception(f"unknown exchange name {self.exchange_name}")

        return RabbitRoute(
            self.func,
            queue=rabbit_queue_for_name_and_routing_key(self.name, self.routing_key),
            exchange=exchange,
            title=self.routing_key,
        )
