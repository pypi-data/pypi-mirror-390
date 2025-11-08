import asyncio
from typing import List, Dict, Any, AsyncGenerator

# Make the version accessible from your package
__version__ = "2.3.0"

# Import the core components needed for the public API
from .runner import Runner
from .output import OutputManager


async def get_urls(domains: List[str], config: Dict[str, Any] | None = None) -> AsyncGenerator[str, None]:
    """
    Public API function to fetch URLs for a list of domains. This is an
    asynchronous generator.

    Args:
        domains: A list of domain strings to scan.
        config: A dictionary to configure the scan. If None, defaults will be used.

    Yields:
        A string for each unique URL found that passes all filters.

    Example:
        async for url in get_urls(["example.com"]):
            print(url)
    """
    # Use a sensible default configuration if none is provided
    if config is None:
        config = {
            'threads': 10, 'timeout': 20, 'retries': 5,
            'subdomains': False, 'parameters': False,
            'providers': ["wayback", "commoncrawl", "otx", "urlscan"],
            'blacklist': ["ttf", "woff", "svg", "png", "jpg", "gif"],
            'filters': {}, 'urlscan': {}
        }

    # The output manager is used here only for its filtering capabilities
    output_filter = OutputManager(config)
    runner = Runner(domains=domains, config=config)

    # This is the core logic that runs providers and yields results
    async for url in runner.stream():  # We will add a 'stream' method to the Runner
        if output_filter.should_process(url):
            yield url