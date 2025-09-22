"""
LLM Description Generator for Code Chunks
Generates rich, searchable descriptions for better vector search
"""

import openai
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMDescriptor:
    """Generates LLM descriptions for code chunks"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = openai.OpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY")
        )
        self.model = "gpt-4o-mini"  # Cost-effective model for descriptions
    
    def generate_chunk_description(self, chunk: Dict[str, Any]) -> str:
        """Generate LLM description for a code chunk"""
        try:
            prompt = self._build_prompt(chunk)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert code analyst. Write clear, concise descriptions of code that are optimized for semantic search and vector retrieval."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating description for {chunk['name']}: {e}")
            return self._fallback_description(chunk)
    
    def _build_prompt(self, chunk: Dict[str, Any]) -> str:
        """Build prompt for LLM based on chunk type"""
        chunk_type = chunk['type']
        name = chunk['name']
        content = chunk['content'][:800]  # Limit content length
        metadata = chunk.get('metadata', {})
        
        if chunk_type == 'package':
            return f"""
            Analyze this Python package and write a searchable description:
            
            Package: {name}
            Purpose: {metadata.get('purpose', 'Unknown')}
            Files: {metadata.get('file_count', 0)} files
            Content: {content}
            
            Write a description that explains:
            - What this package does in the system
            - What functionality it provides
            - When developers would use it
            - How it fits into the overall architecture
            
            Keep it concise but informative for vector search.
            """
        
        elif chunk_type == 'class':
            return f"""
            Analyze this Python class and write a searchable description:
            
            Class: {name}
            Purpose: {metadata.get('purpose', 'Unknown')}
            Methods: {len(metadata.get('methods', []))} methods
            Content: {content}
            
            Write a description that explains:
            - What this class represents or does
            - What problems it solves
            - When developers would use it
            - How it fits into the system
            
            Keep it concise but informative for vector search.
            """
        
        elif chunk_type == 'method':
            return f"""
            Analyze this Python method and write a searchable description:
            
            Method: {name}
            Class: {metadata.get('class_name', 'Unknown')}
            Purpose: {metadata.get('purpose', 'Unknown')}
            Parameters: {metadata.get('parameters', [])}
            Content: {content}
            
            Write a description that explains:
            - What this method does
            - What inputs it expects
            - What it returns
            - When developers would call it
            - What problems it solves
            
            Keep it concise but informative for vector search.
            """
        
        elif chunk_type == 'function':
            return f"""
            Analyze this Python function and write a searchable description:
            
            Function: {name}
            Purpose: {metadata.get('purpose', 'Unknown')}
            Parameters: {metadata.get('parameters', [])}
            Content: {content}
            
            Write a description that explains:
            - What this function does
            - What inputs it expects
            - What it returns
            - When developers would use it
            - What problems it solves
            
            Keep it concise but informative for vector search.
            """
        
        elif chunk_type == 'imports':
            return f"""
            Analyze these Python imports and write a searchable description:
            
            Module: {name}
            Purpose: {metadata.get('purpose', 'Unknown')}
            Content: {content}
            
            Write a description that explains:
            - What dependencies this module has
            - What functionality it provides
            - How it fits into the system
            - What external libraries it uses
            
            Keep it concise but informative for vector search.
            """
        
        else:
            return f"""
            Analyze this code chunk and write a searchable description:
            
            Type: {chunk_type}
            Name: {name}
            Purpose: {metadata.get('purpose', 'Unknown')}
            Content: {content}
            
            Write a description that explains what this code does and when it would be used.
            Keep it concise but informative for vector search.
            """
    
    def _fallback_description(self, chunk: Dict[str, Any]) -> str:
        """Generate fallback description when LLM fails"""
        chunk_type = chunk['type']
        name = chunk['name']
        purpose = chunk.get('metadata', {}).get('purpose', 'Unknown')
        
        if chunk_type == 'package':
            return f"Package {name}: {purpose}"
        elif chunk_type == 'class':
            return f"Class {name}: {purpose}"
        elif chunk_type == 'method':
            return f"Method {name}: {purpose}"
        elif chunk_type == 'function':
            return f"Function {name}: {purpose}"
        elif chunk_type == 'imports':
            return f"Module imports for {name}: {purpose}"
        else:
            return f"{chunk_type.title()} {name}: {purpose}"
    
    def batch_generate_descriptions(self, chunks: list[Dict[str, Any]], batch_size: int = 10) -> list[Dict[str, Any]]:
        """Generate descriptions for multiple chunks in batches"""
        enhanced_chunks = []
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            print(f"Processing batch {i//batch_size + 1}/{(len(chunks) + batch_size - 1)//batch_size}")
            
            for chunk in batch:
                description = self.generate_chunk_description(chunk)
                chunk['description'] = description
                enhanced_chunks.append(chunk)
        
        return enhanced_chunks
