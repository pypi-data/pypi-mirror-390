import sys
import aiofiles
import json
from pathlib import Path
from urllib.parse import urlparse
from typing import Set, AsyncGenerator


class OutputManager:
    """Handles filtering and writing of discovered URLs."""

    def __init__(self, config: dict):
        self.config = config
        self.output_file = config.get('output_file')

        # Initialize sets for filtering
        self.blacklist: Set[str] = {f".{ext.lower()}" for ext in config.get('blacklist', [])}
        self.seen_urls: Set[str] = set()
        self.seen_paths: Set[str] = set()

    def should_process(self, url: str) -> bool:
        """
        Applies filters and returns True if the URL should be processed/yielded.
        This method handles all de-duplication and filtering logic.
        """
        parsed_url = urlparse(url)
        ext = Path(parsed_url.path).suffix.lower()

        # 1. Check against seen URLs to ensure uniqueness
        if url in self.seen_urls:
            return False

        # 2. Check blacklist
        if ext and ext in self.blacklist:
            return False

        # 3. Handle 'remove parameters' (--fp) logic
        if self.config.get('parameters'):
            path_key = f"{parsed_url.hostname}{parsed_url.path}"
            if path_key in self.seen_paths:
                return False
            self.seen_paths.add(path_key)

        # If all checks pass, add to seen set and return True
        self.seen_urls.add(url)
        return True

    async def write_results(self, urls_generator: AsyncGenerator[str, None]):
        """
        Consumes an async generator of URLs and writes them to the configured output.
        """
        writer = None
        if self.output_file:
            writer = await aiofiles.open(self.output_file, 'a')

        try:
            async for url in urls_generator:
                output_line = f'{{"url":"{url}"}}' if self.config.get('json') else url
                if writer:
                    await writer.write(output_line + '\n')
                else:
                    sys.stdout.write(output_line + '\n')
        finally:
            if writer:
                await writer.close()