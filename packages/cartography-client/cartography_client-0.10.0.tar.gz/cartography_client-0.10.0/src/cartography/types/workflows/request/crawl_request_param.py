# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["CrawlRequestParam"]


class CrawlRequestParam(TypedDict, total=False):
    bucket_name: Required[str]

    crawl_id: Required[str]

    engines: Required[
        List[Literal["FLEET", "ZENROWS", "SCRAPINGBEE", "FLEET_ASYNC", "FLEET_WORKFLOW", "ASYNC_FLEET_STICKY"]]
    ]

    url: Required[str]

    absolute_only: bool

    agentic: bool

    batch_size: int

    camo: bool

    depth: int

    keep_external: bool

    max_urls: int

    max_workers: int

    proxy_url: Optional[str]

    session_id: Optional[str]

    stealth: bool

    teardown: bool

    visit_external: bool

    wait_until: Optional[Literal["domcontentloaded", "load", "networkidle", "commit"]]
