# Code Chunker

A hierarchical code chunker for Python codebases that creates structured, searchable components for RAG systems.

## Features

- **6 Chunk Types**: Package, Class, Method, Function, Imports, Constants
- **Hierarchical Structure**: Maintains relationships between code components
- **Rich Metadata**: Comprehensive metadata for each chunk
- **AST-based Parsing**: Accurate Python code analysis
- **Relationship Tracking**: Captures dependencies and relationships

## Chunk Types

### 1. Package Chunks
- **Purpose**: Folder/package summaries
- **Content**: Package overview, contained files, features
- **Metadata**: File count, subpackages, API routes, database tables

### 2. Class Chunks
- **Purpose**: Class structure and relationships
- **Content**: Class signature, method signatures, purpose
- **Metadata**: Methods, attributes, base classes, decorators

### 3. Method Chunks
- **Purpose**: Individual method implementations
- **Content**: Complete method source code
- **Metadata**: Parameters, return type, access level, decorators

### 4. Function Chunks
- **Purpose**: Standalone function implementations
- **Content**: Complete function source code
- **Metadata**: Parameters, return type, decorators

### 5. Imports Chunks
- **Purpose**: Module dependencies
- **Content**: Import statements and dependencies
- **Metadata**: Import types (standard, third_party, local)

### 6. Constants Chunks
- **Purpose**: Module-level constants
- **Content**: Constant definitions
- **Metadata**: Constant names, types, usage

## Usage

```python
from code_chunker import CodeChunker

# Initialize chunker
chunker = CodeChunker("path/to/codebase")

# Chunk the codebase
chunks, relationships = chunker.chunk_codebase()

# Print summary
chunker.print_summary()

# Save results
chunker.save_chunks("output.json")
```

## Demo

Run the demo script to see the chunker in action:

```bash
cd code-agent/chunker
python demo.py
```

## Chunk Structure

Each chunk follows this structure:

```python
{
    "type": "class|method|function|package|imports|constants",
    "name": "chunk_name",
    "content": "chunk_content",
    "metadata": {
        "file_path": "path/to/file.py",
        "purpose": "chunk_purpose",
        "dependencies": ["dep1", "dep2"],
        # ... type-specific metadata
    }
}
```

## Query Examples

With these chunks, you can answer queries like:

- **"What does the app/api folder contain?"** → Package chunk
- **"How does user authentication work?"** → Method chunks for auth methods
- **"What methods are available in the Product class?"** → Class chunk + method chunks
- **"What utility functions are available?"** → Function chunks
- **"What are the dependencies of this module?"** → Imports chunk

## Benefits

1. **No Redundancy**: Each piece of code appears exactly once
2. **Hierarchical Search**: Can search at different abstraction levels
3. **Rich Context**: Comprehensive metadata for better retrieval
4. **Relationship Awareness**: Captures code dependencies
5. **RAG-Optimized**: Designed specifically for retrieval-augmented generation

## Architecture

```
CodeChunker
├── chunk_codebase()          # Main chunking method
├── _chunk_file()            # Process individual files
├── _extract_imports()       # Extract import statements
├── _extract_constants()     # Extract module constants
├── _extract_class()         # Extract classes and methods
├── _extract_method()        # Extract method implementations
├── _extract_function()      # Extract standalone functions
├── _extract_main_block()    # Extract main execution block
└── _generate_package_chunks() # Generate package summaries
```

## Dependencies

- Python 3.7+
- Standard library only (ast, pathlib, dataclasses)

## License

MIT License
