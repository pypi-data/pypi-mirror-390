import asyncio
import httpx
from loguru import logger
from typing import List, Dict, AsyncGenerator

# Import provider classes
from .providers import wayback, commoncrawl, otx, urlscan


class Runner:
    """
    The core runner that manages providers and streams results.
    """

    def __init__(self, domains: List[str], config: Dict):
        self.domains = domains
        self.config = config

        provider_map = {
            "wayback": wayback.Wayback,
            "commoncrawl": commoncrawl.CommonCrawl,
            "otx": otx.OTX,
            "urlscan": urlscan.URLScan,
        }

        self.providers = []
        for p_name in config.get('providers', []):
            if p_name in provider_map:
                self.providers.append(provider_map[p_name])
            else:
                logger.warning(f"Unknown provider '{p_name}' skipped.")

    async def stream(self) -> AsyncGenerator[str, None]:
        """
        Asynchronous generator that yields URLs as they are found.
        This is the primary method for library usage.
        """
        if not self.providers:
            logger.error("No valid providers configured.")
            return

        results_queue = asyncio.Queue()

        # Configure a resilient HTTP transport with retries
        transport = httpx.AsyncHTTPTransport(retries=self.config.get('retries', 5))
        http_limits = httpx.Limits(
            max_connections=self.config['threads'],
            max_keepalive_connections=self.config['threads']
        )

        # The entire logic must be within the client's context manager
        async with httpx.AsyncClient(transport=transport, limits=http_limits, follow_redirects=True) as client:

            # This is the "Producer" part of the pattern.
            # It creates all worker tasks and waits for them to finish.
            async def producer():
                # Define the worker coroutine inside the producer
                async def stream_worker(domain: str, provider_cls):
                    provider = provider_cls(client, self.config)
                    logger.info(f"Fetching URLs for {domain} from {provider.name}...")
                    try:
                        async for url in provider.fetch(domain):
                            await results_queue.put(url)
                    except Exception as e:
                        logger.error(f"Error in {provider.name} for {domain}: {e}")

                # Create and gather all the worker tasks
                worker_tasks = []
                provider_delay = self.config.get('provider_delay', 1.0)  # Default to 1 second

                for domain in self.domains:
                    for provider_cls in self.providers:
                        # Create the task but don't await it yet
                        task = stream_worker(domain, provider_cls)
                        worker_tasks.append(task)
                        # Pause briefly before starting the next provider's task
                        await asyncio.sleep(provider_delay)

                await asyncio.gather(*worker_tasks)
                # After all workers are done, signal the consumer to stop
                await results_queue.put(None)

            # Start the producer in the background
            producer_task = asyncio.create_task(producer())

            # This is the "Consumer" part of the pattern.
            # It yields results from the queue until it sees the "None" signal.
            while True:
                url = await results_queue.get()
                if url is None:
                    break
                yield url

            # Await the producer to ensure it finished cleanly (important for error handling)
            await producer_task