from abc import ABC, abstractmethod
from typing import Tuple


class BrowserClient(ABC):
    """
    Abstract base for a browser client.
    """

    @abstractmethod
    async def render(self, url: str) -> Tuple[str, str, int]:
        """
        Render a page and return:
          - html (str)
          - visible_text (str)
          - status_code (int)
        """
        pass
