import pika

from typing import Mapping

from pika.adapters.blocking_connection import BlockingChannel
from scrapy.crawler import Crawler
from scrapy.settings import Settings
from scrapy.utils.misc import load_object

from crawler_utils.rabbitmq.schemas import CrawlRequestSchema, CrawlResponseSchema

RABBITMQ_USER = "guest"
RABBITMQ_PASSWORD = "guest"
RABBITMQ_CONNECTION_PARAMETERS = {"host": "localhost", "port": 5672}


def connect_to_rabbitmq(parameters: pika.ConnectionParameters) -> BlockingChannel:
    connection = pika.BlockingConnection(parameters=parameters)
    channel = connection.channel()
    return channel


def get_from_crawler_or_connect(
    crawler: Crawler, parameters: pika.ConnectionParameters
):
    if hasattr(crawler, "rabbitmq_channel") and isinstance(
        crawler.rabbitmq_channel,
        BlockingChannel,  # type: ignore
    ):
        channel = crawler.rabbitmq_channel  # type: ignore
    else:
        channel = connect_to_rabbitmq(parameters)
        setattr(crawler, "rabbitmq_channel", channel)
    return channel


def _make_connection_parameters_from_data(
    username: str, password: str, host: str, port: int
) -> pika.ConnectionParameters:
    credentials = pika.PlainCredentials(username=username, password=password)
    parameters = pika.ConnectionParameters(
        host=host, port=port, credentials=credentials
    )
    return parameters


def make_connection_parameters_from_settings(
    settings: Settings,
) -> pika.ConnectionParameters:
    username = settings.get("RABBITMQ_USER", RABBITMQ_USER)
    password = settings.get("RABBITMQ_PASSWORD", RABBITMQ_PASSWORD)
    connection_parameters: Mapping[str, str] | None = settings.get(
        "RABBITMQ_CONNECTION_PARAMETERS"
    )

    assert username
    assert password
    assert connection_parameters

    host: str = str(
        connection_parameters.get("host", RABBITMQ_CONNECTION_PARAMETERS["host"])
    )
    port: int = int(
        connection_parameters.get("port", RABBITMQ_CONNECTION_PARAMETERS["port"])
    )

    return _make_connection_parameters_from_data(username, password, host, port)


def queue_name_from_settings(settings: Settings, settings_name: str):
    queue_name = settings.get(settings_name)
    assert queue_name
    return queue_name


def schema_from_settings(
    settings: Settings,
    setting_name: str,
    default: type[CrawlRequestSchema] | type[CrawlResponseSchema],
):
    schema = load_object(settings.get(setting_name, default))
    assert schema
    return schema
