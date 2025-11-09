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
