import pika

from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import AMQPError, ChannelError
from scrapy.crawler import Crawler
from scrapy.settings import Settings
from scrapy.exceptions import NotConfigured
from pydantic import ValidationError

from crawler_utils.rabbitmq.schemas import CrawlRequestSchema, CrawlResponseSchema
from crawler_utils.rabbitmq.utils import (
    make_connection_parameters_from_settings,
    queue_name_from_settings,
    get_from_crawler_or_connect,
    schema_from_settings,
)

import logging

logger = logging.getLogger(__name__)


class RabbitMQPipeline:
    def __init__(
        self,
        channel: BlockingChannel,
        connection_parameters: pika.ConnectionParameters,
        input_queue_name: str,
        output_queue_name: str,
        request_schema: CrawlRequestSchema,
        response_schema: CrawlResponseSchema,
    ):
        """Initialize the pipeline with channel, connection parameters and schemas.

        Args:
            channel: A pika BlockingChannel used to publish messages.
            connection_parameters: pika.ConnectionParameters used to (re)connect.
            input_queue_name: Name of the input queue for 'order' messages.
            output_queue_name: Name of the output queue for response messages.
            request_schema: Pydantic schema used to validate request payloads.
            response_schema: Pydantic schema used to validate response payloads.
        """
        self.channel = channel
        self.input_queue_name = input_queue_name
        self.output_queue_name = output_queue_name
        self.connection_parameters = connection_parameters
        self.request_schema = request_schema
        self.response_schema = response_schema

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        """Create and return a pipeline instance from a Scrapy Crawler.

        Reads RabbitMQ-related settings, establishes a confirmed channel and
        ensures the configured input/output queues exist. Raises
        `NotConfigured` if connection or queue checks fail.
        """
        connection_parameters = cls.make_connection_parameters_from_settings(
            crawler.settings
        )
        input_queue_name = cls.queue_name_from_settings(
            crawler.settings, "RABBITMQ_INPUT_QUEUE"
        )
        output_queue_name = cls.queue_name_from_settings(
            crawler.settings, "RABBITMQ_OUTPUT_QUEUE"
        )
        request_schema = cls.schema_from_settings(
            crawler.settings, "RABBITMQ_REQUEST_SCHEMA", CrawlRequestSchema
        )
        response_schema = cls.schema_from_settings(
            crawler.settings, "RABBITMQ_RESPONSE_SCHEMA", CrawlResponseSchema
        )

        try:
            channel = get_from_crawler_or_connect(crawler, connection_parameters)
            channel.confirm_delivery()
        except AMQPError as e:
            logger.exception(
                f"Got an error during connection attempt to {connection_parameters}"
            )
            raise NotConfigured("Failed to configure RabbitMQPipeline.") from e
        else:
            logger.info(
                f"Connection with RABBITMQ server {connection_parameters} was established."
            )

        for queue in (input_queue_name, output_queue_name):
            try:
                channel.queue_declare(queue, passive=True)
            except ChannelError as e:
                msg = f"Queue {queue} not ready!"
                logger.exception(msg)
                raise NotConfigured(msg) from e
            else:
                logger.info(f"Queue {queue} are ready!")

        return cls(
            channel,
            connection_parameters,
            input_queue_name,
            output_queue_name,
            request_schema,
            response_schema,
        )

    @staticmethod
    def make_connection_parameters_from_settings(
        settings: Settings,
    ) -> pika.ConnectionParameters:
        """Return pika.ConnectionParameters constructed from Scrapy settings.

        This is a thin wrapper around the helper in
        `crawler_utils.rabbitmq.utils` to keep the pipeline API convenient for
        tests and callers.
        """
        return make_connection_parameters_from_settings(settings)

    @staticmethod
    def queue_name_from_settings(settings: Settings, queue: str) -> str:
        """Resolve and return a queue name from Scrapy settings.

        `queue` is the settings key to look up (for example,
        "RABBITMQ_INPUT_QUEUE" or "RABBITMQ_OUTPUT_QUEUE").
        """
        return queue_name_from_settings(settings, queue)

    @staticmethod
    def schema_from_settings(
        settings: Settings, schema_name: str, schema_class: any
    ) -> any:
        """Load and return a Pydantic schema instance or class from settings.

        Falls back to `schema_class` when no custom schema is configured.
        """
        return schema_from_settings(settings, schema_name, schema_class)

    def close_spider(self, spider):
        """Close the underlying channel when the spider is closed.

        Safely closes the pika channel if it's open. No return value.
        """
        if self.channel.is_open:
            self.channel.close()

    def process_item(self, item: dict, spider):
        """Validate an item and publish it to the appropriate RabbitMQ queue.

        Picks the input or output queue based on item['type'] ("order" ->
        input/request queue; otherwise -> output/response queue). The item is
        validated with the configured Pydantic schema; invalid items are
        dropped (logged) and not published. Returns the original item on
        successful publish.
        """
        itemtype = item.get("type", "item")

        if itemtype == "order":
            queue, schema = self.input_queue_name, self.request_schema
            item_target_field = "args"
        else:
            queue, schema = self.output_queue_name, self.response_schema
            item_target_field = "result"

        # TODO: нужна наверное какая-то проверка на то что канал и очередь готовы
        try:
            body = schema.model_validate({item_target_field: item}).model_dump_json()
        except ValidationError:
            logger.exception(
                "Got message with wrong parameters. Message will be dropped."
            )
            return

        self.channel.basic_publish(exchange="", routing_key=queue, body=body)
        return item
