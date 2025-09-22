from __future__ import annotations

import os
from typing import List, Dict, Tuple

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

from openai import OpenAI
from query_rewriter import QueryRewriter
from embedder import get_embedding
from weaviate_helper import search_near_vector

try:
    from sentence_transformers import CrossEncoder  # type: ignore
except Exception as exc:
    raise ImportError(
        "sentence-transformers is required for reranking. Install with: pip install sentence-transformers"
    ) from exc


SYSTEM_PROMPT = (
    "You are Agreement Specialist, a helpful and friendly assistant for agreement-related queries between parties. "
    "Speak naturally and conversationally. Integrate any provided context seamlessly without saying phrases like 'based on the provided context' or 'the document says'. "
    "Answer clearly, be concise, and when helpful, cite concrete details (figures, clauses, timeframes) directly. "
    "If the context is insufficient, ask a focused clarifying question or state what is missing—without referencing retrieval mechanics."
)


class AgreementSpecialistChatbotMultiHitsLargeReranker:
    def __init__(self, llm_model: str = "gpt-4o", reranker_model: str = "BAAI/bge-reranker-large") -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set in environment")
        self._client = OpenAI(api_key=api_key)
        self.llm_model = llm_model
        self.history: List[Dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.rewriter = QueryRewriter(model=llm_model)
        # Eagerly load larger reranker
        self._reranker = CrossEncoder(reranker_model)

    def _context_block(self, hits: List[Dict]) -> str:
        if not hits:
            return ""
        lines: List[str] = ["Relevant context from FAQ (re-ranked top-3):"]
        for i, h in enumerate(hits, 1):
            q = h.get("question") or ""
            a = h.get("answer") or ""
            lines.append(f"[{i}] Q: {q}\n    A: {a}")
        return "\n".join(lines)

    def _rerank(self, query: str, hits: List[Dict], top_r: int = 3) -> List[Dict]:
        if not hits:
            return []
        pairs: List[Tuple[str, str]] = []
        for h in hits:
            q = h.get("question") or ""
            a = h.get("answer") or ""
            passage = f"Q: {q}\nA: {a}"
            pairs.append((query, passage))
        scores = self._reranker.predict(pairs)  # higher is better
        scored = [({**h}, score) for h, score in zip(hits, scores)]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [h for h, _ in scored[:top_r]]

    def ask(self, user_message: str) -> str:
        self.history.append({"role": "user", "content": user_message})
        rewritten_query = self.rewriter.rewrite(self.history) or user_message
        query_vec = get_embedding(rewritten_query)
        hits = search_near_vector(query_vec, limit=15)
        print("hits from weaviate", hits)
        top_hits = self._rerank(rewritten_query, hits, top_r=3)
        print("top hits from reranker", top_hits)
        messages: List[Dict[str, str]] = list(self.history)
        ctx_block = self._context_block(top_hits)
        if ctx_block:
            messages.append({"role": "system", "content": ctx_block})

        completion = self._client.chat.completions.create(
            model=self.llm_model,
            messages=messages,
            temperature=0.2,
            max_tokens=400,
        )
        answer = (completion.choices[0].message.content or "").strip()
        self.history.append({"role": "assistant", "content": answer})
        return answer


def _repl() -> None:
    bot = AgreementSpecialistChatbotMultiHitsLargeReranker()
    print("Agreement Specialist Chatbot (Multi-Hits + Large Reranker). Type 'exit' to quit.\n")
    while True:
        try:
            user_input = input("You: ").strip()
        except EOFError:
            break
        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            break
        response = bot.ask(user_input)
        print(f"Assistant: {response}\n")


if __name__ == "__main__":
    _repl()


