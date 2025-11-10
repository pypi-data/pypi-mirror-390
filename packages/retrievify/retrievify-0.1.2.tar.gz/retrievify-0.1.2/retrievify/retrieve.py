from .store import make_store
from .embed import EmbeddingBackend

class Retriever:
    def __init__(self, cfg):
        self.cfg = cfg
        self.store = None
        self.embedder = None
        self.chunks = None
        self.backend_name = None

    def build(self, docs, embeddings: EmbeddingBackend):
        self.embedder = embeddings
        self.chunks = docs
        X = self.embedder.encode([d["chunk"] for d in docs])
        self.store, self.backend_name = make_store(X)
        if hasattr(self.store, "meta"):
            self.store.meta = docs

    def search(self, query, k=5):
        q = self.embedder.encode([query])
        idxs, scores = self.store.search(q, k)
        hits = []
        for i, s in zip(idxs, scores):
            d = self.chunks[int(i)]
            hits.append({"score": float(s), **d})
        return hits
