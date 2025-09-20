from __future__ import annotations

import os
from typing import List, Dict, Optional

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


class AgreementSpecialistChatbot:
    def __init__(self, llm_model: str = "gpt-4o") -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set in environment")
        self._client = OpenAI(api_key=api_key)
        self.llm_model = llm_model
        self.history: List[Dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.rewriter = QueryRewriter(model=llm_model)

    def _build_messages(self, user_message: str, top_context: Optional[Dict] = None) -> List[Dict[str, str]]:
        msgs: List[Dict[str, str]] = list(self.history)
        if top_context:
            ctx_q = top_context.get("question") or ""
            ctx_a = top_context.get("answer") or ""
            context_block = f"Relevant context from FAQ (top match):\nQ: {ctx_q}\nA: {ctx_a}"
            msgs.append({"role": "system", "content": context_block})
        msgs.append({"role": "user", "content": user_message})
        return msgs

    def ask(self, user_message: str) -> str:
        # Maintain conversation history
        self.history.append({"role": "user", "content": user_message})

        # Rewrite query using the recent conversation window
        rewritten_query = self.rewriter.rewrite(self.history)
        if not rewritten_query:
            rewritten_query = user_message
        print("rewritten query => ", rewritten_query)
        # Retrieve top-1 context from Weaviate
        query_vec = get_embedding(rewritten_query)
        hits = search_near_vector(query_vec, limit=3)
        print("hits from weaviate => ", hits)
        top_hit = hits[0] if hits else None
        print(top_hit)
        # Build LLM messages with contex
        messages = self._build_messages(user_message, top_hit)

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
    bot = AgreementSpecialistChatbot()
    print("Agreement Specialist Chatbot. Type 'exit' to quit.\n")
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


