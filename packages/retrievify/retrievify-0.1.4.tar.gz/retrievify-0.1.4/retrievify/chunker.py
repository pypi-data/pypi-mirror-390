import re

def chunk_text(text: str, cfg: dict):
    text = re.sub(r"\s+\n", "\n", text).strip()
    max_tokens = cfg["chunk_max_tokens"]
    overlap    = cfg["chunk_overlap_tokens"]
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        end = min(i + max_tokens, len(words))
        chunk = " ".join(words[i:end])
        chunks.append(chunk)
        if end == len(words): break
        i = end - overlap
    return chunks
