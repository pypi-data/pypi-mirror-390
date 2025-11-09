# Project Compilation: spider_core

## 🧾 Summary

| Metric | Value |
|:--|:--|
| Root Directory | `/home/gompert/data/workspace/spider_core` |
| Total Directories | 10 |
| Total Indexed Files | 37 |
| Skipped Files | 0 |
| Indexed Size | 58.12 KB |
| Max File Size Limit | 2 MB |

## 📚 Table of Contents

- [__init__.py](#init-py)
- [base/__init__.py](#base-init-py)
- [base/link_metadata.py](#base-link-metadata-py)
- [base/page_result.py](#base-page-result-py)
- [base/spider.py](#base-spider-py)
- [browser/__init__.py](#browser-init-py)
- [browser/browser_client.py](#browser-browser-client-py)
- [browser/playwright_client.py](#browser-playwright-client-py)
- [cli_spider.py](#cli-spider-py)
- [core_utils/__init__.py](#core-utils-init-py)
- [core_utils/chunking.py](#core-utils-chunking-py)
- [core_utils/url_utils.py](#core-utils-url-utils-py)
- [extractors/__init__.py](#extractors-init-py)
- [extractors/deterministic_extractor.py](#extractors-deterministic-extractor-py)
- [goal/__init__.py](#goal-init-py)
- [goal/goal_planner.py](#goal-goal-planner-py)
- [llm/__init__.py](#llm-init-py)
- [llm/embeddings_client.py](#llm-embeddings-client-py)
- [llm/llm_client.py](#llm-llm-client-py)
- [llm/openai_gpt_client.py](#llm-openai-gpt-client-py)
- [llm/relevance_ranker.py](#llm-relevance-ranker-py)
- [requirements.txt](#requirements-txt)
- [spiders/__init__.py](#spiders-init-py)
- [spiders/basic_spider.py](#spiders-basic-spider-py)
- [spiders/goal_spider.py](#spiders-goal-spider-py)
- [spiders/stealth/__init__.py](#spiders-stealth-init-py)
- [spiders/stealth/stealth_config.py](#spiders-stealth-stealth-config-py)
- [spiders/stealth/stealth_spider.py](#spiders-stealth-stealth-spider-py)
- [spiders/stealth/vpn_manager.py](#spiders-stealth-vpn-manager-py)
- [storage/__init__.py](#storage-init-py)
- [storage/db.py](#storage-db-py)
- [test/test.py](#test-test-py)
- [test/test2.py](#test-test2-py)
- [test/test3.py](#test-test3-py)
- [test/test4.py](#test-test4-py)
- [test/test_ranker.py](#test-test-ranker-py)
- [test/test_spider.py](#test-test-spider-py)

## 📂 Project Structure

```
📁 base/
    📄 __init__.py
    📄 link_metadata.py
    📄 page_result.py
    📄 spider.py
📁 browser/
    📄 __init__.py
    📄 browser_client.py
    📄 playwright_client.py
📁 core_utils/
    📄 __init__.py
    📄 chunking.py
    📄 url_utils.py
📁 extractors/
    📄 __init__.py
    📄 deterministic_extractor.py
📁 goal/
    📄 __init__.py
    📄 goal_planner.py
📁 llm/
    📄 __init__.py
    📄 embeddings_client.py
    📄 llm_client.py
    📄 openai_gpt_client.py
    📄 relevance_ranker.py
📁 spiders/
    📁 stealth/
        📄 __init__.py
        📄 stealth_config.py
        📄 stealth_spider.py
        📄 vpn_manager.py
    📄 __init__.py
    📄 basic_spider.py
    📄 goal_spider.py
📁 storage/
    📄 __init__.py
    📄 db.py
📁 test/
    📄 test.py
    📄 test2.py
    📄 test3.py
    📄 test4.py
    📄 test_ranker.py
    📄 test_spider.py
📄 __init__.py
📄 cli_spider.py
📄 requirements.txt
```

## `__init__.py`

```python
"""
Spider implementations: basic, stealth, and goal-oriented variants.
"""
from spider_core.spiders.basic_spider import BasicSpider
from spider_core.spiders.stealth.stealth_spider import StealthSpider
try:
    from spider_core.spiders.goal_spider import GoalOrientedSpider
except ImportError:
    GoalOrientedSpider = None

__all__ = ["BasicSpider", "StealthSpider", "GoalOrientedSpider"]

```

## `base/__init__.py`

```python

```

## `base/link_metadata.py`

```python
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

```

## `base/page_result.py`

```python
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

```

## `base/spider.py`

```python
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

```

## `browser/__init__.py`

```python

```

## `browser/browser_client.py`

```python
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

```

## `browser/playwright_client.py`

```python
import asyncio
from typing import Tuple
from playwright.async_api import async_playwright, Browser, Page
from spider_core.browser.browser_client import BrowserClient


class PlaywrightBrowserClient(BrowserClient):
    """
    A Playwright-based implementation of BrowserClient.
    Launches Chromium and renders pages asynchronously.
    """

    def __init__(self, headless: bool = True, viewport: Tuple[int, int] = (1200, 900)):
        self.headless = headless
        self.viewport = viewport
        self.browser: Browser | None = None

    async def _ensure_browser(self):
        """Launches the browser if it's not already running."""
        if self.browser is None:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=self.headless)

    async def render(self, url: str) -> Tuple[str, str, int]:
        """
        Render a page and return:
          - html (str)
          - visible_text (str)
          - status_code (int)
        """
        await self._ensure_browser()
        page: Page = await self.browser.new_page(viewport={"width": self.viewport[0], "height": self.viewport[1]})

        response = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        status_code = response.status if response else 0

        # Optional scroll to trigger lazy-loaders
        try:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2);")
            await asyncio.sleep(0.5)
        except Exception:
            pass

        html = await page.content()

        # Visible text (scripts/styles removed by Playwright's innerText handling)
        visible_text = await page.evaluate("""
            () => {
                const clone = document.body.cloneNode(true);
                clone.querySelectorAll('script, style, noscript').forEach(el => el.remove());
                return clone.innerText;
            }
        """)

        await page.close()
        return html, visible_text, status_code

    async def close(self):
        """Close the browser when done."""
        if self.browser is not None:
            await self.browser.close()
            self.browser = None

```

## `cli_spider.py`

```python
import argparse
import asyncio
import json
from pathlib import Path

from spider_core.browser.playwright_client import PlaywrightBrowserClient
from spider_core.core_utils.chunking import TextChunker
from spider_core.llm.openai_gpt_client import OpenAIGPTClient
from spider_core.llm.relevance_ranker import RelevanceRanker
from spider_core.spiders.basic_spider import BasicSpider

# ---------------------------------------------------------------------
# Optional stealth mode imports
# ---------------------------------------------------------------------
try:
    from spider_core.spiders.stealth.stealth_spider import StealthSpider
    from spider_core.spiders.stealth.stealth_config import (
        DEFAULT_REGION,
        DEFAULT_VPN_PROVIDER,
        REQUIRE_VPN_DEFAULT,
    )
    STEALTH_AVAILABLE = True
except ImportError:
    STEALTH_AVAILABLE = False

# ---------------------------------------------------------------------
# Optional goal-oriented imports
# ---------------------------------------------------------------------
try:
    from spider_core.spiders.goal_spider import GoalOrientedSpider
    from spider_core.goal.goal_planner import GoalPlanner
    from spider_core.storage.db import DB
    GOAL_AVAILABLE = True
except ImportError:
    GOAL_AVAILABLE = False


# ---------------------------------------------------------------------
# Helper: run a simple single-page spider (basic/stealth)
# ---------------------------------------------------------------------
async def run_basic_spider(spider, url, output_path, pretty):
    print(f"🔍 Fetching: {url} using {spider.__class__.__name__} ...")
    result = await spider.fetch(url)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("a") as f:
        json.dump(
            result.__dict__,
            f,
            default=lambda o: o.__dict__ if hasattr(o, "__dict__") else str(o),
            indent=4 if pretty else None,
        )
        f.write("\n")

    print("\n--- Summary ---")
    print(spider.summarize_result(result))
    print("----------------")
    print(f"✅ Saved result to {output_path}")


# ---------------------------------------------------------------------
# CLI Entrypoint
# ---------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="LLM-powered recursive web spider CLI")

    # Base arguments
    parser.add_argument("url", help="Seed URL to crawl or fetch")
    parser.add_argument("--output", default="output.jsonl", help="JSONL output path for basic mode")
    parser.add_argument("--pretty", action="store_true", help="Pretty print JSON output")
    parser.add_argument("--max-tokens", type=int, default=1200, help="Max tokens per chunk")
    parser.add_argument("--no-headless", action="store_true", help="Run Playwright in visible (non-headless) mode")

    # Stealth mode arguments
    parser.add_argument("--stealth", action="store_true", help="Use StealthSpider with VPN enforcement")
    parser.add_argument("--vpn", type=str, default=None, help="VPN provider (default: nordvpn)")
    parser.add_argument("--region", type=str, default=None, help="VPN region (e.g. hong_kong)")
    parser.add_argument("--no-require-vpn", action="store_true", help="Do not fail if VPN not connected")

    # Goal-oriented mode arguments
    parser.add_argument("--goal", type=str, default=None, help="Goal or question to recursively answer")
    parser.add_argument("--db", type=str, default="spider_core.db", help="SQLite DB path for crawl data (goal mode)")
    parser.add_argument("--max-pages", type=int, default=25, help="Max pages to crawl in goal mode")
    parser.add_argument("--confidence", type=float, default=0.85, help="Confidence threshold to stop goal mode")
    parser.add_argument("--max-depth", type=int, default=3, help="Maximum recursion depth for goal mode")

    args = parser.parse_args()

    async def async_main():
        # -----------------------------------------------------------------
        # Shared components
        # -----------------------------------------------------------------
        browser = PlaywrightBrowserClient(headless=not args.no_headless)
        llm = OpenAIGPTClient()
        ranker = RelevanceRanker(llm)
        chunker = TextChunker(max_tokens=args.max_tokens)

        # -----------------------------------------------------------------
        # GOAL-ORIENTED MODE
        # -----------------------------------------------------------------
        if args.goal:
            if not GOAL_AVAILABLE:
                raise RuntimeError("Goal modules not found. Ensure goal_spider.py, goal_planner.py, and storage/db.py exist.")

            print(f"[CLI] 🚀 Running Goal-Oriented Spider for goal: '{args.goal}'")
            db = DB(args.db)
            planner = GoalPlanner(llm)

            # Choose base spider (stealth or normal)
            if args.stealth:
                if not STEALTH_AVAILABLE:
                    raise RuntimeError("StealthSpider not available. Install stealth module.")
                vpn_provider = args.vpn or DEFAULT_VPN_PROVIDER
                region = args.region or DEFAULT_REGION
                require_vpn = not args.no_require_vpn
                print(f"[CLI] Using StealthSpider VPN={vpn_provider}, region={region}, require_vpn={require_vpn}")
                base_spider = StealthSpider(
                    browser_client=browser,
                    relevance_ranker=ranker,
                    chunker=chunker,
                    vpn_provider=vpn_provider,
                    region=region,
                    require_vpn=require_vpn,
                )
            else:
                base_spider = BasicSpider(browser, ranker, chunker)

            # Initialize the goal-oriented spider
            goal_spider = GoalOrientedSpider(
                browser_client=browser,
                relevance_ranker=ranker,
                chunker=chunker,
                planner=planner,
                db=db,
                stop_threshold=args.confidence,
                max_pages=args.max_pages,
                max_depth=args.max_depth,
            )

            try:
                result = await goal_spider.fetch_goal(args.url, args.goal)
                print("\n=== GOAL RESULT ===")
                print(f"Goal: {result['goal']}")
                print(f"Confidence: {result['confidence']:.2f}")
                print(f"Visited pages: {result['visited_count']}")
                print("\nAnswer:")
                print(result['answer'][:2000], "..." if len(result['answer']) > 2000 else "", sep="")
                print("===================")
            finally:
                await browser.close()
                db.close()
            return

        # -----------------------------------------------------------------
        # BASIC OR STEALTH MODE
        # -----------------------------------------------------------------
        if args.stealth:
            if not STEALTH_AVAILABLE:
                raise RuntimeError("StealthSpider not available. Ensure stealth module installed.")
            vpn_provider = args.vpn or DEFAULT_VPN_PROVIDER
            region = args.region or DEFAULT_REGION
            require_vpn = not args.no_require_vpn
            print(f"[CLI] Using StealthSpider with VPN={vpn_provider}, region={region}, require_vpn={require_vpn}")
            spider = StealthSpider(
                browser_client=browser,
                relevance_ranker=ranker,
                chunker=chunker,
                vpn_provider=vpn_provider,
                region=region,
                require_vpn=require_vpn,
            )
        else:
            print("[CLI] Using BasicSpider (no VPN).")
            spider = BasicSpider(browser, ranker, chunker)

        try:
            await run_basic_spider(spider, args.url, Path(args.output), args.pretty)
        finally:
            await browser.close()

    asyncio.run(async_main())


if __name__ == "__main__":
    main()

```

## `core_utils/__init__.py`

```python

```

## `core_utils/chunking.py`

```python
import tiktoken
from typing import List, Dict


class TextChunker:
    """
    Splits large text into LLM-friendly chunks with estimated token limits.
    Attempts to preserve paragraph structure for coherence.
    """

    def __init__(self, model: str = "gpt-4o-mini", max_tokens: int = 1200):
        """
        :param model: GPT model name for tokenizer.
        :param max_tokens: Max tokens per chunk.
        """
        self.max_tokens = max_tokens

        try:
            self.encoder = tiktoken.encoding_for_model(model)
        except KeyError:
            # Fallback for unknown models
            self.encoder = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Return the number of tokens in the given text."""
        return len(self.encoder.encode(text))

    def chunk_text(self, text: str) -> List[Dict]:
        """
        Returns a list of chunk objects: {"chunk_id", "text", "token_count"}
        Large paragraphs will be split if necessary.
        """
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        chunks = []
        current_text = ""
        current_tokens = 0
        chunk_id = 0

        for para in paragraphs:
            para_tokens = self.count_tokens(para)

            # If this paragraph alone exceeds max tokens, split by words
            if para_tokens > self.max_tokens:
                words = para.split()
                sub_text = ""
                for word in words:
                    test_text = (sub_text + " " + word).strip()
                    if self.count_tokens(test_text) > self.max_tokens:
                        chunks.append({
                            "chunk_id": chunk_id,
                            "text": sub_text.strip(),
                            "token_count": self.count_tokens(sub_text)
                        })
                        chunk_id += 1
                        sub_text = word
                    else:
                        sub_text = test_text

                if sub_text.strip():
                    chunks.append({
                        "chunk_id": chunk_id,
                        "text": sub_text.strip(),
                        "token_count": self.count_tokens(sub_text)
                    })
                    chunk_id += 1

                continue

            # Try adding the paragraph to current chunk
            if current_tokens + para_tokens <= self.max_tokens:
                current_text += ("\n\n" + para if current_text else para)
                current_tokens += para_tokens
            else:
                # Finalize current chunk & start a new one
                chunks.append({
                    "chunk_id": chunk_id,
                    "text": current_text,
                    "token_count": current_tokens
                })
                chunk_id += 1
                current_text = para
                current_tokens = para_tokens

        # Add the last chunk if any
        if current_text:
            chunks.append({
                "chunk_id": chunk_id,
                "text": current_text,
                "token_count": current_tokens
            })

        return chunks

```

## `core_utils/url_utils.py`

```python
from urllib.parse import urljoin, urlparse, urlunparse


def canonicalize_url(href: str, base_url: str) -> str | None:
    """
    Convert a possibly relative URL into an absolute canonical form.
    Removes URL fragments. Returns None if invalid.
    """
    try:
        # Join with base (relative → absolute)
        absolute = urljoin(base_url, href)

        # Parse and remove fragment (#...)
        parsed = urlparse(absolute)
        cleaned = parsed._replace(fragment="")

        return urlunparse(cleaned)
    except Exception:
        return None

```

## `extractors/__init__.py`

```python

```

## `extractors/deterministic_extractor.py`

```python
from typing import List
from bs4 import BeautifulSoup
from spider_core.base.link_metadata import LinkMetadata
from spider_core.core_utils.url_utils import canonicalize_url


class DeterministicLinkExtractor:
    """
    Deterministically extracts visible and metadata-based link structures.
    Does not rely on LLMs or heuristics – purely structural extraction.
    """

    @staticmethod
    def extract(html: str, base_url: str) -> List[LinkMetadata]:
        soup = BeautifulSoup(html, "lxml")
        link_map = {}  # href -> LinkMetadata (deduplicates canonical URLs)

        def add_link(raw_href: str, text: str | None, rel: list[str], source: str):
            canon = canonicalize_url(raw_href, base_url)
            if not canon:
                return

            # Create new or merge into existing record
            if canon not in link_map:
                link_map[canon] = LinkMetadata(
                    href=canon,
                    text=(text.strip()[:300] if text else None),
                    rel=rel or [],
                    detected_from=[source],
                    llm_score=0.0,
                    llm_tags=None,
                    reasons=None
                )
            else:
                entry = link_map[canon]
                # Add new source if missing
                if source not in entry.detected_from:
                    entry.detected_from.append(source)
                # Merge rel attributes
                for r in rel:
                    if r not in entry.rel:
                        entry.rel.append(r)
                # If no text set yet and this one has text, use it
                if not entry.text and text:
                    entry.text = text.strip()[:300]

        # 1️⃣ Extract <a href=""> links
        for a in soup.find_all("a", href=True):
            add_link(a["href"], a.get_text(), a.get("rel", []), "a")

        # 2️⃣ Extract <link> tags (e.g., canonical, preload, etc.)
        for link in soup.find_all("link", href=True):
            rel = link.get("rel", [])
            add_link(link["href"], None, rel, f"link:{','.join(rel) or 'link'}")

        # 3️⃣ Extract OpenGraph / Twitter metadata URLs
        for meta in soup.find_all("meta", content=True):
            prop = meta.get("property", "").lower()
            name = meta.get("name", "").lower()
            if prop == "og:url" or name in ("og:url", "twitter:url"):
                add_link(meta["content"], None, [], "meta")

        # 4️⃣ Extract data-href style links commonly used in JS menus
        for el in soup.find_all(attrs={"data-href": True}):
            add_link(el["data-href"], el.get_text(), [], "data-href")

        return list(link_map.values())

```

## `goal/__init__.py`

```python
"""
Goal module: handles goal-driven reasoning and planning for the spider.
"""
from spider_core.goal.goal_planner import GoalPlanner

__all__ = ["GoalPlanner"]

```

## `goal/goal_planner.py`

```python
# goal/goal_planner.py
from typing import List, Dict, Any
from spider_core.llm.openai_gpt_client import OpenAIGPTClient

GOAL_SYSTEM = (
  "You are a goal-driven web research planner. "
  "Given a user GOAL and a PAGE CHUNK, you will: "
  "1) estimate if the GOAL is fully answered by this page content (0-1), "
  "2) extract a concise answer delta (new facts that progress the goal), "
  "3) propose next links (subset of candidates) most likely to progress the goal."
)

def build_user_prompt(goal: str, chunk_text: str, link_candidates: List[Dict[str, str]]) -> str:
    return (
        f"GOAL:\n{goal}\n\n"
        f"PAGE CHUNK:\n{chunk_text[:4000]}\n\n"
        f"LINK CANDIDATES (href + text):\n{[{'href': l['href'], 'text': l.get('text','')} for l in link_candidates]}\n\n"
        "Return JSON: {"
        '"goal_satisfaction_estimate": 0..1, '
        '"answer_delta": "short text", '
        '"next_link_scores": [{"href":"...","score":0..1}]'
        "}"
    )

class GoalPlanner:
    def __init__(self, llm: OpenAIGPTClient):
        self.llm = llm

    async def evaluate_chunk(self, goal: str, chunk_text: str, link_candidates: List[Dict[str, Any]]):
        prompt = build_user_prompt(goal, chunk_text, link_candidates)
        out = await self.llm.complete_json(GOAL_SYSTEM, prompt)
        # normalize
        est = float(out.get("goal_satisfaction_estimate", 0.0))
        delta = out.get("answer_delta", "").strip()
        next_scores = out.get("next_link_scores", [])
        scored = {x["href"]: float(x.get("score", 0.0)) for x in next_scores if "href" in x}
        return est, delta, scored

```

## `llm/__init__.py`

```python

```

## `llm/embeddings_client.py`

```python
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

```

## `llm/llm_client.py`

```python
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

```

## `llm/openai_gpt_client.py`

```python
import json
import asyncio
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from pathlib import Path
import openai


# ✅ Load environment variables
load_dotenv()  # Load project-level .env (if present)
load_dotenv(Path("~/.elf_env").expanduser(), override=False)  # Load personal fallback


class OpenAIGPTClient:
    """
    LLM client for GPT models using OpenAI's API (v2.x).
    Supports JSON-mode completions with retry.
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",  # GPT-4.1-mini alias
        max_retries: int = 2,
        temperature: float = 0.2,
        api_key: Optional[str] = None,
    ):
        # ✅ Prefer explicit API key > environment variables
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("No OpenAI API key found. Set OPENAI_API_KEY in .env or ~/.elf_env")

        # ✅ v2.x uses a client object
        self.client = openai.OpenAI(api_key=api_key)

        self.model = model
        self.max_retries = max_retries
        self.temperature = temperature

    async def complete_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        Sends a JSON-enforced completion request.
        Tries up to `max_retries` times to parse valid JSON.
        Runs the sync OpenAI call in a background thread.
        """
        attempt = 0
        error_message = ""

        while attempt <= self.max_retries:
            try:
                # ✅ Run synchronous OpenAI call in async-safe thread
                response = await asyncio.to_thread(
                    self.client.chat.completions.create,
                    model=self.model,
                    temperature=self.temperature,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )

                content = response.choices[0].message.content.strip()
                return json.loads(content)

            except Exception as e:
                attempt += 1
                error_message = str(e)
                await asyncio.sleep(0.5)

        raise RuntimeError(f"Failed to parse valid JSON after retries. Last error: {error_message}")

```

## `llm/relevance_ranker.py`

```python
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

```

## `requirements.txt`

```text
playwright>=1.42.0
openai>=1.3.0
pydantic>=2.5.0
beautifulsoup4>=4.12.0
lxml>=4.9.3
tiktoken>=0.6.0

```

## `spiders/__init__.py`

```python

```

## `spiders/basic_spider.py`

```python
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


```

## `spiders/goal_spider.py`

```python
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

```

## `spiders/stealth/__init__.py`

```python

```

## `spiders/stealth/stealth_config.py`

```python
# spiders/stealth/stealth_config.py
# Configuration defaults for StealthSpider / VPN behavior.

DEFAULT_VPN_PROVIDER = "nordvpn"
DEFAULT_REGION = "hong_kong"
REQUIRE_VPN_DEFAULT = True

# Behavior toggles
DISCONNECT_BEFORE_LLM = True      # Disconnect VPN before making LLM API calls (recommended)
RECONNECT_AFTER_LLM = False       # Reconnect VPN after LLM calls (optional)
OBFUSCATE_BY_DEFAULT = True       # Try to enable obfuscation if provider supports it
PROTOCOL_DEFAULT = "tcp"          # prefer tcp for stealthy behaviour (OpenVPN over TCP/443)
CONNECT_TIMEOUT = 30              # seconds to wait for VPN connect
DISCONNECT_TIMEOUT = 10           # seconds to wait for VPN disconnect
MAX_CONNECT_RETRIES = 2

```

## `spiders/stealth/stealth_spider.py`

```python
"""
StealthSpider: extends BasicSpider to perform fetches while routing
page loads through a VPN (NordVPN CLI). Important LLM calls will be
performed after disconnecting the VPN so they originate from your normal IP.

Assumptions:
 - NordVPN CLI is installed and accessible as `nordvpn`.
 - VPNManager in spiders.stealth.vpn_manager supports connect(region, obfuscate, protocol)
   and disconnect() and raises VPNError when appropriate.
"""

import asyncio
import logging
from typing import Optional

from spider_core.spiders.basic_spider import BasicSpider
from spider_core.spiders.stealth.vpn_manager import VPNManager, VPNError
from spider_core.spiders.stealth.stealth_config import (
    DEFAULT_REGION,
    DEFAULT_VPN_PROVIDER,
    REQUIRE_VPN_DEFAULT,
    DISCONNECT_BEFORE_LLM,
    RECONNECT_AFTER_LLM,
    OBFUSCATE_BY_DEFAULT,
    PROTOCOL_DEFAULT,
)

logger = logging.getLogger("stealth_spider")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[StealthSpider] %(message)s"))
    logger.addHandler(ch)


async def maybe_await(result):
    if asyncio.iscoroutine(result):
        return await result
    return result


class StealthSpider(BasicSpider):
    def __init__(
        self,
        browser_client,
        relevance_ranker,
        chunker,
        vpn_provider: str = DEFAULT_VPN_PROVIDER,
        region: str = DEFAULT_REGION,
        require_vpn: bool = REQUIRE_VPN_DEFAULT,
        disconnect_before_llm: bool = DISCONNECT_BEFORE_LLM,
        reconnect_after_llm: bool = RECONNECT_AFTER_LLM,
        obfuscate: bool = OBFUSCATE_BY_DEFAULT,
        protocol: str = PROTOCOL_DEFAULT,
    ):
        super().__init__(browser_client, relevance_ranker, chunker)
        self.vpn_provider = vpn_provider
        self.region = region
        self.require_vpn = require_vpn
        self.disconnect_before_llm = disconnect_before_llm
        self.reconnect_after_llm = reconnect_after_llm
        self.obfuscate = obfuscate
        self.protocol = protocol
        self.vpn = VPNManager(provider=vpn_provider)

    async def _ensure_vpn(self):
        if self.require_vpn:
            logger.info(f"Enforcing VPN for region: {self.region}")
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    lambda: self.vpn.connect(self.region, obfuscate=self.obfuscate, protocol=self.protocol),
                )
            except Exception as e:
                logger.error(f"Failed to establish VPN connection: {e}")
                raise VPNError(str(e))
            logger.info("VPN connected")
        else:
            logger.info("VPN not required for this fetch (require_vpn=False).")

    async def _teardown_vpn_before_llm(self):
        if self.disconnect_before_llm:
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self.vpn.disconnect)
                logger.info("VPN disconnected before LLM calls as configured.")
            except Exception as e:
                logger.warning(f"Failed to disconnect VPN before LLM calls: {e}")
        else:
            logger.info("Configured to NOT disconnect before LLM calls.")

    async def _reconnect_vpn_after_llm_if_needed(self):
        if self.reconnect_after_llm and self.require_vpn:
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    lambda: self.vpn.connect(self.region, obfuscate=self.obfuscate, protocol=self.protocol),
                )
                logger.info("VPN reconnected after LLM calls.")
            except Exception as e:
                logger.warning(f"Failed to reconnect VPN after LLM calls: {e}")

    async def fetch(self, url: str):
        """
        Override pipeline to:
         - ensure VPN connected (if required)
         - render + deterministic extraction + chunking (no LLM)
         - disconnect VPN (optional) before LLM
         - run LLM-based scoring
         - optionally reconnect VPN
        """
        # 1) ensure vpn
        try:
            await self._ensure_vpn()
        except VPNError:
            if self.require_vpn:
                raise RuntimeError("StealthSpider: unable to establish VPN and VPN is required.")
            else:
                logger.warning("Could not establish VPN but continuing because require_vpn is False.")

        logger.info(f"Fetching: {url} using VPN (if connected).")

        # 2) Use BasicSpider helper to fetch without LLM (render/extract/chunk)
        try:
            page_result = await self._fetch_without_llm(url)
        except Exception as e:
            logger.warning(f"Failed to build PageResult using BasicSpider helper: {e}")
            # re-raise — we choose failure since fetch couldn't render/extract
            raise

        # 3) Disconnect VPN before doing LLM calls (if configured)
        await self._teardown_vpn_before_llm()

        # 4) Now call BasicSpider's scoring routine (which will call the LLM via ranker)
        try:
            await self._score_links_with_llm(page_result)
        except Exception as e:
            logger.warning(f"LLM ranking failed: {e}")

        # 5) Reconnect VPN after LLM if configured
        await self._reconnect_vpn_after_llm_if_needed()

        return page_result

```

## `spiders/stealth/vpn_manager.py`

```python
# spiders/stealth/vpn_manager.py
"""
VPN helper for StealthSpider.

Currently supports NordVPN via the `nordvpn` CLI.
The manager:
 - can switch NordVPN "technology" to openvpn when required for obfuscation,
 - enable obfuscation,
 - attempt connect/disconnect with retries and timeouts,
 - queries the current connection state.

This is intentionally conservative in side-effects and logs clearly.
"""

import subprocess
import shlex
import time
from typing import Optional
import logging

logger = logging.getLogger("vpn_manager")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[VPN] %(message)s"))
    logger.addHandler(ch)


class VPNError(Exception):
    pass


class VPNManager:
    def __init__(self, provider: str = "nordvpn"):
        self.provider = provider.lower()
        if self.provider != "nordvpn":
            raise VPNError("Only 'nordvpn' provider is implemented in this manager.")
        self._last_region = None

    def _run(self, cmd: str, timeout: int = 15) -> str:
        logger.debug(f"Running: {cmd}")
        parts = shlex.split(cmd)
        try:
            out = subprocess.check_output(parts, stderr=subprocess.STDOUT, timeout=timeout)
            return out.decode("utf-8", errors="replace")
        except subprocess.CalledProcessError as e:
            logger.debug(f"Cmd failed ({cmd}): {e.output.decode(errors='replace')}")
            raise VPNError(f"Command failed: {cmd}\n{e.output.decode(errors='replace')}")
        except subprocess.TimeoutExpired as e:
            logger.debug(f"Cmd timeout ({cmd})")
            raise VPNError(f"Command timeout: {cmd}")

    # ---------- NordVPN-specific helpers ----------
    def _nordvpn_status(self) -> str:
        return self._run("nordvpn status", timeout=6)

    def _is_connected(self) -> bool:
        try:
            out = self._nordvpn_status().lower()
            return "connected" in out
        except Exception:
            return False

    def _current_country(self) -> Optional[str]:
        try:
            out = self._nordvpn_status()
            # Status output contains "Country: Hong Kong" or "City: ..."
            for line in out.splitlines():
                if line.lower().startswith("country:"):
                    return line.split(":", 1)[1].strip().lower().replace(" ", "_")
        except Exception:
            return None

    def ensure_openvpn_for_obfuscation(self) -> None:
        """
        NordVPN disallows `obfuscate on` unless technology is set to openvpn.
        Switch to openvpn if needed.
        """
        try:
            tech_out = self._run("nordvpn settings")
            # quick check: if technology is already OpenVPN, bail
            if "Technology: OpenVPN" in tech_out or "technology: OpenVPN".lower() in tech_out.lower():
                logger.debug("NordVPN technology already OpenVPN.")
                return
        except Exception:
            # settings might vary; attempt to set openvpn anyway
            logger.debug("Could not read nordvpn settings; proceeding to set technology to openvpn.")

        logger.info("Setting NordVPN technology to OpenVPN (required for obfuscation).")
        try:
            self._run("nordvpn set technology openvpn", timeout=6)
        except Exception as e:
            logger.warning(f"Could not set technology to openvpn: {e}")

    def set_obfuscation(self, value: bool) -> None:
        val = "on" if value else "off"
        logger.info(f"Setting obfuscation: {val}")
        try:
            self._run(f"nordvpn set obfuscate {val}", timeout=6)
        except VPNError as e:
            # surfacing helpful message
            msg = str(e)
            if "not available" in msg or "not installed" in msg.lower():
                logger.warning("Obfuscation not supported with current settings/provider.")
            else:
                logger.warning(f"Failed to set obfuscation: {e}")

    def set_protocol(self, protocol: str) -> None:
        protocol = protocol.lower()
        if protocol not in ("tcp", "udp"):
            raise VPNError("protocol must be 'tcp' or 'udp'")
        logger.info(f"Setting NordVPN protocol to {protocol}")
        try:
            self._run(f"nordvpn set protocol {protocol}", timeout=6)
        except Exception as e:
            logger.warning(f"Failed to set protocol: {e}")

    def connect(self, region: str, obfuscate: bool = True, protocol: str = "tcp", timeout: int = 30) -> None:
        """
        Connect to provider's region. Uses retries and attempts to enable obfuscation if requested.
        """
        region = region.replace(" ", "_")
        self._last_region = region

        # ensure protocol + obfuscation readiness
        if obfuscate:
            # NordVPN requires openvpn tech for obfuscation
            try:
                self.ensure_openvpn_for_obfuscation()
            except Exception:
                logger.debug("ensure_openvpn_for_obfuscation had an issue, continuing.")

        # set protocol
        try:
            self.set_protocol(protocol)
        except Exception:
            logger.debug("set_protocol failed; continuing.")

        # enable obfuscation if requested
        if obfuscate:
            try:
                self.set_obfuscation(True)
            except Exception:
                logger.debug("set_obfuscation failed; continuing.")

        # attempt connect with retries
        last_err = None
        for attempt in range(1, 1 + 2):
            try:
                logger.info(f"Attempting VPN connection to: {region} (attempt {attempt})")
                out = self._run(f"nordvpn connect {region}", timeout=timeout)
                logger.info(out.strip().splitlines()[-1] if out else "Connected (no output)")
                # confirm connected
                start = time.time()
                while time.time() - start < (timeout if timeout else 30):
                    if self._is_connected():
                        logger.info(f"VPN connected to {region}")
                        return
                    time.sleep(1)
                raise VPNError("Connection attempt timed out")
            except VPNError as e:
                last_err = e
                logger.warning(f"Connect attempt failed: {e}")
                # try a fallback: turn obfuscation off and try TCP again if obfuscate was on
                if obfuscate:
                    try:
                        logger.info("Falling back: disabling obfuscation and retrying.")
                        self.set_obfuscation(False)
                    except Exception:
                        pass
                time.sleep(1)

        raise VPNError(f"Failed to connect to VPN {region}. Last error: {last_err}")

    def disconnect(self, timeout: int = 10) -> None:
        """
        Disconnect vpn client.
        """
        if not self._is_connected():
            logger.info("VPN already disconnected.")
            return
        logger.info("Disconnecting VPN...")
        try:
            out = self._run("nordvpn disconnect", timeout=timeout)
            logger.info("Disconnected.")
            # small wait to ensure new interface state
            time.sleep(1)
        except Exception as e:
            logger.warning(f"Failed to cleanly disconnect VPN: {e}")

    def running_provider(self) -> str:
        return self.provider

    def last_region(self) -> Optional[str]:
        return self._last_region

```

## `storage/__init__.py`

```python
"""
Storage module: database and persistence layer for crawled pages and embeddings.
"""
from spider_core.storage.db import DB

__all__ = ["DB"]

```

## `storage/db.py`

```python
# storage/db.py
import sqlite3, json, time
from pathlib import Path
from typing import Iterable, Optional, Any

SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS pages(
  id INTEGER PRIMARY KEY,
  url TEXT UNIQUE,
  canonical TEXT,
  status INTEGER,
  fetched_at INTEGER,
  title TEXT,
  visible_text TEXT
);

CREATE TABLE IF NOT EXISTS links(
  id INTEGER PRIMARY KEY,
  from_url TEXT,
  to_url TEXT,
  anchor_text TEXT,
  rel TEXT,
  llm_score_est REAL DEFAULT 0.0,
  llm_score_final REAL DEFAULT 0.0,
  UNIQUE(from_url, to_url)
);

CREATE TABLE IF NOT EXISTS chunks(
  id INTEGER PRIMARY KEY,
  page_url TEXT,
  chunk_id INTEGER,
  text TEXT,
  token_count INTEGER,
  UNIQUE(page_url, chunk_id)
);

-- Simple vector storage (float32 array as JSON; small, portable)
CREATE TABLE IF NOT EXISTS embeddings(
  id INTEGER PRIMARY KEY,
  page_url TEXT,
  chunk_id INTEGER,
  vector TEXT,             -- json.dumps(list of floats)
  model TEXT,
  dim INTEGER,
  created_at INTEGER,
  UNIQUE(page_url, chunk_id, model)
);

CREATE TABLE IF NOT EXISTS crawl_log(
  id INTEGER PRIMARY KEY,
  url TEXT,
  action TEXT,             -- queued, fetched, skipped, failed
  reason TEXT,
  ts INTEGER
);

CREATE INDEX IF NOT EXISTS idx_pages_url ON pages(url);
CREATE INDEX IF NOT EXISTS idx_links_to ON links(to_url);
CREATE INDEX IF NOT EXISTS idx_chunks_page ON chunks(page_url);
CREATE INDEX IF NOT EXISTS idx_embeds_page ON embeddings(page_url);
"""

class DB:
    def __init__(self, path: str = "spider_core.db"):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def upsert_page(self, url: str, canonical: Optional[str], status: int, title: Optional[str], visible_text: str):
        self.conn.execute(
            """INSERT INTO pages(url, canonical, status, fetched_at, title, visible_text)
               VALUES(?,?,?,?,?,?)
               ON CONFLICT(url) DO UPDATE SET
                 canonical=excluded.canonical,
                 status=excluded.status,
                 fetched_at=excluded.fetched_at,
                 title=excluded.title,
                 visible_text=excluded.visible_text
            """,
            (url, canonical, status, int(time.time()), title, visible_text),
        )
        self.conn.commit()

    def upsert_links(self, from_url: str, links: Iterable[dict]):
        rows = []
        for l in links:
            rows.append((
                from_url, l["href"], l.get("text"), json.dumps(l.get("rel", [])),
                float(l.get("llm_score", 0.0))
            ))
        self.conn.executemany(
            """INSERT INTO links(from_url, to_url, anchor_text, rel, llm_score_est)
               VALUES(?,?,?,?,?)
               ON CONFLICT(from_url,to_url) DO UPDATE SET
                 anchor_text=excluded.anchor_text,
                 rel=excluded.rel,
                 llm_score_est=excluded.llm_score_est
            """,
            rows
        )
        self.conn.commit()

    def set_final_link_score(self, from_url: str, to_url: str, score: float):
        self.conn.execute(
            "UPDATE links SET llm_score_final=? WHERE from_url=? AND to_url=?",
            (float(score), from_url, to_url)
        )
        self.conn.commit()

    def upsert_chunks(self, page_url: str, chunks: Iterable[dict]):
        rows = []
        for c in chunks:
            rows.append((page_url, int(c["chunk_id"]), c["text"], int(c["token_count"])))
        self.conn.executemany(
            """INSERT INTO chunks(page_url, chunk_id, text, token_count)
               VALUES(?,?,?,?)
               ON CONFLICT(page_url,chunk_id) DO UPDATE SET
                 text=excluded.text,
                 token_count=excluded.token_count
            """, rows
        )
        self.conn.commit()

    def upsert_embedding(self, page_url: str, chunk_id: int, vec: list[float], model: str, dim: int):
        self.conn.execute(
            """INSERT INTO embeddings(page_url,chunk_id,vector,model,dim,created_at)
               VALUES(?,?,?,?,?,?)
               ON CONFLICT(page_url,chunk_id,model) DO UPDATE SET
                 vector=excluded.vector,
                 dim=excluded.dim,
                 created_at=excluded.created_at
            """,
            (page_url, chunk_id, json.dumps(vec), model, dim, int(time.time()))
        )
        self.conn.commit()

    def already_fetched(self, url: str) -> bool:
        r = self.conn.execute("SELECT 1 FROM pages WHERE url=? LIMIT 1", (url,)).fetchone()
        return r is not None

    def log(self, url: str, action: str, reason: Optional[str] = None):
        self.conn.execute(
            "INSERT INTO crawl_log(url,action,reason,ts) VALUES(?,?,?,?)",
            (url, action, reason, int(time.time()))
        )
        self.conn.commit()

    def close(self):
        self.conn.close()

```

## `test/test.py`

```python
import asyncio
from browser.playwright_client import PlaywrightBrowserClient

async def test():
    client = PlaywrightBrowserClient()
    html, text, status = await client.render("https://nytimes.com")
    print("Status:", status)
    print("HTML length:", len(html))
    print("Visible text:", text[:200])
    await client.close()

asyncio.run(test())

```

## `test/test2.py`

```python
from extractors.deterministic_extractor import DeterministicLinkExtractor

sample_html = """
<a href="/about">About Us</a>
<link rel="canonical" href="https://example.com/home" />
<meta property="og:url" content="https://example.com/page" />
<div data-href="/contact">Get in Touch</div>
"""

links = DeterministicLinkExtractor.extract(sample_html, "https://example.com")
for link in links:
    print(link)

```

## `test/test3.py`

```python
from core_utils.chunking import TextChunker

text = """
This is a paragraph.
Another one.
And a very long paragraph that keeps going and might exceed a chunk limit depending on the token count, so this is just for demonstration purposes.
"""
chunker = TextChunker(model="gpt-4o-mini", max_tokens=20)
chunks = chunker.chunk_text(text)
for c in chunks:
    print(c)

```

## `test/test4.py`

```python
from llm.openai_gpt_client import OpenAIGPTClient
import asyncio

async def main():
    llm = OpenAIGPTClient()
    result = await llm.complete_json(
        "You are a JSON bot. Output only valid JSON with one key 'greet'.",
        "Say hi in JSON."
    )
    print(result)

asyncio.run(main())

```

## `test/test_ranker.py`

```python
import asyncio
from llm.openai_gpt_client import OpenAIGPTClient
from llm.relevance_ranker import RelevanceRanker
from base.link_metadata import LinkMetadata

async def main():
    llm = OpenAIGPTClient()
    ranker = RelevanceRanker(llm)

    links = [
        LinkMetadata(href="https://example.com/about", text="About Us", rel=[], detected_from=["a"]),
        LinkMetadata(href="https://example.com/contact", text="Contact", rel=[], detected_from=["a"]),
    ]

    chunks = [{"chunk_id": 0, "text": "This page discusses who we are and our company mission.", "token_count": 12}]

    enriched = await ranker.score_links(links, chunks)
    for link in enriched:
        print(link)

asyncio.run(main())

```

## `test/test_spider.py`

```python
import asyncio
from browser.playwright_client import PlaywrightBrowserClient
from core_utils.chunking import TextChunker
from llm.openai_gpt_client import OpenAIGPTClient
from llm.relevance_ranker import RelevanceRanker
from spiders.basic_spider import BasicSpider


async def main():
    browser = PlaywrightBrowserClient()
    llm = OpenAIGPTClient()
    ranker = RelevanceRanker(llm)
    chunker = TextChunker()

    spider = BasicSpider(browser, ranker, chunker)
    result = await spider.fetch("https://example.com")

    print(result)
    await browser.close()

asyncio.run(main())

```

<details>
<summary>📁 Final Project Structure</summary>

```
📁 base/
    📄 __init__.py
    📄 link_metadata.py
    📄 page_result.py
    📄 spider.py
📁 browser/
    📄 __init__.py
    📄 browser_client.py
    📄 playwright_client.py
📁 core_utils/
    📄 __init__.py
    📄 chunking.py
    📄 url_utils.py
📁 extractors/
    📄 __init__.py
    📄 deterministic_extractor.py
📁 goal/
    📄 __init__.py
    📄 goal_planner.py
📁 llm/
    📄 __init__.py
    📄 embeddings_client.py
    📄 llm_client.py
    📄 openai_gpt_client.py
    📄 relevance_ranker.py
📁 spiders/
    📁 stealth/
        📄 __init__.py
        📄 stealth_config.py
        📄 stealth_spider.py
        📄 vpn_manager.py
    📄 __init__.py
    📄 basic_spider.py
    📄 goal_spider.py
📁 storage/
    📄 __init__.py
    📄 db.py
📁 test/
    📄 test.py
    📄 test2.py
    📄 test3.py
    📄 test4.py
    📄 test_ranker.py
    📄 test_spider.py
📄 __init__.py
📄 cli_spider.py
📄 requirements.txt
```

</details>
