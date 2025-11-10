from retrievify import RAG

def test_smoke_fit_and_query(tmp_path):
    fp = tmp_path / "a.txt"
    fp.write_text("Retrievify is a tiny RAG toolkit. It supports chunking and retrieval.", encoding="utf-8")
    rag = RAG().fit(tmp_path.as_posix(), patterns=["*.txt"])
    out = rag.ask("What is retrievify?")
    assert "evidence" in out and len(out["evidence"]) > 0
