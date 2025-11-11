import pika
import logging

from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import AMQPError, ChannelError
from scrapy import Spider, signals
from scrapy.crawler import Crawler, ExecutionEngine
from scrapy.exceptions import DontCloseSpider, NotConfigured
from scrapy.settings import Settings
from pydantic import ValidationError

from crawler_utils.rabbitmq.schemas import CrawlRequestSchema
from crawler_utils.rabbitmq.utils import (
    get_from_crawler_or_connect,
    make_connection_parameters_from_settings,
    queue_name_from_settings,
    schema_from_settings,
)

RABBITMQ_QUEUE_NAME = "scrapy_queue"

logger = logging.getLogger(__name__)
logging.getLogger("pika").setLevel(logging.WARN)


class RabbitMQExtension:
    def __init__(
        self,
        crawler: Crawler,
        channel: BlockingChannel,
        connection_parameters: pika.ConnectionParameters,
        queue_name: str,
        request_schema: CrawlRequestSchema,
    ):
        if not crawler.settings.getbool("RABBITMQ_ENABLED"):
            raise NotConfigured
        self.crawler = crawler
        self.spider: Spider | None = None
        self.engine: ExecutionEngine | None = None
        self.connection_parameters = connection_parameters
        self.queue_name = queue_name
        self.channel = channel
        setattr(crawler, "rabbitmq_channel", self.channel)
        self.delivery_tag = None
        self.request_schema = request_schema

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        """Create and return an extension instance from a Scrapy Crawler.

        Reads and mutates some Scrapy settings (dupefilter and pipelines),
        establishes a RabbitMQ channel, checks the queue existence and
        registers signal handlers. Raises `NotConfigured` when setup fails.
        """
        # TODO: не надо отключать дедупликацию совсем. Она должна работать в рамках одного ордера
        crawler.settings.set("DUPEFILTER_CLASS", "scrapy.dupefilters.BaseDupeFilter")
        pipelines = crawler.settings.getdict("ITEM_PIPELINES")
        pipelines.update(
            {"crawler_utils.rabbitmq.rabbitmq_pipeline.RabbitMQPipeline": 442}
        )
        crawler.settings.setdict({"ITEM_PIPELINES": pipelines})

        connection_parameters = cls.parameters_from_settings(crawler.settings)
        queue_name = cls.queue_name_from_settings(crawler.settings)
        request_schema = schema_from_settings(
            crawler.settings, "RABBITMQ_REQUEST_SCHEMA", CrawlRequestSchema
        )

        try:
            channel = get_from_crawler_or_connect(crawler, connection_parameters)
        except AMQPError as e:
            logger.exception(
                f"Got an error during connection attempt to {connection_parameters}"
            )
            raise NotConfigured("Failed to configure RabbitMQExtension.") from e
        else:
            logger.info(
                f"Connection with RABBITMQ server {connection_parameters} was established."
            )

        try:
            channel.queue_declare(queue_name, passive=True)
        except ChannelError as e:
            msg = f"Queue {queue_name} not ready!"
            logger.exception(msg)
            raise NotConfigured(msg) from e

        ext = cls(crawler, channel, connection_parameters, queue_name, request_schema)

        crawler.signals.connect(ext.engine_started, signal=signals.engine_started)
        crawler.signals.connect(ext.spider_idle, signal=signals.spider_idle)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)

        return ext

    @staticmethod
    def parameters_from_settings(settings: Settings) -> pika.ConnectionParameters:
        """Build and return pika.ConnectionParameters from Scrapy settings.

        Thin wrapper around the helper in `crawler_utils.rabbitmq.utils`.
        """
        return make_connection_parameters_from_settings(settings)

    @staticmethod
    def queue_name_from_settings(settings: Settings) -> str:
        """Resolve and return the input queue name from settings.

        Looks up the configured settings key (defaults to
        "RABBITMQ_INPUT_QUEUE") and returns the resolved queue name.
        """
        return queue_name_from_settings(settings, "RABBITMQ_INPUT_QUEUE")

    def engine_started(self):
        """Signal handler invoked when the Scrapy engine starts.

        Stores references to the current spider and engine and begins
        waiting for orders from RabbitMQ.
        """
        logger.info("Rabbitmq extension started.")
        self.spider = self.crawler.spider
        self.engine = self.crawler.engine
        self.wait_for_order(self.crawl)

    def spider_idle(self):
        """Signal handler for when the spider becomes idle.

        Acknowledges any pending delivery, then restarts waiting for the
        next order and prevents the spider from closing by raising
        `DontCloseSpider`.
        """
        if self.delivery_tag:
            self.channel.basic_ack(delivery_tag=self.delivery_tag)
            self.delivery_tag = None
        logger.info("Spider idle.")
        self.wait_for_order(callback=self.crawl)
        raise DontCloseSpider

    def spider_closed(self):
        """Signal handler for spider closed event.

        Ensures the RabbitMQ channel is closed and logs the shutdown.
        """
        self.close_channel()
        logger.info("Spider closed.")

    def close_channel(self):
        """Safely close the underlying pika channel if it's open."""
        if self.channel.is_open:
            self.channel.close()

    def wait_for_order(self, /, callback):
        """Start consuming messages from the configured queue.

        Registers `callback` as the consumer callback and starts the
        blocking consumption loop. This call blocks until consumption is
        stopped or an error occurs.
        """
        self.channel.basic_consume(self.queue_name, callback)
        logger.info("Waiting for orders!")
        self.channel.start_consuming()

    def crawl(self, ch: BlockingChannel, method, properties, body):
        """Callback invoked for each incoming order message.

        Validates the incoming JSON payload against the configured
        `request_schema`. On success, reinitializes the spider (or calls
        `reinit_spider` if available), records the delivery tag for later
        acknowledgement, stops consumption and schedules the spider's
        start_requests on the Scrapy engine. Invalid messages are
        acknowledged and dropped.
        """
        assert self.engine
        assert self.spider

        logger.info(f"Got new order: {body}.")

        try:
            data = self.request_schema.model_validate_json(body)
        except ValidationError:
            logger.exception(
                "Got message with wrong json syntax. Message will be dropped."
            )
            ch.basic_ack(method.delivery_tag)
            logger.info("Waiting for orders!")
            return

        if hasattr(self.spider, "reinit_spider"):
            self.spider.reinit_spider(**data.args)  # type: ignore
        else:
            self.spider.__init__(**data)

        self.delivery_tag = method.delivery_tag
        ch.stop_consuming()

        # TODO: Надо бы наверное делать это асинхронно?
        for request in self.spider.start_requests():
            self.engine.crawl(request)
