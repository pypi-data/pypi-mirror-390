from retrievify import RAG

def test_query_top1(tmp_path):
    (tmp_path / "d1.txt").write_text("Neural models with embeddings enable semantic search.", encoding="utf-8")
    (tmp_path / "d2.txt").write_text("Classical IR uses TF-IDF and BM25.", encoding="utf-8")
    rag = RAG().fit(tmp_path.as_posix(), patterns=["*.txt"])
    res = rag.ask("semantic search with embeddings", k=1)
    assert len(res["evidence"]) == 1
