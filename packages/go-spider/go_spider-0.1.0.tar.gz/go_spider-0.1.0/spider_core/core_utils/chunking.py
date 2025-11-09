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
