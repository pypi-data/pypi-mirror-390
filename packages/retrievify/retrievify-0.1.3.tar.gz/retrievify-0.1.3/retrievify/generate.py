import os

class LLM:
    def __init__(self, cfg):
        self.cfg = cfg
        self.backend = cfg.get("llm_backend", "openai")  # default to openai
        self.model = cfg.get("llm_model", "gpt-4o-mini")

    def answer(self, query: str, context: str) -> str:
        if self.backend == "openai":
            try:
                import openai
                openai.api_key = os.getenv("OPENAI_API_KEY")
                prompt = f"Answer concisely using only the context.\n\nContext:\n{context}\n\nQuestion: {query}\n"
                # Using legacy ChatCompletion API for broad compatibility
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                )
                return response["choices"][0]["message"]["content"]
            except Exception as e:
                return f"OpenAI backend error: {e}"

        if self.backend == "ollama":
            try:
                import ollama
                response = ollama.chat(
                    model=self.model,
                    messages=[{"role": "user", "content": f"Context: {context}\n\nQ: {query}"}],
                )
                # Newer ollama returns dict with 'message' or 'messages' depending on version
                if isinstance(response, dict):
                    if "message" in response and "content" in response["message"]:
                        return response["message"]["content"]
                    if "messages" in response and response["messages"]:
                        return response["messages"][-1].get("content", "")
                return str(response)
            except Exception as e:
                return f"Ollama backend error: {e}"

        # Fallback: no backend configured
        return f"Q: {query}\n\nContext:\n{context[:800]}\n\n(No LLM backend configured.)"
