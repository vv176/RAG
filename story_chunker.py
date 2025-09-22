"""
story_chunker.py
Chunking strategies for story text: fixed-size and overlapping chunking.
"""

from __future__ import annotations

import re
from typing import List, Dict, Optional


class StoryChunker:
    """
    Chunking strategies for story text.
    Demonstrates fixed-size chunking problems and overlapping solutions.
    """
    
    def __init__(self, chunk_size: int = 300, overlap_percent: float = 0.25):
        self.chunk_size = chunk_size
        self.overlap_percent = overlap_percent
        self.overlap_size = int(chunk_size * overlap_percent)
    
    def chunk_by_size(self, text: str) -> List[Dict]:
        """
        Fixed-size chunking - splits text into chunks of exactly chunk_size characters.
        This method demonstrates the problems with fixed-size chunking:
        - Words get split mid-word
        - Sentences get cut off
        - Context is lost at boundaries
        """
        chunks = []
        start = 0
        chunk_id = 1
        
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            # Don't create empty chunks
            if chunk_text.strip():
                chunks.append({
                    "id": chunk_id,
                    "text": chunk_text,
                    "start_char": start,
                    "end_char": end,
                    "length": len(chunk_text),
                    "chunk_type": "fixed_size"
                })
                chunk_id += 1
            
            start = end
        
        return chunks
    
    def chunk_with_overlap(self, text: str) -> List[Dict]:
        """
        Overlapping chunking - creates chunks with overlap to preserve context.
        Each chunk overlaps with the previous one by overlap_percent.
        This helps maintain context across chunk boundaries.
        """
        chunks = []
        start = 0
        chunk_id = 1
        
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            # Don't create empty chunks
            if chunk_text.strip():
                chunks.append({
                    "id": chunk_id,
                    "text": chunk_text,
                    "start_char": start,
                    "end_char": end,
                    "length": len(chunk_text),
                    "chunk_type": "overlapping",
                    "overlap_size": self.overlap_size
                })
                chunk_id += 1
            
            # Move start position by (chunk_size - overlap_size) to create overlap
            start = start + self.chunk_size - self.overlap_size
            
            # Stop if we've covered the entire text
            if start >= len(text):
                break
        
        return chunks
    


def demo_chunking_strategies():
    """
    Demonstrate different chunking strategies on the story text.
    """
    # Read the story
    with open("/Users/vivekanandvivek/RAG/data/story.txt", "r", encoding="utf-8") as f:
        story_text = f.read()
    
    print(f"Story length: {len(story_text)} characters")
    print("=" * 80)
    
    # Create chunker with small chunk size to demonstrate problems
    chunker = StoryChunker(chunk_size=200, overlap_percent=0.25)
    
    # Fixed-size chunking
    print("\n1. FIXED-SIZE CHUNKING (200 chars)")
    print("-" * 40)
    fixed_chunks = chunker.chunk_by_size(story_text)
    print(f"Number of chunks: {len(fixed_chunks)}")
    
    # Show first few chunks to demonstrate problems
    for i, chunk in enumerate(fixed_chunks[:3]):
        print(f"\nChunk {chunk['id']}:")
        print(f"Length: {chunk['length']} chars")
        print(f"Text: '{chunk['text'][:100]}...'")
        print(f"Ends with: '{chunk['text'][-20:]}'")
    
    # Overlapping chunking
    print("\n\n2. OVERLAPPING CHUNKING (200 chars, 25% overlap)")
    print("-" * 50)
    overlap_chunks = chunker.chunk_with_overlap(story_text)
    print(f"Number of chunks: {len(overlap_chunks)}")
    
    # Show first few chunks
    for i, chunk in enumerate(overlap_chunks[:3]):
        print(f"\nChunk {chunk['id']}:")
        print(f"Length: {chunk['length']} chars")
        print(f"Text: '{chunk['text'][:100]}...'")
        print(f"Ends with: '{chunk['text'][-20:]}'")


if __name__ == "__main__":
    demo_chunking_strategies()
