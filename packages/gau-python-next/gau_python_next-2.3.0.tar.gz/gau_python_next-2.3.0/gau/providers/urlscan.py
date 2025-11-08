import httpx
from loguru import logger
from typing import AsyncGenerator
from .base import Provider


class URLScan(Provider):
    """
    Provider for fetching URLs from URLScan.io.
    """

    async def fetch(self, domain: str) -> AsyncGenerator[str, None]:
        search_after = None
        urlscan_config = self.config.get('urlscan', {})
        api_key = urlscan_config.get('apikey')
        host = urlscan_config.get('host', 'https://urlscan.io/')

        headers = {}
        if api_key:
            headers['API-Key'] = api_key

        while True:
            url = f"{host}api/v1/search/?q=domain:{domain}&size=100"
            if search_after:
                url += f"&search_after={search_after}"

            try:
                logger.debug(f"Fetching results for {domain} from URLScan...")
                resp = await self.client.get(url, headers=headers, timeout=self.config['timeout'])

                if resp.status_code == 429:
                    logger.warning(f"URLScan rate limit hit. Stopping scan for {domain}.")
                    break

                resp.raise_for_status()
                data = resp.json()

                results = data.get('results', [])
                for res in results:
                    if 'page' in res and 'url' in res['page']:
                        yield res['page']['url']

                if data.get('has_more') and results:
                    # The `sort` property of the last result is used for pagination
                    search_after = ','.join(map(str, results[-1].get('sort', [])))
                else:
                    break

            except (httpx.RequestError, Exception) as e:
                logger.error(f"Error fetching URLScan for {domain}: {e}")
                break