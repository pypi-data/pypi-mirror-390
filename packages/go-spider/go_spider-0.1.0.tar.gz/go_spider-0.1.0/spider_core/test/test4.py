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
