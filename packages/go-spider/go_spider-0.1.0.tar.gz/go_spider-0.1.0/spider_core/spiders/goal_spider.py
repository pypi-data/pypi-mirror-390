import asyncio
import logging
from typing import Set, List, Dict, Optional
from datetime import datetime
from spider_core.spiders.basic_spider import BasicSpider
from spider_core.base.page_result import PageResult
from spider_core.base.link_metadata import LinkMetadata

logger = logging.getLogger("goal_spider")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[GoalSpider] %(message)s"))
    logger.addHandler(ch)


class GoalSpider(BasicSpider):
    """
    GoalSpider recursively crawls pages until the given goal is achieved.
    Example goal: 'Find contact email'
    """

    def __init__(self, browser_client, relevance_ranker, chunker, llm_client, max_depth: int = 3):
        super().__init__(browser_client, relevance_ranker, chunker)
        self.llm_client = llm_client
        self.max_depth = max_depth
        self.visited: Set[str] = set()
        self.goal_result: Optional[str] = None
        self.confidence: float = 0.0

    async def _check_goal(self, page: PageResult, goal: str) -> Dict:
        """Ask the LLM if the goal is satisfied on this page."""
        system_prompt = (
            "You are a goal evaluator for a web crawler. "
            "Given a user goal and a web page's text content, "
            "determine if the goal has been achieved. "
            "Return JSON with keys: {'found': bool, 'confidence': float, 'answer': str}."
        )
        user_prompt = f"GOAL: {goal}\n\nPAGE TEXT:\n{page.page_chunks[0]['text'][:4000] if page.page_chunks else ''}"
        try:
            response = await self.llm_client.complete_json(system_prompt, user_prompt)
            return response
        except Exception as e:
            logger.warning(f"Goal check failed: {e}")
            return {"found": False, "confidence": 0.0, "answer": ""}

    async def crawl_until_goal(self, start_url: str, goal: str, depth: int = 0) -> Optional[PageResult]:
        """Recursive crawler that continues until goal found or depth exhausted."""
        if depth > self.max_depth:
            return None
        if start_url in self.visited:
            return None
        self.visited.add(start_url)

        logger.info(f"[Depth {depth}] Crawling: {start_url}")
        page = await self.fetch(start_url)
        goal_check = await self._check_goal(page, goal)

        if goal_check.get("found") and goal_check.get("confidence", 0) > 0.7:
            logger.info(f"✅ Goal achieved at {start_url} (confidence={goal_check['confidence']})")
            self.goal_result = goal_check.get("answer")
            self.confidence = goal_check.get("confidence", 1.0)
            return page

        # Recurse into high-ranking links
        sorted_links = sorted(page.links, key=lambda l: getattr(l, "llm_score", 0.0), reverse=True)
        for link in sorted_links[:5]:  # limit fan-out
            if link.href not in self.visited:
                result = await self.crawl_until_goal(link.href, goal, depth + 1)
                if result is not None:
                    return result
        return None

    async def run_goal(self, start_url: str, goal: str) -> Dict:
        """Entrypoint for CLI or programmatic use."""
        page = await self.crawl_until_goal(start_url, goal)
        return {
            "goal": goal,
            "found": self.goal_result is not None,
            "confidence": self.confidence,
            "answer": self.goal_result,
            "visited_pages": len(self.visited),
        }
