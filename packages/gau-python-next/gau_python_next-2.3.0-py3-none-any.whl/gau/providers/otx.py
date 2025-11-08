import httpx
from loguru import logger
from typing import AsyncGenerator
from urllib.parse import urlparse
from .base import Provider


def get_domain_and_category(domain: str, include_subdomains: bool):
    """Determine the OTX category based on domain structure."""
    parsed = urlparse(f"http://{domain}")
    parts = parsed.netloc.split('.')

    is_subdomain = len(parts) > 2

    if is_subdomain and include_subdomains:
        base_domain = '.'.join(parts[-2:])
        return base_domain, "domain"

    category = "hostname" if is_subdomain else "domain"
    return domain, category


class OTX(Provider):
    """
    Provider for fetching URLs from AlienVault's OTX.
    """

    async def fetch(self, domain: str) -> AsyncGenerator[str, None]:
        page = 1
        base_url = "https://otx.alienvault.com/"
        target_domain, category = get_domain_and_category(domain, self.config.get('subdomains'))

        while True:
            url = f"{base_url}api/v1/indicators/{category}/{target_domain}/url_list?limit=100&page={page}"

            try:
                logger.debug(f"Fetching page {page} for {domain} from OTX...")
                resp = await self.client.get(url, timeout=self.config['timeout'])
                resp.raise_for_status()
                data = resp.json()

                for entry in data.get('url_list', []):
                    if 'url' in entry:
                        yield entry['url']

                if not data.get('has_next', False):
                    break
                page += 1
            except (httpx.RequestError, Exception) as e:
                logger.error(f"Error fetching OTX page {page} for {domain}: {e}")
                break