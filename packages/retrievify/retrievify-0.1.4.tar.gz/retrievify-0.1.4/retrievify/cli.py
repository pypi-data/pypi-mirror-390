import json
import typer
from .rag import RAG

app = typer.Typer(help="retrievify: tiny RAG toolkit (Windows-friendly)")

@app.command()
def index(path: str, pattern: str = "*.pdf,*.md,*.txt", out: str = "index.json"):
    pats = [p.strip() for p in pattern.split(",")]
    rag = RAG()
    docs = rag.indexer.build_corpus(path, patterns=pats)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
    typer.echo(f"Indexed {len(docs)} chunks → {out}")

@app.command()
def query(path: str, q: str, k: int = 5, generate: bool = False):
    rag = RAG({"generation": generate}).fit(path)
    res = rag.ask(q, k=k, generate=generate)
    if generate and "answer" in res:
        typer.echo(f"Answer:\n{res['answer']}\n")
    for i, h in enumerate(res["evidence"], 1):
        typer.echo(f"[{i}] {h['score']:.3f}  {h['path']}\n{h['chunk'][:240]}...\n")
