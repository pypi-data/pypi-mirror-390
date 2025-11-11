from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar


class CrawlStatus(str, Enum):
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    TIMED_OUT = "timed_out"
    FAILED = "failed"
    ABORTED = "aborted"
    ERROR = "error"


class EngineType(str, Enum):
    PLAYWRIGHT = "playwright"
    CHEERIO = "cheerio"
    AUTO = "auto"


@dataclass
class StartCrawlPayload:
    startUrl: str
    maxResults: Optional[int] = None
    maxDepth: Optional[int] = None
    includeLinks: Optional[bool] = None
    useSitemap: Optional[bool] = None
    entireWebsite: Optional[bool] = None
    excludeNonMainTags: Optional[bool] = None
    deduplicateContent: Optional[bool] = None
    extraction: Optional[str] = None
    timeout: Optional[int] = None
    engineType: Optional[EngineType] = None
    useStaticIps: Optional[bool] = None


@dataclass
class StartScrapePayload:
    urls: List[str]
    useSitemap: Optional[bool] = None
    entireWebsite: Optional[bool] = None
    maxResults: Optional[int] = None
    maxDepth: Optional[int] = None
    includeLinks: Optional[bool] = None
    excludeNonMainTags: Optional[bool] = None
    timeout: Optional[int] = None
    engineType: Optional[EngineType] = None
    useStaticIps: Optional[bool] = None
    deduplicateContent: Optional[bool] = None
    extraction: Optional[str] = None


@dataclass
class QueryCrawlsPayload:
    page: int = 0
    status: Optional[List[CrawlStatus]] = None
    startUrls: Optional[List[str]] = None


@dataclass
class CrawlResult:
    crawlId: str
    url: str
    title: str
    markdown: str
    teamId: Optional[str] = None
    depthOfUrl: Optional[int] = None
    createdAt: Optional[str] = None
    anonymousUserId: Optional[str] = None
    isSuccess: Optional[bool] = None
    error: Optional[str] = None
    isDeleted: Optional[bool] = None


class CrawlLogLevel(str, Enum):
    INFO = "info"
    DEBUG = "debug"
    WARN = "warn"
    ERROR = "error"


@dataclass
class CrawlLog:
    id: str
    message: str
    level: CrawlLogLevel
    description: str
    crawlId: str
    teamId: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    createdAt: Optional[str] = None


@dataclass
class Crawl:
    id: str
    status: CrawlStatus
    startUrls: List[str]
    includeLinks: bool
    maxDepth: int
    maxResults: int
    teamId: str
    createdAt: str
    durationInSeconds: int
    totalPages: int
    useSitemap: bool
    entireWebsite: bool
    excludeNonMainTags: bool
    timeout: int
    useStaticIps: bool
    engineType: EngineType
    completedAt: Optional[str] = None
    projectId: Optional[str] = None
    deduplicateContent: Optional[bool] = None
    extraction: Optional[str] = None


@dataclass
class UrlResult:
    url: str
    isSuccess: bool
    title: str
    markdown: str
    links: List[str]
    duplicatesRemovedCount: Optional[int] = None
    errorCode: Optional[int] = None
    errorMessage: Optional[str] = None


@dataclass
class ScrapeResponse:
    id: str
    teamId: str
    results: List[UrlResult]
    timeout: int
    origin: str
    projectId: str
    createdAt: str
    updatedAt: str


T = TypeVar("T")


@dataclass
class PaginationResult(Generic[T]):
    results: List[T]
    page: int
    limit: int
    totalPages: int
    totalResults: int


def _from_dict(model_cls, data: Dict[str, Any]):
    return model_cls(**data)


