from faststream import FastStream
from faststream.rabbit import RabbitBroker

import logging

from contextlib import asynccontextmanager

from cattle_grid.app import app_globals
from cattle_grid.app.lifespan import common_lifespan

from .app import add_routers_to_broker, init_extensions

from .dependencies.globals import global_container

from .extensions.load import (
    lifespan_from_extensions,
)
from .exchange.exception import exception_middleware

logging.basicConfig(level=logging.INFO)

global_container.load_config()

extensions = init_extensions(global_container.config)

broker = RabbitBroker(
    app_globals.application_config.amqp_url,  # type:ignore
    middlewares=[exception_middleware],
)
add_routers_to_broker(broker, extensions, global_container.config)


@asynccontextmanager
async def lifespan():
    async with common_lifespan():
        async with lifespan_from_extensions(extensions):
            yield


app = FastStream(broker, lifespan=lifespan)


@app.after_startup
async def declare_exchanges() -> None:
    if app_globals.internal_exchange:
        await broker.declare_exchange(app_globals.internal_exchange)
    if app_globals.activity_exchange:
        await broker.declare_exchange(app_globals.activity_exchange)
