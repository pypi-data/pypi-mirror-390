from faststream import ExceptionMiddleware

import logging

from cattle_grid.model.account import ErrorMessage
from cattle_grid.dependencies import AccountExchangePublisher

from .annotations import AccountName, RoutingKey

logger = logging.getLogger(__name__)

exception_middleware = ExceptionMiddleware()


@exception_middleware.add_handler(Exception)
async def exception_handler(
    exception: Exception,
    name: AccountName,
    routing_key: RoutingKey,
    publisher: AccountExchangePublisher,
):
    logger.error("Processing error occurred for %s", name)
    logger.exception(exception)

    await publisher(
        ErrorMessage(message=str(exception).split("\n"), routing_key=routing_key),
        routing_key=f"error.{name}",
    )
