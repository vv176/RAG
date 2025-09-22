"""
Enhanced Demo script with LLM descriptions
"""

import json
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from code_chunker import CodeChunker


def main():
    """Demo the enhanced code chunker with LLM descriptions"""
    
    # Initialize chunker with LLM descriptions enabled
    codebase_path = "../code-base"
    chunker = CodeChunker(codebase_path, generate_descriptions=True)
    
    print("🔍 Starting enhanced code chunking with LLM descriptions...")
    print(f"Codebase path: {codebase_path}")
    
    # Debug: Check if path exists
    from pathlib import Path
    path = Path(codebase_path)
    print(f"Path exists: {path.exists()}")
    print(f"Path is directory: {path.is_dir()}")
    
    # Debug: Find Python files
    python_files = list(path.rglob("*.py"))
    print(f"Found {len(python_files)} Python files")
    if python_files:
        print(f"First few files: {python_files[:5]}")
    
    # Chunk the codebase
    chunks, relationships = chunker.chunk_codebase()
    
    # Print summary
    chunker.print_summary()
    
    # Save results
    output_path = "enhanced_chunks_output.json"
    chunker.save_chunks(output_path)
    
    # Show enhanced examples
    print(f"\n=== Enhanced Examples with LLM Descriptions ===")
    
    # Show package chunks with descriptions
    package_chunks = [c for c in chunks if c['type'] == 'package']
    if package_chunks:
        print(f"\n📁 Package Chunks with Descriptions ({len(package_chunks)}):")
        for chunk in package_chunks[:2]:
            print(f"\n{chunk['name']}:")
            print(f"  Purpose: {chunk['metadata']['purpose']}")
            print(f"  Files: {chunk['metadata']['file_count']}")
            print(f"  Description: {chunk.get('description', 'No description')[:150]}...")
    
    # Show class chunks with descriptions
    class_chunks = [c for c in chunks if c['type'] == 'class']
    if class_chunks:
        print(f"\n🏗️  Class Chunks with Descriptions ({len(class_chunks)}):")
        for chunk in class_chunks[:3]:
            print(f"\n{chunk['name']}:")
            print(f"  Purpose: {chunk['metadata']['purpose']}")
            print(f"  Methods: {len(chunk['metadata']['methods'])}")
            print(f"  Description: {chunk.get('description', 'No description')[:150]}...")
    
    # Show method chunks with descriptions
    method_chunks = [c for c in chunks if c['type'] == 'method']
    if method_chunks:
        print(f"\n⚙️  Method Chunks with Descriptions ({len(method_chunks)}):")
        for chunk in method_chunks[:3]:
            print(f"\n{chunk['name']}:")
            print(f"  Purpose: {chunk['metadata']['purpose']}")
            print(f"  Parameters: {len(chunk['metadata']['parameters'])}")
            print(f"  Description: {chunk.get('description', 'No description')[:150]}...")
    
    # Show function chunks with descriptions
    function_chunks = [c for c in chunks if c['type'] == 'function']
    if function_chunks:
        print(f"\n🔧 Function Chunks with Descriptions ({len(function_chunks)}):")
        for chunk in function_chunks[:3]:
            print(f"\n{chunk['name']}:")
            print(f"  Purpose: {chunk['metadata']['purpose']}")
            print(f"  Description: {chunk.get('description', 'No description')[:150]}...")
    
    # Show chunk structure with description
    print(f"\n=== Enhanced Chunk Structure Example ===")
    if chunks:
        example_chunk = chunks[0]
        print(f"Chunk type: {example_chunk['type']}")
        print(f"Name: {example_chunk['name']}")
        print(f"Description: {example_chunk.get('description', 'No description')}")
        print(f"Content preview: {example_chunk['content'][:100]}...")
        print(f"Metadata keys: {list(example_chunk['metadata'].keys())}")
    
    # Query examples
    print(f"\n=== Enhanced Query Examples ===")
    print("With LLM descriptions, you can now answer queries like:")
    print("  - 'How do I create a new user account?'")
    print("  - 'What handles user authentication?'")
    print("  - 'How do I process an order?'")
    print("  - 'What validates user input?'")
    print("  - 'How do I send email notifications?'")
    print("  - 'What manages database connections?'")
    
    print(f"\n✅ Enhanced chunking complete! Saved to {output_path}")


if __name__ == "__main__":
    main()
