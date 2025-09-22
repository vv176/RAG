from __future__ import annotations

import os
from typing import List, Dict

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

from openai import OpenAI

from query_rewriter import QueryRewriter
from embedder import get_embedding
from weaviate_helper import search_near_vector


SYSTEM_PROMPT = (
    "You are Agreement Specialist, a helpful and friendly assistant for agreement-related queries between parties. "
    "Speak naturally and conversationally. Integrate any provided context seamlessly without saying phrases like 'based on the provided context' or 'the document says'. "
    "Answer clearly, be concise, and when helpful, cite concrete details (figures, clauses, timeframes) directly. "
    "If the context is insufficient, ask a focused clarifying question or state what is missing—without referencing retrieval mechanics."
)


class AgreementSpecialistChatbotMultiHits:
    def __init__(self, llm_model: str = "gpt-4o") -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set in environment")
        self._client = OpenAI(api_key=api_key)
        self.llm_model = llm_model
        self.history: List[Dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.rewriter = QueryRewriter(model=llm_model)

    def _context_block(self, hits: List[Dict]) -> str:
        if not hits:
            return ""
        lines: List[str] = ["Relevant context from FAQ (multiple matches):"]
        for i, h in enumerate(hits, 1):
            q = h.get("question") or ""
            a = h.get("answer") or ""
            lines.append(f"[{i}] Q: {q}\n    A: {a}")
        return "\n".join(lines)

    def ask(self, user_message: str) -> str:
        # Keep history
        self.history.append({"role": "user", "content": user_message})

        # Rewrite query using conversation window
        rewritten_query = self.rewriter.rewrite(self.history) or user_message
        print("rewritten query => ", rewritten_query)
        # Retrieve multi-hit context
        query_vec = get_embedding(rewritten_query)
        hits = search_near_vector(query_vec, limit=15)
        print(hits)
        # Build messages with all contexts as a system note
        messages: List[Dict[str, str]] = list(self.history)
        ctx_block = self._context_block(hits)
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
    bot = AgreementSpecialistChatbotMultiHits()
    print("Agreement Specialist Chatbot (Multi-Hits). Type 'exit' to quit.\n")
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


