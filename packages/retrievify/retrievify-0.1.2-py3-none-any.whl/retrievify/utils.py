from pypdf import PdfReader
from pathlib import Path

def default_config():
    return {
        "chunk_max_tokens": 256,
        "chunk_overlap_tokens": 32,
        "embed_backend": "tfidf",  # <— pure Python fallback
        "embed_model": "sentence-transformers/all-MiniLM-L6-v2",
        "generation": False,
        "llm_backend": "openai",
        "llm_model": "gpt-4o-mini"
    }

def load_text_from_file(path: str) -> str:
    p = Path(path)
    suf = p.suffix.lower()
    if suf == ".pdf":
        reader = PdfReader(str(p))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return p.read_text(encoding="utf-8", errors="ignore")
