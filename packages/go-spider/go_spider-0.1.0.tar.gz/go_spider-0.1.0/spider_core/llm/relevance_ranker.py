import asyncio
from typing import List, Dict
from spider_core.base.link_metadata import LinkMetadata
from spider_core.llm.openai_gpt_client import OpenAIGPTClient


class RelevanceRanker:
    """
    Uses an LLM to evaluate the relevance of each link based on page chunks.
    """

    def __init__(self, llm_client: OpenAIGPTClient, max_reason_count: int = 3):
        self.llm_client = llm_client
        self.max_reason_count = max_reason_count

    async def score_links(self, links: List[LinkMetadata], chunks: List[Dict]) -> List[LinkMetadata]:
        """
        Scores links using chunk-based evaluation with GPT.
        """

        # Initialize aggregation structure
        scores = {link.href: {"sum": 0.0, "count": 0, "tags": set(), "reasons": []} for link in links}

        for chunk in chunks:
            system_prompt = (
                "You are an AI that evaluates the relevance of web links based on page content. "
                "Given a page text chunk and a set of candidate links (with href and anchor text), "
                "score each link from 0.0 to 1.0 based on how likely it is to be important or useful. "
                "Output JSON ONLY in this form: "
                '{"results":[{"href":"...", "score":0.0, "tags":["..."], "reason":"..."}]}'
            )

            candidate_minimal = [{"href": l.href, "text": l.text or ""} for l in links]

            user_prompt = (
                f"PAGE CHUNK:\n{chunk['text']}\n\n"
                f"LINK CANDIDATES:\n{candidate_minimal}\n\n"
                "Respond with relevance scores."
            )

            result = await self.llm_client.complete_json(system_prompt, user_prompt)

            if "results" in result and isinstance(result["results"], list):
                for item in result["results"]:
                    href = item.get("href")
                    if href in scores:
                        score = float(item.get("score", 0))
                        tags = item.get("tags", [])
                        reason = item.get("reason", "")

                        scores[href]["sum"] += score
                        scores[href]["count"] += 1
                        scores[href]["tags"].update(tags)
                        if reason:
                            scores[href]["reasons"].append(reason)

        # Apply aggregated scores to the LinkMetadata objects
        for link in links:
            data = scores[link.href]
            if data["count"] > 0:
                link.llm_score = round(data["sum"] / data["count"], 3)
                link.llm_tags = list(data["tags"])
                link.reasons = data["reasons"][: self.max_reason_count]

        return links
