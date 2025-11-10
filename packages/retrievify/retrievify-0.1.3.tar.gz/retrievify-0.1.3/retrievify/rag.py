from .index import DocumentIndexer
from .retrieve import Retriever
from .generate import LLM
from .utils import default_config

class RAG:
    def __init__(self, config: dict | None = None):
        self.cfg = default_config() | (config or {})
        self.indexer = DocumentIndexer(self.cfg)
        self.retriever = Retriever(self.cfg)
        self.llm = LLM(self.cfg) if self.cfg.get("generation", False) else None

    def fit(self, path_or_glob: str, patterns=None):
        docs = self.indexer.build_corpus(path_or_glob, patterns=patterns)
        self.retriever.build(docs, embeddings=self.indexer.embedder)
        return self

    def ask(self, query: str, k: int = 5, generate: bool | None = None):
        hits = self.retriever.search(query, k=k)
        if generate or (generate is None and self.llm):
            context = "\n\n".join(h["chunk"] for h in hits)
            answer = self.llm.answer(query, context)
            return {"answer": answer, "evidence": hits}
        return {"evidence": hits}
