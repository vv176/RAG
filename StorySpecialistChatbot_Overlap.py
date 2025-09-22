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
from weaviate_helper import search_hybrid_story_overlap


SYSTEM_PROMPT = (
    "You are Story Specialist, a helpful and friendly assistant for story-related queries. "
    "Speak naturally and conversationally. Integrate any provided story context seamlessly without saying phrases like 'based on the provided context' or 'the story says'. "
    "Answer clearly, be concise, and when helpful, cite specific details, characters, or plot points directly. "
    "If the context is insufficient, ask a focused clarifying question or state what is missing—without referencing retrieval mechanics."
)


class StorySpecialistChatbotOverlap:
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
        lines: List[str] = ["Relevant story context:"]
        for i, h in enumerate(hits, 1):
            part = h.get("part") or ""
            lines.append(f"[{i}] {part}")
        return "\n".join(lines)

    def ask(self, user_message: str) -> str:
        # Keep history
        self.history.append({"role": "user", "content": user_message})

        # Rewrite query using conversation window
        rewritten_query = self.rewriter.rewrite(self.history) or user_message
        print("rewritten query => ", rewritten_query)
        # Search story parts overlap using hybrid search (top 3)
        query_vec = get_embedding(rewritten_query)
        hits = search_hybrid_story_overlap(rewritten_query, vector=query_vec, alpha=0.5, limit=7)
        print("hits from weaviate => ", hits)
        # Build messages with story context
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
    bot = StorySpecialistChatbotOverlap()
    print("Story Specialist Chatbot (Overlap Chunks). Type 'exit' to quit.\n")
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
