import numpy as np

class EmbeddingBackend:
    """
    Embedding backend with two modes:
      - 'tfidf'  : pure scikit-learn (no Torch). Zero-setup.
      - 'minilm' : sentence-transformers MiniLM (requires torch).
    """
    def __init__(self, cfg):
        self.backend = cfg.get("embed_backend", "tfidf")  # default to tfidf (Windows-friendly)
        self.model_name = cfg.get("embed_model", "sentence-transformers/all-MiniLM-L6-v2")
        self._model = None
        self._vectorizer = None
        self._fitted = False

        if self.backend == "tfidf":
            # set up TF-IDF vectorizer lazily
            from sklearn.feature_extraction.text import TfidfVectorizer
            # 384 features ~= MiniLM dim; add bigrams for better recall
            self._vectorizer = TfidfVectorizer(max_features=384, ngram_range=(1, 2))

    def _ensure_minilm(self):
        if self._model is None:
            # lazy import so package import doesn't force torch load
            from sentence_transformers import SentenceTransformer  # heavy import
            self._model = SentenceTransformer(self.model_name)

    def encode(self, texts):
        if self.backend == "tfidf":
            if not self._fitted:
                X = self._vectorizer.fit_transform(texts)
                self._fitted = True
            else:
                X = self._vectorizer.transform(texts)
            return X.toarray().astype("float32")

        # MiniLM
        self._ensure_minilm()
        embs = self._model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
        return np.asarray(embs, dtype="float32")
