from __future__ import annotations

import os
from typing import Any, Dict, Optional, TypeVar, Union

import httpx
from .errors import ApiError, OlyptikError
from .models import (
    Crawl,
    CrawlResult,
    CrawlLog,
    PaginationResult,
    StartCrawlPayload,
    StartScrapePayload,
    QueryCrawlsPayload,
    ScrapeResponse,
    UrlResult
)

T = TypeVar("T")


DEFAULT_TIMEOUT = 15.0


class BaseClient:
    def __init__(self, api_key: str, endpoint: Optional[str] = None, timeout: float = DEFAULT_TIMEOUT):
        self.endpoint = endpoint or os.getenv("OLYPTIK_ENDPOINT", "https://api.olyptik.io")
        self.api_key = api_key
        self.timeout = timeout

    @property
    def headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "olyptik-python-sdk/0.1.0 (+https://www.olyptik.io)",
            "Accept": "application/json",
        }


class Olyptik(BaseClient):
    def __init__(self, api_key: str, endpoint: Optional[str] = None, timeout: float = DEFAULT_TIMEOUT):
        super().__init__(api_key=api_key, endpoint=endpoint, timeout=timeout)
        self._client = httpx.Client(timeout=timeout)

    def _handle(self, res: httpx.Response) -> Any:
        if res.status_code >= 400:
            # try json first
            try:
                data = res.json()
                message = data.get("message") or res.text
            except Exception:
                data = None
                message = res.text
            raise ApiError(res.status_code, message, data)
        if res.headers.get("content-type", "").startswith("application/json"):
            return res.json()
        return res.text

    def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        """Make synchronous HTTP request."""
        url = f"{self.endpoint}{path}"
        try:
            return self._client.request(method, url, headers=self.headers, **kwargs)
        except httpx.HTTPError as e:
            raise OlyptikError(str(e))

    def _safe_create_crawl(self, data: Dict[str, Any]) -> Crawl:
        """Safely create a Crawl object, filtering out unexpected fields."""
        from dataclasses import fields
        valid_fields = {f.name for f in fields(Crawl)}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return Crawl(**filtered_data)

    def _safe_create_crawl_result(self, data: Dict[str, Any]) -> CrawlResult:
        """Safely create a CrawlResult object, filtering out unexpected fields."""
        from dataclasses import fields
        valid_fields = {f.name for f in fields(CrawlResult)}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return CrawlResult(**filtered_data)

    def _safe_create_crawl_log(self, data: Dict[str, Any]) -> CrawlLog:
        """Safely create a CrawlLog object, filtering out unexpected fields."""
        from dataclasses import fields
        valid_fields = {f.name for f in fields(CrawlLog)}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return CrawlLog(**filtered_data)

    def _safe_create_url_result(self, data: Dict[str, Any]) -> UrlResult:
        """Safely create a UrlResult object, filtering out unexpected fields."""
        from dataclasses import fields
        valid_fields = {f.name for f in fields(UrlResult)}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return UrlResult(**filtered_data)

    def _safe_create_scrape_response(self, data: Dict[str, Any]) -> ScrapeResponse:
        """Safely create a ScrapeResponse object, filtering out unexpected fields."""
        from dataclasses import fields
        valid_fields = {f.name for f in fields(ScrapeResponse)}
        # Convert results array to UrlResult objects
        if "results" in data and isinstance(data["results"], list):
            data["results"] = [self._safe_create_url_result(item) for item in data["results"]]
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return ScrapeResponse(**filtered_data)

    def run_crawl(self, payload: Union[Dict[str, Any], StartCrawlPayload]) -> Crawl:
        if isinstance(payload, StartCrawlPayload):
            payload = payload.__dict__
        res = self._request("POST", "/crawls", json=payload)
        data = self._handle(res)
        return self._safe_create_crawl(data)

    def get_crawl(self, crawl_id: str) -> Crawl:
        res = self._request("GET", f"/crawls/{crawl_id}")
        data = self._handle(res)
        return self._safe_create_crawl(data)

    def abort_crawl(self, crawl_id: str) -> Crawl:
        res = self._request("PATCH", f"/crawls/{crawl_id}/abort")
        data = self._handle(res)
        return self._safe_create_crawl(data)

    def query_crawls(self, payload: Union[Dict[str, Any], QueryCrawlsPayload]) -> PaginationResult[Crawl]:
        if isinstance(payload, QueryCrawlsPayload):
            payload = payload.__dict__
        res = self._request("POST", "/crawls/query", json=payload)
        data = self._handle(res)
        # Convert the results to safe Crawl objects
        if "results" in data and isinstance(data["results"], list):
            data["results"] = [self._safe_create_crawl(item) for item in data["results"]]
        return PaginationResult[Crawl](**data)  # type: ignore[arg-type]

    def get_crawl_results(self, crawl_id: str, page: int = 0, limit: int = 50) -> PaginationResult[CrawlResult]:
        res = self._request("GET", f"/crawls-results/{crawl_id}", params={"page": page, "limit": limit})
        data = self._handle(res)
        # Convert the results to safe CrawlResult objects
        if "results" in data and isinstance(data["results"], list):
            data["results"] = [self._safe_create_crawl_result(item) for item in data["results"]]
        return PaginationResult[CrawlResult](**data)  # type: ignore[arg-type]

    def get_crawl_logs(self, crawl_id: str, page: int = 1, limit: int = 1200) -> PaginationResult[CrawlLog]:
        res = self._request("GET", f"/crawl-logs/{crawl_id}", params={"page": page, "limit": limit})
        data = self._handle(res)
        # Convert the results to safe CrawlLog objects
        if "results" in data and isinstance(data["results"], list):
            data["results"] = [self._safe_create_crawl_log(item) for item in data["results"]]
        return PaginationResult[CrawlLog](**data)  # type: ignore[arg-type]

    def scrape(self, payload: Union[Dict[str, Any], StartScrapePayload]) -> ScrapeResponse:
        if isinstance(payload, StartScrapePayload):
            payload = payload.__dict__
        res = self._request("POST", "/scrape", json=payload)
        data = self._handle(res)
        return self._safe_create_scrape_response(data)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "Olyptik":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        self.close()


