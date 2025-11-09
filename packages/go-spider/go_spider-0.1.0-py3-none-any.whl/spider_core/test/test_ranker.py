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
