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
