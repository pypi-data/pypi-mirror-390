from abc import ABC, abstractmethod
from typing import Any, Dict


class LLMClient(ABC):
    """
    Abstract base class for LLM interactions.
    """

    @abstractmethod
    async def complete_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        Send a request that expects a structured JSON response.
        """
        pass
