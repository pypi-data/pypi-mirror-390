from dataclasses import dataclass
from typing import List, Optional


@dataclass
class LinkMetadata:
    href: str
    text: Optional[str]
    rel: List[str]
    detected_from: List[str]
    llm_score: float = 0.0
    llm_tags: Optional[List[str]] = None
    reasons: Optional[List[str]] = None
