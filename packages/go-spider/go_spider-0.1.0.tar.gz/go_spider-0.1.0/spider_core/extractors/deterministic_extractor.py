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
