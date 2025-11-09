from abc import ABC, abstractmethod
from typing import Any, Dict


class Spider(ABC):
    """
    Abstract base class for spiders.
    Defines a contract for fetching and enriching a web page.
    """

    @abstractmethod
    async def fetch(self, url: str) -> Dict[str, Any]:
        """
        Fetch a URL, process it (deterministic extraction + LLM enrichment),
        and return a structured dict or PageResult.
        """
        pass
