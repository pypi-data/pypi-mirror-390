import logging
from dynaconf import Dynaconf
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ApplicationConfig(BaseModel):
    """Configuration values relevant to the base application"""

    db_url: str = Field(description="Database URL")
    amqp_url: str = Field(description="location of the rabbitmq broker")
    testing: bool = Field(description="wether the application is in testing mode")

    @staticmethod
    def from_settings(settings: Dynaconf) -> "ApplicationConfig":
        db_url = settings.get("db_url")
        if db_url is None:
            db_url = settings.db_uri
            logger.warning("Please update db_uri to db_url")

        amqp_url = settings.get("amqp_url")
        if amqp_url is None:
            amqp_url = settings.amqp_uri
            logger.warning("Please update amqp_uri to amqp_url")

        testing = settings.get("testing", {}).get("enabled", False)
        if testing:
            logger.warning("Running in TESTING mode")

        return ApplicationConfig(db_url=db_url, amqp_url=amqp_url, testing=testing)
