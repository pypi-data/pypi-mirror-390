# Olyptik Python SDK
The Olyptik Python SDK provides a simple and intuitive interface for web crawling and content extraction. It supports both synchronous and asynchronous programming patterns with full type hints.

## Installation

Install the SDK using pip:

```bash
pip install olyptik
```

## Configuration

First, you'll need to initialize the SDK with your API key - you can get it from the [settings page](https://app.olyptik.io/settings/crawl). You can either pass it directly or use environment variables.

```python
from olyptik import Olyptik

# Initialize with API key
client = Olyptik(api_key="your_api_key_here")
```

## Synchronous Usage

### Start a crawl

<CodeGroup>

Minimal settings crawl:
```python
crawl = client.run_crawl({
    "startUrl": "https://example.com",
    "maxResults": 50
})

print(f"Crawl started with ID: {crawl.id}")
print(f"Status: {crawl.status}")
```

Full example:
```python
# Start a crawl
crawl = client.run_crawl({
    "startUrl": "https://example.com",
    "maxResults": 50,
    "maxDepth": 2,
    "engineType": "auto",
    "includeLinks": True,
    "timeout": 60,
    "useSitemap": False,
    "entireWebsite": False,
    "excludeNonMainTags": True,
    "deduplicateContent": True,
    "extraction": "",
    "useStaticIps": False
})

print(f"Crawl started with ID: {crawl.id}")
print(f"Status: {crawl.status}")
```
</CodeGroup>

### Query crawls

```python
from olyptik import CrawlStatus

result = client.query_crawls({
    "startUrls": ["https://example.com"],
    "status": [CrawlStatus.SUCCEEDED],
    "page": 0,
})

print("Crawls: ", result.results)
print("Page: ", result.page)
print("Total pages: ", result.totalPages)
print("Count of items per page: ", result.limit)
print("Total matched crawls: ", result.totalResults)
```

### Getting Crawl Results
Retrieve the results of your crawl using the crawl ID.
The results are paginated, and you can specify the page number and limit per page.

```python
limit = 50
page = 0
results = client.get_crawl_results(crawl.id, page, limit)
for result in results.results:
    print(f"URL: {result.url}")
    print(f"Title: {result.title}")
    print(f"Depth: {result.depthOfUrl}")
```

### Abort a crawl

```python
aborted_crawl = client.abort_crawl(crawl.id)
print(f"Crawl aborted with ID: {aborted_crawl.id}")
```

### Get crawl logs

Retrieve logs for a specific crawl to monitor its progress and debug issues:

```python
page = 1
limit = 1200
logs = client.get_crawl_logs(crawl.id, page, limit)
for log in logs.results:
    print(f"[{log.level}] {log.message}: {log.description}")
```

### Scrape multiple URLs

Scrape up to 30 URLs at once without following links:

```python
scrape_response = client.scrape({
    "urls": ["https://example.com", "https://example.com/about"],
    "includeLinks": True,
    "excludeNonMainTags": True,
    "deduplicateContent": True,
    "extraction": "",
    "timeout": 5,
    "engineType": "auto",
    "useStaticIps": False
})

for result in scrape_response.results:
    if result.isSuccess:
        print(f"URL: {result.url}")
        print(f"Title: {result.title}")
        print(f"Links found: {len(result.links)}")
    else:
        print(f"Failed to scrape {result.url}: {result.errorMessage}")
```

## Asynchronous Usage

For better performance with I/O operations, use the async client:

### Start a crawl

<CodeGroup>

Minimal settings crawl:
```python
import asyncio
from olyptik import AsyncOlyptik

async def main():
    async with AsyncOlyptik(api_key="your_api_key_here") as client:
        crawl = await client.run_crawl({
            "startUrl": "https://example.com",
            "maxResults": 50
        })

        print(f"Crawl started with ID: {crawl.id}")
        print(f"Status: {crawl.status}")

asyncio.run(main())
```

Full example:
```python
import asyncio
from olyptik import AsyncOlyptik

async def main():
    async with AsyncOlyptik(api_key="your_api_key_here") as client:
        # Start a crawl
        crawl = await client.run_crawl({
            "startUrl": "https://example.com",
            "maxResults": 50,
            "maxDepth": 2,
            "engineType": "auto",
            "includeLinks": True,
            "timeout": 60,
            "useSitemap": False,
            "entireWebsite": False,
            "deduplicateContent": True,
            "excludeNonMainTags": True,
            "extraction": "",
            "useStaticIps": False
        })

        print(f"Crawl started with ID: {crawl.id}")
        print(f"Status: {crawl.status}")

asyncio.run(main())
```

</CodeGroup>

### Query crawls

