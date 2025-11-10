from pathlib import Path
from .embed import EmbeddingBackend
from .chunker import chunk_text
from .utils import load_text_from_file

class DocumentIndexer:
    def __init__(self, cfg):
        self.cfg = cfg
        self.embedder = EmbeddingBackend(cfg)

    def build_corpus(self, root: str, patterns=None):
        root = Path(root)
        globs = patterns or ["*.txt", "*.md", "*.pdf"]
        files = []
        for pat in globs:
            files += list(root.rglob(pat))
        docs = []
        for fp in files:
            text = load_text_from_file(fp)
            for i, chunk in enumerate(chunk_text(text, self.cfg)):
                docs.append({
                    "id": f"{fp.as_posix()}:::{i}",
                    "path": fp.as_posix(),
                    "chunk": chunk,
                })
        return docs
