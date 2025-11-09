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
