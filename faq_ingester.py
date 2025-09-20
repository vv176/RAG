from __future__ import annotations

from typing import Optional

from faq_chunker import parse_qa_file
from embedder import get_embedding
from weaviate_helper import insert_chunk, search_near_vector, search_bm25


class FAQIngester:
    def __init__(self, faq_path: str = "data/FAQ.txt") -> None:
        self.faq_path = faq_path

    def ingest(self, limit: Optional[int] = None) -> int:
        """
        Read FAQ file, chunk into Q/A pairs, embed concatenated text,
        and insert into Weaviate via helper. Returns number of processed pairs.
        """
        chunks = parse_qa_file(self.faq_path)
        count = 0
        for ch in (chunks[:limit] if limit else chunks):
            question = ch["question"]
            answer = ch["answer"]
            combined = f"Q: {question}\nA: {answer}"
            vector = get_embedding(combined)
            insert_chunk(question, answer, vector)
            count += 1
        return count


if __name__ == "__main__":
    #ingester = FAQIngester("/Users/vivekanandvivek/RAG/data/FAQ.txt")
    #n = ingester.ingest()
    #print(f"Ingested {n} FAQ pairs.")

    demo_queries = [
        "When was the agreement signed and how long is it valid?",
        "What happens in case of poaching?",
        "Will I be guaranteed 99.5% uptime for the hosted components?",
        "Who are the parties to this agreement?",
        "Can this be terminated early and under what conditions?",
        "Which law governs and where is jurisdiction?",
        "What happens in case of a dispute?"
    ]
    print("\nSearch demos (user-style queries):")
    for q in demo_queries:
        q_vec = get_embedding(q)
        hits = search_near_vector(q_vec, limit=3)
        print(f"\nQuery: {q}")
        for r in hits:
            print(f"- distance={r['distance']:.4f}\n  Q: {r['question']}\n  A: {r['answer']}")

    print("="*100)
    keyword_queries = [
        "What are the delivery obligations typically included in an agreement between parties?",
        "What happens in case of poaching?",
        "What happens in case of a dispute?"
    ]
    print("Search demos (keyword-style queries):")
    for q in keyword_queries:
        hits = search_bm25(q, limit=3)
        print(f"\nQuery: {q}")
        for r in hits:
            print(f"- score={r['score']:.4f}\n  Q: {r['question']}\n  A: {r['answer']}")
