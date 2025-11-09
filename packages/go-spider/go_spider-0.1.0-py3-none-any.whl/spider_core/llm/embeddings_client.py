# llm/embeddings_client.py
from abc import ABC, abstractmethod
from typing import List
import os
import numpy as np
import openai

class EmbeddingsClient(ABC):
    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        ...

class OpenAIEmbeddings(EmbeddingsClient):
    def __init__(self, model: str = "text-embedding-3-small", api_key: str | None = None):
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set for embeddings.")
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    def embed(self, texts: List[str]) -> List[List[float]]:
        resp = self.client.embeddings.create(model=self.model, input=texts)
        return [d.embedding for d in resp.data]

def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    na = np.linalg.norm(a); nb = np.linalg.norm(b)
    if na == 0 or nb == 0: return 0.0
    return float(a @ b / (na * nb))
