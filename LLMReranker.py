from __future__ import annotations

import os
from typing import List, Dict, Tuple

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

from openai import OpenAI


SYSTEM_PROMPT = (
    "You are a reranker. Given a user query and a list of candidate passages, "
    "assign a single numeric relevance score to each passage reflecting how well it answers the query. "
    "Use a 0–6 integer scale (0=irrelevant, 6=directly answers with high confidence). "
    "Base scoring strictly on semantic relevance and specificity. Return only a JSON list of integers, in order."
)


class LLMReranker:
    def __init__(self, model: str = "gpt-4o-mini") -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set in environment")
        self._client = OpenAI(api_key=api_key)
        self.model = model

    def _build_prompt(self, query: str, passages: List[str]) -> List[Dict[str, str]]:
        numbered = "\n\n".join([f"[{i+1}]\n{p}" for i, p in enumerate(passages)])
        user = (
            "Query:\n"
            f"{query}\n\n"
            "Passages (score each on 0–6):\n"
            f"{numbered}\n\n"
            "Call the provided tool with an array of integers named 'scores', one per passage, strictly in order."
        )
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user},
        ]

    def rerank(self, query: str, hits: List[Dict], top_r: int = 3) -> List[Dict]:
        if not hits:
            return []
        passages: List[str] = []
        for h in hits:
            q = h.get("question") or ""
            a = h.get("answer") or ""
            passages.append(f"Q: {q}\nA: {a}")

        messages = self._build_prompt(query, passages)
        # Define tool schema to force structured output
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "score_passages",
                    "description": "Return relevance scores (0-6) for each passage in order.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "scores": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "description": "Array of integers, length equals number of passages."
                            }
                        },
                        "required": ["scores"],
                        "additionalProperties": False,
                    },
                },
            }
        ]

        completion = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0,
            tools=tools,
            tool_choice={"type": "function", "function": {"name": "score_passages"}},
        )

        scores: List[int]
        try:
            tool_calls = completion.choices[0].message.tool_calls or []
            if not tool_calls:
                raise ValueError("No tool call returned")
            args_text = tool_calls[0].function.arguments
            import json
            args = json.loads(args_text)
            raw_scores = args.get("scores")
            if not isinstance(raw_scores, list):
                raise ValueError("scores missing or not a list")
            scores = [int(x) for x in raw_scores]
        except Exception:
            scores = [0] * len(passages)

        # Zip, sort by score desc, stable by index
        indexed = list(enumerate(hits))
        scored = [(*pair, scores[i] if i < len(scores) else 0) for i, pair in enumerate(indexed)]
        scored.sort(key=lambda t: (t[2], -t[0]), reverse=True)
        return [h for _, h, _ in scored[:top_r]]


