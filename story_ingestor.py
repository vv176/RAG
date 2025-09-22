from __future__ import annotations

from typing import Optional

from story_chunker import StoryChunker
from embedder import get_embedding
from weaviate_helper import insert_story_part, insert_story_part_overlap


class StoryIngester:
    def __init__(self, story_path: str = "data/story.txt", chunk_size: int = 2000, overlap_percent: float = 0.5) -> None:
        self.story_path = story_path
        self.chunker = StoryChunker(chunk_size=chunk_size, overlap_percent=overlap_percent)

    def ingest(self, limit: Optional[int] = None) -> int:
        """
        Read story file, chunk into fixed-size chunks, embed each chunk,
        and insert into Weaviate via helper. Returns number of processed chunks.
        """
        with open(self.story_path, "r", encoding="utf-8") as f:
            story_text = f.read()
        
        chunks = self.chunker.chunk_by_size(story_text)
        count = 0
        
        for ch in (chunks[:limit] if limit else chunks):
            part_text = ch["text"]
            vector = get_embedding(part_text)
            insert_story_part(part_text, vector)
            count += 1
        
        return count

    def ingest_with_overlaps(self, limit: Optional[int] = None) -> int:
        """
        Read story file, chunk into overlapping chunks, embed each chunk,
        and insert into Weaviate via helper. Returns number of processed chunks.
        """
        with open(self.story_path, "r", encoding="utf-8") as f:
            story_text = f.read()
        
        chunks = self.chunker.chunk_with_overlap(story_text)
        count = 0
        
        for ch in (chunks[:limit] if limit else chunks):
            part_text = ch["text"]
            vector = get_embedding(part_text)
            insert_story_part_overlap(part_text, vector)
            count += 1
        
        return count


if __name__ == "__main__":
    ingester = StoryIngester("/Users/vivekanandvivek/RAG/data/story.txt")
    n = ingester.ingest_with_overlaps()
    print(f"Ingested {n} story chunks.")
