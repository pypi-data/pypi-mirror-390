# retrievify

![PyPI](https://img.shields.io/pypi/v/retrievify)
![Python](https://img.shields.io/pypi/pyversions/retrievify)
![License](https://img.shields.io/github/license/MeerMagia/retrievify)
![Downloads](https://img.shields.io/pypi/dm/retrievify)

**Lightweight Retrieval-Augmented Generation (RAG) toolkit in 3 lines.**

```python
from retrievify import RAG
rag = RAG().fit("docs/", patterns=["*.pdf","*.md","*.txt"])
print(rag.ask("What are the core contributions?"))
```

## Why retrievify?
- ⚡ Fast local embeddings (MiniLM) by default
- 🧱 Smart chunking & FAISS/Annoy vector stores (Windows-friendly)
- 🧩 Optional LLM generation hook (OpenAI/Ollama)
- 🛠️ CLI for quick indexing and querying

## Install
```bash
pip install retrievify
# If FAISS is tricky on Windows, use Annoy:
pip install annoy
```

## Quickstart
```python
from retrievify import RAG
rag = RAG().fit("docs/")
res = rag.ask("What are the key limitations?", k=5)
print(res["evidence"][0])
```

## CLI
```bash
retrievify index ./docs --pattern "*.pdf,*.md"
retrievify query ./docs -q "evaluation pipeline" -k 5 --generate
```

## LLM (optional)
Set env var for OpenAI first:
```powershell
$env:OPENAI_API_KEY="sk-..."
```
Then:
```python
from retrievify import RAG
rag = RAG({"generation": True, "llm_backend": "openai"}).fit("docs/")
print(rag.ask("Summarize the paper")["answer"])
```

## Roadmap
- Cross-encoder re-ranking
- HTML/URL loaders & deduplication
- Simple retrieval eval (Recall@k, MRR, NDCG)
