import httpx
from loguru import logger
from typing import AsyncGenerator, List, Dict, Any
from .base import Provider


class CommonCrawl(Provider):
    """
    Provider for fetching URLs from Common Crawl.
    """

    async def get_latest_index(self) -> str | None:
        """Fetches the API URL for the latest Common Crawl index."""
        try:
            resp = await self.client.get("http://index.commoncrawl.org/collinfo.json")
            resp.raise_for_status()
            indices: List[Dict[str, Any]] = resp.json()
            if indices:
                return indices[0].get("cdx-api")
        except (httpx.RequestError, Exception) as e:
            logger.error(f"Failed to get CommonCrawl index: {e}")
        return None

    async def fetch(self, domain: str) -> AsyncGenerator[str, None]:
        api_url = await self.get_latest_index()
        if not api_url:
            return

        target_domain = f"*.{domain}" if self.config.get('subdomains') else domain
        filter_params = self.get_filter_params(for_wayback=False)

        # First get number of pages
        try:
            pagination_url = f"{api_url}?url={target_domain}/*&output=json&showNumPages=true"
            resp = await self.client.get(pagination_url, timeout=self.config['timeout'])
            pages_data = resp.json()
            num_pages = pages_data.get('pages', 0)
        except Exception as e:
            logger.error(f"Could not get page count for {domain} from CommonCrawl: {e}")
            return

        for page in range(num_pages):
            url = (
                f"{api_url}?url={target_domain}/*&output=json&fl=url"
                f"&page={page}"
            )
            url += filter_params

            try:
                logger.debug(f"Fetching page {page}/{num_pages - 1} for {domain} from CommonCrawl...")
                resp = await self.client.get(url, timeout=self.config['timeout'])
                resp.raise_for_status()

                # CommonCrawl returns JSON objects separated by newlines
                for line in resp.text.strip().split('\n'):
                    try:
                        data = httpx.json.loads(line)
                        if 'url' in data:
                            yield data['url']
                    except Exception:
                        continue  # Ignore malformed JSON lines
            except (httpx.RequestError, Exception) as e:
                logger.error(f"Error fetching CommonCrawl page {page} for {domain}: {e}")
                break