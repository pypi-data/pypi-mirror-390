from typing import Literal
from pydantic import BaseModel


class CrawlRequestSchema(BaseModel):
    crawl_request_id: int = 0
    order_id: int = 0
    args: dict = {"url": " "}


class CrawlResponseSchema(BaseModel):
    crawl_request_id: int = 0
    order_id: int = 0
    status: Literal["Pending", "Running", "Error", "Finished"] = ""
    result: dict = {}
