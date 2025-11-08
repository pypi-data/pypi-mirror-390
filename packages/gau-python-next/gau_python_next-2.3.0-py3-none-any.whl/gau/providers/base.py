import abc
import httpx
from typing import AsyncGenerator, Set

class Provider(abc.ABC):
    """Abstract base class for all providers."""

    def __init__(self, client: httpx.AsyncClient, config: dict):
        self.client = client
        self.config = config

    @abc.abstractmethod
    async def fetch(self, domain: str) -> AsyncGenerator[str, None]:
        """
        Fetches URLs for a given domain and yields them.
        Must be implemented by subclasses.
        """
        yield

    @property
    def name(self) -> str:
        """Returns the name of the provider."""
        return self.__class__.__name__.lower()

    def get_filter_params(self, for_wayback: bool) -> str:
        """Constructs filter query parameters from the config."""
        filters = self.config.get('filters', {})
        params = []

        if filters.get('from'):
            params.append(f"from={filters['from']}")
        if filters.get('to'):
            params.append(f"to={filters['to']}")

        param_map = {
            'matchmimetypes': 'mimetype' if for_wayback else 'mime',
            'matchstatuscodes': 'statuscode' if for_wayback else 'status',
            'filtermimetypes': '!mimetype' if for_wayback else '!=mime',
            'filterstatuscodes': '!statuscode' if for_wayback else '!=status',
        }

        for config_key, param_name in param_map.items():
            for value in filters.get(config_key, []):
                params.append(f"filter={param_name}:{value}")

        return f"&{'&'.join(params)}" if params else ""