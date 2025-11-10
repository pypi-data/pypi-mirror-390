from retrievify import RAG

# Windows-friendly demo
rag = RAG().fit("examples/sample_docs", patterns=["*.pdf","*.md","*.txt"])
q = "Summarize the contribution and limitations."
res = rag.ask(q, k=5, generate=False)
for h in res["evidence"]:
    print(f"{h['score']:.3f} :: {h['path']}\n{h['chunk'][:180]}...\n")