class AsyncOlyptik(BaseClient):
    def __init__(self, api_key: str, endpoint: Optional[str] = None, timeout: float = DEFAULT_TIMEOUT):
        super().__init__(api_key=api_key, endpoint=endpoint, timeout=timeout)
        self._client = httpx.AsyncClient(timeout=timeout)

    def _safe_create_crawl(self, data: Dict[str, Any]) -> Crawl:
        """Safely create a Crawl object, filtering out unexpected fields."""
        from dataclasses import fields
        valid_fields = {f.name for f in fields(Crawl)}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return Crawl(**filtered_data)

    def _safe_create_crawl_result(self, data: Dict[str, Any]) -> CrawlResult:
        """Safely create a CrawlResult object, filtering out unexpected fields."""
        from dataclasses import fields
        valid_fields = {f.name for f in fields(CrawlResult)}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return CrawlResult(**filtered_data)

    def _safe_create_crawl_log(self, data: Dict[str, Any]) -> CrawlLog:
        """Safely create a CrawlLog object, filtering out unexpected fields."""
        from dataclasses import fields
        valid_fields = {f.name for f in fields(CrawlLog)}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return CrawlLog(**filtered_data)

    def _safe_create_url_result(self, data: Dict[str, Any]) -> UrlResult:
        """Safely create a UrlResult object, filtering out unexpected fields."""
        from dataclasses import fields
        valid_fields = {f.name for f in fields(UrlResult)}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return UrlResult(**filtered_data)

    def _safe_create_scrape_response(self, data: Dict[str, Any]) -> ScrapeResponse:
        """Safely create a ScrapeResponse object, filtering out unexpected fields."""
        from dataclasses import fields
        valid_fields = {f.name for f in fields(ScrapeResponse)}
        # Convert results array to UrlResult objects
        if "results" in data and isinstance(data["results"], list):
            data["results"] = [self._safe_create_url_result(item) for item in data["results"]]
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return ScrapeResponse(**filtered_data)

    def _handle(self, res: httpx.Response) -> Any:
        if res.status_code >= 400:
            try:
                data = res.json()
                message = data.get("message") or res.text
            except Exception:
                data = None
                message = res.text
            raise ApiError(res.status_code, message, data)
        if res.headers.get("content-type", "").startswith("application/json"):
            return res.json()
        return res.text

    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        """Make asynchronous HTTP request."""
        url = f"{self.endpoint}{path}"
        try:
            return await self._client.request(method, url, headers=self.headers, **kwargs)
        except httpx.HTTPError as e:
            raise OlyptikError(str(e))

    async def run_crawl(self, payload: Union[Dict[str, Any], StartCrawlPayload]) -> Crawl:
        if isinstance(payload, StartCrawlPayload):
            payload = payload.__dict__
        res = await self._request("POST", "/crawls", json=payload)
        data = self._handle(res)
        return self._safe_create_crawl(data)

    async def get_crawl(self, crawl_id: str) -> Crawl:
        res = await self._request("GET", f"/crawls/{crawl_id}")
        data = self._handle(res)
        return self._safe_create_crawl(data)

    async def query_crawls(self, payload: Union[Dict[str, Any], QueryCrawlsPayload]) -> PaginationResult[Crawl]:
        if isinstance(payload, QueryCrawlsPayload):
            payload = payload.__dict__
        res = await self._request("POST", "/crawls/query", json=payload)
        data = self._handle(res)
        # Convert the results to safe Crawl objects
        if "results" in data and isinstance(data["results"], list):
            data["results"] = [self._safe_create_crawl(item) for item in data["results"]]
        return PaginationResult[Crawl](**data)  # type: ignore[arg-type]

    async def abort_crawl(self, crawl_id: str) -> Crawl:
        res = await self._request("PATCH", f"/crawls/{crawl_id}/abort")
        data = self._handle(res)
        return self._safe_create_crawl(data)

    async def get_crawl_results(self, crawl_id: str, page: int = 0, limit: int = 50) -> PaginationResult[CrawlResult]:
        res = await self._request("GET", f"/crawls-results/{crawl_id}", params={"page": page, "limit": limit})
        data = self._handle(res)
        # Convert the results to safe CrawlResult objects
        if "results" in data and isinstance(data["results"], list):
            data["results"] = [self._safe_create_crawl_result(item) for item in data["results"]]
        return PaginationResult[CrawlResult](**data)  # type: ignore[arg-type]

    async def get_crawl_logs(self, crawl_id: str, page: int = 1, limit: int = 1200) -> PaginationResult[CrawlLog]:
        res = await self._request("GET", f"/crawl-logs/{crawl_id}", params={"page": page, "limit": limit})
        data = self._handle(res)
        # Convert the results to safe CrawlLog objects
        if "results" in data and isinstance(data["results"], list):
            data["results"] = [self._safe_create_crawl_log(item) for item in data["results"]]
        return PaginationResult[CrawlLog](**data)  # type: ignore[arg-type]

    async def scrape(self, payload: Union[Dict[str, Any], StartScrapePayload]) -> ScrapeResponse:
        if isinstance(payload, StartScrapePayload):
            payload = payload.__dict__
        res = await self._request("POST", "/scrape", json=payload)
        data = self._handle(res)
        return self._safe_create_scrape_response(data)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncOlyptik":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        await self.aclose()


async def _asleep(seconds: float) -> None:
    # local import to avoid adding asyncio at module import time
    import asyncio

    await asyncio.sleep(seconds)


