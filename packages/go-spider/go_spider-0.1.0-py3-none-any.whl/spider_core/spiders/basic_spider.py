import asyncio
import logging
from datetime import datetime
from typing import List

from spider_core.base.page_result import PageResult
from spider_core.browser.browser_client import BrowserClient
from spider_core.extractors.deterministic_extractor import DeterministicLinkExtractor
from spider_core.core_utils.chunking import TextChunker
from spider_core.llm.relevance_ranker import RelevanceRanker
from spider_core.base.link_metadata import LinkMetadata

logger = logging.getLogger("basic_spider")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[BasicSpider] %(levelname)s %(message)s"))
    logger.addHandler(ch)


async def maybe_await(result):
    if asyncio.iscoroutine(result):
        return await result
    return result


class BasicSpider:
    """
    BasicSpider: orchestrates render -> extract -> chunk -> score (LLM)
    - split into two main building blocks:
        * _fetch_without_llm: render, extract, chunk, build PageResult (no LLM calls)
        * _score_links_with_llm: calls the ranker to score/update links (LLM calls)
    This split allows StealthSpider to call _fetch_without_llm while the
    machine is routed through VPN, then disconnect before _score_links_with_llm.
    """

    def __init__(
        self,
        browser_client: BrowserClient,
        relevance_ranker: RelevanceRanker,
        chunker: TextChunker,
    ):
        self.browser_client = browser_client
        self.relevance_ranker = relevance_ranker
        self.chunker = chunker

    async def fetch(self, url: str) -> PageResult:
        """
        Full pipeline: render -> extract/chunk -> (LLM scoring) -> return PageResult
        """
        logger.info(f"Starting fetch pipeline for: {url}")
        # 1) render + extract + chunk (without calling LLM)
        page_result = await self._fetch_without_llm(url)

        # 2) if we have chunks and a ranker, run scoring (LLM)
        if page_result.page_chunks and self.relevance_ranker:
            try:
                await self._score_links_with_llm(page_result)
            except Exception as e:
                logger.warning(f"LLM scoring failed: {e}")

        # 3) finalize canonical if missing
        if not page_result.canonical:
            canonical = next((l.href for l in page_result.links if "canonical" in (l.rel or [])), page_result.url)
            page_result.canonical = canonical

        logger.info(f"Finished fetch pipeline for: {url} (links={len(page_result.links)})")
        return page_result

    async def _fetch_without_llm(self, url: str) -> PageResult:
        """
        Render the page, extract deterministic links, chunk visible text, and
        return a PageResult WITHOUT doing any LLM calls.
        """
        logger.info(f"Rendering URL: {url}")
        html, visible_text, status = await self.browser_client.render(url)

        logger.debug(f"Render complete (status={status}), extracting links")
        # Deterministic extractor is implemented as a function/classmethod that expects html + base_url
        try:
            links: List[LinkMetadata] = DeterministicLinkExtractor.extract(html, url)
        except TypeError:
            # fallbacks for other extractor signatures
            try:
                links = DeterministicLinkExtractor().extract(html, url)
            except Exception as e:
                logger.warning(f"Deterministic extractor failed: {e}; falling back to empty link list")
                links = []

        logger.debug(f"Extracted {len(links)} links")

        # Chunk the visible text. Accept multiple method names for compatibility.
        logger.debug("Chunking visible text")
        chunks = None
        try:
            chunks = self.chunker.chunk_text(visible_text)
        except Exception:
            try:
                chunks = list(self.chunker.chunk(visible_text))
            except Exception:
                try:
                    chunks = self.chunker.chunking(visible_text)
                except Exception as e:
                    logger.warning(f"Chunker failed: {e}; using single-chunk fallback")
                    chunks = [{"chunk_id": 0, "text": visible_text or "", "token_count": len((visible_text or "").split())}]

        logger.debug(f"Produced {len(chunks)} chunks")

        # Build PageResult
        page_result = PageResult(
            url=url,
            fetched_at=datetime.utcnow(),
            status=status,
            canonical=None,
            links=links,
            llm_summary=None,
            page_chunks=chunks,
        )
        return page_result

    async def _score_links_with_llm(self, page_result: PageResult):
        """
        Use the relevance_ranker to score links and optionally produce summaries.
        This method assumes the environment's network identity is the one the LLM
        should see (i.e., called after VPN is disconnected in StealthSpider).
        """
        logger.info("Scoring links with LLM...")
        rr = self.relevance_ranker

        # prefer common method names
        method = None
        for name in ("score_links", "rank_links", "rank", "score"):
            if hasattr(rr, name):
                method = getattr(rr, name)
                break

        if method is None:
            logger.warning("No scoring method found on relevance_ranker; skipping LLM scoring.")
            return

        # Call the ranker with (links, chunks) if possible
        try:
            res = method(page_result.links, page_result.page_chunks)
            await maybe_await(res)
            logger.debug("LLM scoring completed and may have mutated page_result.links in-place.")
        except TypeError:
            # fallback: maybe the ranker expects a different signature (links only)
            try:
                res = method(page_result.links)
                await maybe_await(res)
                logger.debug("LLM scoring completed with fallback signature.")
            except Exception as e:
                logger.warning(f"LLM scoring failed with fallback attempt: {e}")
        except Exception as e:
            logger.warning(f"LLM scoring raised an unexpected error: {e}")

    def summarize_result(self, page_result):
        """
        Produce a concise human-readable summary of a PageResult.
        Includes status, canonical, link count, and top LLM-scored links.
        """
        summary_lines = []
        summary_lines.append(f"URL: {page_result.url}")
        summary_lines.append(f"Status: {page_result.status}")
        summary_lines.append(f"Canonical: {page_result.canonical or 'N/A'}")

        links = getattr(page_result, "links", [])
        chunks = getattr(page_result, "page_chunks", [])
        summary_lines.append(f"Links found: {len(links)}")
        summary_lines.append(f"Text chunks: {len(chunks)}")

        # Optional: summarize top 3 links by LLM score
        if links:
            top_links = sorted(links, key=lambda l: getattr(l, "llm_score", 0.0), reverse=True)[:3]
            summary_lines.append("Top links by LLM score:")
            for l in top_links:
                summary_lines.append(f"  - {l.href} ({l.llm_score:.2f}) {l.text or ''}".strip())

        # Optional summary snippet of first text chunk
        if chunks:
            first_text = chunks[0].get("text", "")[:180].replace("\n", " ")
            summary_lines.append(f"Sample text chunk: {first_text}...")

        return "\n".join(summary_lines)