```python
import asyncio
from olyptik import AsyncOlyptik, CrawlStatus

async def main():
    async with AsyncOlyptik(api_key="your_api_key_here") as client:
        result = await client.query_crawls({
            "startUrls": ["https://example.com"],
            "status": [CrawlStatus.SUCCEEDED],
            "page": 0,
        })
        
        print("Crawls: ", result.results)
        print("Page: ", result.page)
        print("Total pages: ", result.totalPages)
        print("Count of items per page: ", result.limit)
        print("Total matched crawls: ", result.totalResults)

asyncio.run(main())
```

### Get crawl results

```python
import asyncio
from olyptik import AsyncOlyptik

async def main():
    async with AsyncOlyptik(api_key="your_api_key_here") as client:
        # First start a crawl
        crawl = await client.run_crawl({
            "startUrl": "https://example.com",
            "maxResults": 50
        })
        
        # Get crawl results
        limit = 50
        page = 0
        results = await client.get_crawl_results(crawl.id, page, limit)
        for result in results.results:
            print(f"URL: {result.url}")
            print(f"Title: {result.title}")
            print(f"Depth: {result.depthOfUrl}")

asyncio.run(main())
```

### Abort a crawl

```python
import asyncio
from olyptik import AsyncOlyptik

async def main():
    async with AsyncOlyptik(api_key="your_api_key_here") as client:
        # First start a crawl
        crawl = await client.run_crawl({
            "startUrl": "https://example.com",
            "maxResults": 50
        })
        
        # Abort the crawl
        aborted_crawl = await client.abort_crawl(crawl.id)
        print(f"Crawl aborted with ID: {aborted_crawl.id}")

asyncio.run(main())
```

### Get crawl logs

```python
import asyncio
from olyptik import AsyncOlyptik

async def main():
    async with AsyncOlyptik(api_key="your_api_key_here") as client:
        # First start a crawl
        crawl = await client.run_crawl({
            "startUrl": "https://example.com",
            "maxResults": 50
        })
        
        # Get crawl logs
        page = 1
        limit = 1200
        logs = await client.get_crawl_logs(crawl.id, page, limit)
        for log in logs.results:
            print(f"[{log.level}] {log.message}: {log.description}")

asyncio.run(main())
```

### Scrape multiple URLs

```python
import asyncio
from olyptik import AsyncOlyptik

async def main():
    async with AsyncOlyptik(api_key="your_api_key_here") as client:
        scrape_response = await client.scrape({
            "urls": ["https://example.com", "https://example.com/about"],
            "includeLinks": True,
            "excludeNonMainTags": True,
            "deduplicateContent": True,
            "extraction": "",
            "timeout": 5,
            "engineType": "auto",
            "useStaticIps": False
        })
        
        for result in scrape_response.results:
            if result.isSuccess:
                print(f"URL: {result.url}")
                print(f"Title: {result.title}")
                print(f"Links found: {len(result.links)}")
            else:
                print(f"Failed to scrape {result.url}: {result.errorMessage}")

asyncio.run(main())
```

## Configuration Options

### StartCrawlPayload

The crawl configuration options available:

You must provide at least one of the following: maxResults, useSitemap, or entireWebsite.

| Property | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| startUrl | string | ✅ | - | The URL to start crawling from |
| maxResults | number | ❌ | - | Maximum number of results to collect (1-5,000) |
| useSitemap | boolean | ❌ | false | Whether to use sitemap.xml to crawl the website |
| entireWebsite | boolean | ❌ | false | Whether to use sitemap.xml and all found links to crawl the website |
| maxDepth | number | ❌ | 10 | Maximum depth of pages to crawl (1-100) |
| includeLinks | boolean | ❌ | true | Whether to include links in the crawl results' markdown |
| excludeNonMainTags | boolean | ❌ | true | Whether to exclude non-main HTML tags (header, footer, aside, etc.) from the crawl results |
| deduplicateContent | boolean | ❌ | true | Remove duplicate content from markdown that appears on multiple pages |
| extraction | string | ❌ | "" | Instructions defining how the AI should extract specific content from the crawl results |
| timeout | number | ❌ | 60 | Timeout duration in minutes |
| engineType | string | ❌ | "auto" | The engine to use: "auto", "cheerio" (fast, static sites), "playwright" (dynamic sites) |
| useStaticIps | boolean | ❌ | false | Whether to use static IPs for the crawl |

### StartScrapePayload

The scrape configuration options available:

| Property | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| urls | string[] | ✅ | - | Array of URLs to scrape (max 30 URLs) |
| includeLinks | boolean | ❌ | true | Whether to include links in the scrape results' markdown |
| excludeNonMainTags | boolean | ❌ | true | Whether to exclude non-main HTML tags (header, footer, aside, etc.) from the scrape results |
| deduplicateContent | boolean | ❌ | true | Remove duplicate content from markdown that appears in multiple scraped pages |
| extraction | string | ❌ | "" | Instructions defining how the AI should extract specific content from the scrape results |
| timeout | number | ❌ | 5 | Timeout duration in minutes |
| engineType | string | ❌ | "auto" | The engine to use: "auto", "cheerio" (fast, static sites), "playwright" (dynamic sites) |
| useStaticIps | boolean | ❌ | false | Whether to use static IPs for the scrape |

