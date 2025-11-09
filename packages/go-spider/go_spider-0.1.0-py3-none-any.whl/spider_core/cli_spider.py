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
    # NOTE: your module currently defines GoalSpider, not GoalOrientedSpider
    from spider_core.spiders.goal_spider import GoalSpider
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
    parser.add_argument("--max-depth", type=int, default=3, help="Maximum recursion depth for goal mode")
    # keep these args for future; currently not used by GoalSpider, but harmless:
    parser.add_argument("--db", type=str, default="spider_core.db", help="(Reserved) SQLite DB path for future use")
    parser.add_argument("--max-pages", type=int, default=25, help="(Reserved) Max pages to crawl in goal mode")
    parser.add_argument("--confidence", type=float, default=0.85, help="(Reserved) Confidence threshold for goal mode")

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
                raise RuntimeError("Goal modules not found. Ensure spiders/goal_spider.py exists and is importable.")

            print(f"[CLI] 🚀 Running Goal Spider for goal: '{args.goal}'")

            # Choose base spider (stealth or normal) just for behavior parity;
            # GoalSpider itself will handle recursive crawling.
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
                # We don't actually *use* base_spider inside GoalSpider yet, but you can wire it in later.
            else:
                base_spider = BasicSpider(browser, ranker, chunker)

            # Initialize the goal spider (uses llm directly)
            goal_spider = GoalSpider(
                browser_client=browser,
                relevance_ranker=ranker,
                chunker=chunker,
                llm_client=llm,
                max_depth=args.max_depth,
            )

            try:
                result = await goal_spider.run_goal(args.url, args.goal)
                print("\n=== GOAL RESULT ===")
                print(f"Goal: {result['goal']}")
                print(f"Found: {result['found']}")
                print(f"Confidence: {result['confidence']:.2f}")
                print(f"Visited pages: {result['visited_pages']}")
                print("\nAnswer:")
                print(result["answer"] or "(no answer found)")
                print("===================")
            finally:
                await browser.close()
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
