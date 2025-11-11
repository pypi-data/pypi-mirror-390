"""The before_all, _scenario, and after_scenario functions
need to be imported in your environment.py file, e.g.

```python title="features/environment.py"
--8<-- "./features/environment.py"
```
"""

import aiohttp
import asyncio
import logging

from behave.runner import Context
from behave.model import Scenario

from cattle_grid.config import load_settings
from cattle_grid.account.account import delete_account
from cattle_grid.database import database_session
from .reporting import publish_reporting

logger = logging.getLogger(__name__)


async def create_session(context: Context):
    if not context.session:
        context.session = aiohttp.ClientSession()


async def close_session(context: Context):
    config = load_settings()

    async with database_session(db_url=config.db_url) as session:  # type: ignore
        for name, connection in context.connections.items():
            try:
                if name in context.actors:
                    await connection.trigger(
                        "delete_actor",
                        {
                            "actor": context.actors[name].get("id"),
                        },
                    )
                    await asyncio.sleep(0.1)

                await delete_account(session, name, name)
            except Exception as e:
                logger.exception(e)

    await context.session.close()

    try:
        for connection in context.connections.values():
            connection.task.cancel()
            try:
                await connection.task
            except asyncio.CancelledError:
                pass
    except Exception as e:
        logger.exception(e)


def before_all(context: Context):
    """Called in features/environment.py

    Ensures that default variables, `context.session`, `.actors`, `.connections`
    exist.
    """
    context.session = None

    context.actors = {}
    context.connections = {}


def before_scenario(context: Context, scenario: Scenario):
    """Called in features/environment.py

    Opens an [aiohttp.ClientSession][] and sets it to `context.session`.
    """
    asyncio.get_event_loop().run_until_complete(create_session(context))

    context.actors = {}
    context.connections = {}

    asyncio.get_event_loop().run_until_complete(
        publish_reporting(
            "scenario",
            {
                "name": scenario.name,
                "file": scenario.filename,
                "description": scenario.description,
            },
        )
    )


def after_scenario(context: Context, scenario: Scenario):
    """Called in features/environment.py

    Deletes the created actors and associated accounts.
    Closes the aiohttp.ClientSession.
    """

    asyncio.get_event_loop().run_until_complete(
        publish_reporting(
            "scenario_end",
            {},
        )
    )

    if context.session:
        asyncio.get_event_loop().run_until_complete(close_session(context))
        context.session = None
