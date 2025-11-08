import httpx
from loguru import logger
from typing import AsyncGenerator
from .base import Provider

class Wayback(Provider):
    """
    Provider for fetching URLs from the Wayback Machine.
    """
    async def fetch(self, domain: str) -> AsyncGenerator[str, None]:
        target_domain = f"*.{domain}" if self.config.get('subdomains') else domain
        page = 0
        filter_params = self.get_filter_params(for_wayback=True)

        while True:
            url = (
                f"https://web.archive.org/cdx/search/cdx?url={target_domain}/*&output=json"
                f"&collapse=urlkey&fl=original&pageSize=5000&page={page}"
            )
            url += filter_params

            try:
                logger.debug(f"Fetching page {page} for {domain} from Wayback...")
                resp = await self.client.get(url, timeout=self.config['timeout'])
                resp.raise_for_status()
                data = resp.json()

                if not data or len(data) <= 1:
                    break

                # The first item is the header, skip it
                for item in data[1:]:
                    yield item[0]

                page += 1

            except (httpx.RequestError, Exception) as e:
                logger.error(f"Error fetching Wayback page {page} for {domain}: {e}")
                break