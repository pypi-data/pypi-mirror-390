import numpy as np

# Try FAISS, then Annoy; if neither is available, use a pure-NumPy fallback.
try:
    import faiss  # type: ignore
    _HAS_FAISS = True
except Exception:
    _HAS_FAISS = False

try:
    from annoy import AnnoyIndex  # type: ignore
    _HAS_ANNOY = True
except Exception:
    _HAS_ANNOY = False


class FaissStore:
    def __init__(self):
        self.index = None
        self.meta  = []

    def build(self, embeddings, meta):
        import faiss  # local import
        d = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(d)
        self.index.add(embeddings)
        self.meta = meta

    def search(self, qvec, k=5):
        D, I = self.index.search(qvec, k)
        return I[0], D[0]


class AnnoyStore:
    def __init__(self, dim, n_trees=10):
        self.dim = dim
        self.index = AnnoyIndex(dim, metric='angular')
        self.meta = []
        self._built = False

    def build(self, embeddings, meta):
        for i, vec in enumerate(embeddings):
            self.index.add_item(i, vec.tolist())
        self.index.build(10)
        self.meta = meta
        self._built = True

    def search(self, qvec, k=5):
        q = qvec[0].tolist()
        idxs = self.index.get_nns_by_vector(q, k, include_distances=True)
        I, D = idxs[0], [1 - (1/(1 + d)) for d in idxs[1]]  # rough similarity proxy
        return np.array(I), np.array(D, dtype=float)


class NumpyStore:
    """Pure-NumPy cosine-similarity search (no C++ deps). Slower, but zero-setup."""
    def __init__(self):
        self.X = None  # (n, d)
        self.meta = []

    def build(self, embeddings, meta):
        # ensure normalized vectors (cosine == dot after norm)
        eps = 1e-12
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True) + eps
        self.X = embeddings / norms
        self.meta = meta

    def search(self, qvec, k=5):
        eps = 1e-12
        q = qvec[0]
        q = q / (np.linalg.norm(q) + eps)
        sims = self.X @ q  # (n,)
        if k >= sims.shape[0]:
            idxs = np.argsort(-sims)
        else:
            idxs = np.argpartition(-sims, k-1)[:k]
            idxs = idxs[np.argsort(-sims[idxs])]
        scores = sims[idxs]
        return idxs.astype(int), scores.astype(float)


def make_store(embeddings):
    if _HAS_FAISS:
        s = FaissStore()
        s.build(embeddings, meta=None)
        return s, "faiss"
    elif _HAS_ANNOY:
        s = AnnoyStore(embeddings.shape[1])
        s.build(embeddings, meta=None)
        return s, "annoy"
    else:
        s = NumpyStore()
        s.build(embeddings, meta=None)
        return s, "numpy"
