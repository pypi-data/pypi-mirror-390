from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
from spider_core.base.link_metadata import LinkMetadata


@dataclass
class PageResult:
    url: str
    fetched_at: datetime
    status: int
    canonical: str
    links: List[LinkMetadata]
    llm_summary: Optional[str]
    page_chunks: List[Dict]
