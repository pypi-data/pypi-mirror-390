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