### Engine Types

Choose the appropriate engine for your crawling needs:

```python
from olyptik import EngineType

# Available engine types
EngineType.AUTO        # Automatically choose the best engine
EngineType.PLAYWRIGHT  # Use Playwright for JavaScript-heavy sites
EngineType.CHEERIO     # Use Cheerio for faster, static content crawling
```

### Crawl Status

Monitor your crawl status using the `CrawlStatus` enum:

```python
from olyptik import CrawlStatus

# Possible status values
CrawlStatus.RUNNING    # Crawl is currently running
CrawlStatus.SUCCEEDED  # Crawl completed successfully
CrawlStatus.FAILED     # Crawl failed due to an error
CrawlStatus.TIMED_OUT  # Crawl exceeded timeout limit
CrawlStatus.ABORTED    # Crawl was manually aborted
CrawlStatus.ERROR      # Crawl encountered an error
```

### Crawl Log Level

Monitor log levels using the `CrawlLogLevel` enum:

```python
from olyptik import CrawlLogLevel

# Possible log levels
CrawlLogLevel.INFO     # Informational messages
CrawlLogLevel.DEBUG    # Debug messages
CrawlLogLevel.WARN     # Warning messages
CrawlLogLevel.ERROR    # Error messages
```

## Error Handling

The SDK throws errors for various scenarios. Always wrap your calls in try-catch blocks:

```python
from olyptik import Olyptik, ApiError

client = Olyptik(api_key="your_api_key_here")

try:
    crawl = client.run_crawl({
        "startUrl": "https://example.com",
        "maxResults": 10
    })
except ApiError as e:
    # API returned an error response
    print(f"API Error: {e.message}")
    print(f"Status Code: {e.status_code}")
```

## Data Models

### CrawlResult

Each crawl result contains:

```python
@dataclass
class CrawlResult:
    crawlId: str          # Unique identifier for the crawl
    teamId: str          # Team identifier
    url: str              # The crawled URL
    title: str            # Page title
    markdown: str         # Extracted content in markdown format
    depthOfUrl: int       # How deep this URL was in the crawl
    createdAt: str        # When the result was created
```

### Crawl

Crawl metadata includes:

```python
@dataclass
class Crawl:
    id: str                    # Unique crawl identifier
    status: CrawlStatus        # Current status
    startUrls: List[str]       # Starting URLs
    includeLinks: bool         # Whether links are included
    maxDepth: int              # Maximum crawl depth
    maxResults: int            # Maximum number of results
    teamId: str                # Team identifier
    createdAt: str             # Creation timestamp
    completedAt: Optional[str] # Completion timestamp
    durationInSeconds: int     # Total duration
    totalPages: int       # Number of results found
    useSitemap: bool           # Whether sitemap was used
    entireWebsite: Optional[bool] # Whether to use both sitemap and all found links
    deduplicateContent: bool   # Remove duplicate content from markdown that appears on multiple pages |

    extraction: Optional[str]
    excludeNonMainTags: bool   # Whether non-main HTML tags were excluded
    timeout: int               # Timeout setting
    useStaticIps: bool         # Whether static IPs were used
    engineType: EngineType     # Engine type used
```

### CrawlLog

Each crawl log entry contains:

```python
@dataclass
class CrawlLog:
    id: str                      # Unique log identifier
    message: str                 # Log message
    level: CrawlLogLevel         # Log level (info, debug, warn, error)
    description: str             # Detailed description
    crawlId: str                 # Crawl identifier
    teamId: Optional[str]        # Team identifier
    data: Optional[Dict[str, Any]] # Additional log data
    createdAt: Optional[str]     # Creation timestamp
```

### ScrapeResponse

The response from a scrape operation:

```python
@dataclass
class ScrapeResponse:
    id: str                    # Unique scrape identifier
    teamId: str                # Team identifier
    projectId: str             # Project identifier
    results: List[UrlResult]   # Array of scrape results
    timeout: int               # Timeout in minutes
    origin: str                # Origin of the scrape ("api" or "web")
    createdAt: str             # Creation timestamp
    updatedAt: str             # Last update timestamp
```

### UrlResult

Each URL scrape result contains:

```python
@dataclass
class UrlResult:
    url: str                            # The URL that was scraped
    isSuccess: bool                     # Whether the scrape was successful
    title: str                          # Page title
    markdown: str                       # Extracted content in markdown format
    links: List[str]                    # Links found on the page
    duplicatesRemovedCount: Optional[int]  # Number of duplicate content blocks removed
    errorCode: Optional[int]            # Error code if the scrape failed
    errorMessage: Optional[str]         # Error message if the scrape failed
```
