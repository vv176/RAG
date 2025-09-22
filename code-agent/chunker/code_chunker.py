"""
Hierarchical Code Chunker
Chunks Python codebases into structured, searchable components with LLM descriptions
"""

import os
import ast
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import asdict

try:
    from .chunk_types import ChunkType, create_chunk
    from .llm_descriptor import LLMDescriptor
except ImportError:
    from chunk_types import ChunkType, create_chunk
    from llm_descriptor import LLMDescriptor


class CodeChunker:
    """Hierarchical code chunker for Python codebases with LLM descriptions"""
    
    def __init__(self, codebase_path: str, generate_descriptions: bool = False):
        self.codebase_path = Path(codebase_path)
        self.chunks: List[Dict[str, Any]] = []
        self.relationships: List[Dict[str, Any]] = []
        self.generate_descriptions = generate_descriptions
        self.llm_descriptor = LLMDescriptor() if generate_descriptions else None
    
    def chunk_codebase(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Chunk entire codebase and return chunks with relationships"""
        self.chunks = []
        self.relationships = []
        
        # Find all Python files
        python_files = list(self.codebase_path.rglob("*.py"))
        
        # Process each file
        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue
            
            try:
                file_chunks, file_relationships = self._chunk_file(file_path)
                self.chunks.extend(file_chunks)
                self.relationships.extend(file_relationships)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue
        
        # Generate package chunks
        self._generate_package_chunks()
        
        # Generate LLM descriptions if enabled
        if self.generate_descriptions and self.llm_descriptor:
            print("🤖 Generating LLM descriptions for chunks...")
            self.chunks = self.llm_descriptor.batch_generate_descriptions(self.chunks)
        
        return self.chunks, self.relationships
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        skip_patterns = [
            "__pycache__",
            ".git",
            ".pytest_cache",
            "venv",
            "env",
            ".env"
        ]
        
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def _chunk_file(self, file_path: Path) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Chunk a single Python file"""
        chunks = []
        relationships = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Get relative path for metadata
            rel_path = str(file_path.relative_to(self.codebase_path))
            
            # Extract imports
            imports_chunk = self._extract_imports(tree, rel_path, content)
            if imports_chunk:
                chunks.append(imports_chunk)
            
            # Extract constants
            constants_chunk = self._extract_constants(tree, rel_path, content)
            if constants_chunk:
                chunks.append(constants_chunk)
            
            # Extract classes and their methods
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_chunk, class_relationships = self._extract_class(node, rel_path, content)
                    if class_chunk:
                        chunks.append(class_chunk)
                        relationships.extend(class_relationships)
            
            # Extract standalone functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and not self._is_method(node):
                    function_chunk = self._extract_function(node, rel_path, content)
                    if function_chunk:
                        chunks.append(function_chunk)
            
            # Extract main block
            main_chunk = self._extract_main_block(tree, rel_path, content)
            if main_chunk:
                chunks.append(main_chunk)
            
        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
        
        return chunks, relationships
    
    def _extract_imports(self, tree: ast.AST, file_path: str, content: str) -> Optional[Dict[str, Any]]:
        """Extract import statements"""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                import_info = self._parse_import_node(node)
                if import_info:
                    imports.append(import_info)
        
        if not imports:
            return None
        
        # Create imports content
        imports_content = "Module Dependencies:\n\n"
        for imp in imports:
            if imp["type"] == "standard":
                imports_content += f"Standard Library: {imp['module']}\n"
            elif imp["type"] == "third_party":
                imports_content += f"Third Party: {imp['module']}\n"
            elif imp["type"] == "local":
                imports_content += f"Local: {imp['module']}\n"
            
            if imp.get("items"):
                imports_content += f"  - {', '.join(imp['items'])}\n"
            imports_content += "\n"
        
        return create_chunk(
            chunk_type=ChunkType.IMPORTS,
            name="module_imports",
            content=imports_content.strip(),
            file_path=file_path,
            purpose="Module dependencies and imports",
            imports=imports
        )
    
    def _parse_import_node(self, node: ast.Import | ast.ImportFrom) -> Optional[Dict[str, str]]:
        """Parse an import node into structured data"""
        if isinstance(node, ast.Import):
            # import module
            for alias in node.names:
                module_name = alias.name.split('.')[0]
                return {
                    "module": module_name,
                    "type": self._classify_import(module_name),
                    "items": [alias.name]
                }
        
        elif isinstance(node, ast.ImportFrom):
            # from module import items
            module_name = node.module or ""
            items = [alias.name for alias in node.names]
            
            return {
                "module": module_name,
                "type": self._classify_import(module_name),
                "items": items
            }
        
        return None
    
    def _classify_import(self, module_name: str) -> str:
        """Classify import as standard, third_party, or local"""
        if not module_name:
            return "local"
        
        # Standard library modules (simplified list)
        stdlib_modules = {
            'os', 'sys', 'json', 'datetime', 'typing', 'pathlib', 're',
            'collections', 'functools', 'itertools', 'math', 'random',
            'string', 'io', 'urllib', 'http', 'email', 'html', 'xml',
            'sqlite3', 'csv', 'configparser', 'logging', 'unittest',
            'asyncio', 'threading', 'multiprocessing', 'subprocess'
        }
        
        if module_name in stdlib_modules:
            return "standard"
        elif module_name.startswith('app.') or module_name.startswith('.'):
            return "local"
        else:
            return "third_party"
    
    def _extract_constants(self, tree: ast.AST, file_path: str, content: str) -> Optional[Dict[str, Any]]:
        """Extract module-level constants"""
        constants = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                # Check if it's a module-level constant (all caps)
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        constants.append({
                            "name": target.id,
                            "value": ast.unparse(node.value) if hasattr(ast, 'unparse') else str(node.value)
                        })
        
        if not constants:
            return None
        
        # Create constants content
        constants_content = "Module Constants:\n\n"
        for const in constants:
            constants_content += f"{const['name']} = {const['value']}\n"
        
        return create_chunk(
            chunk_type=ChunkType.CONSTANTS,
            name="module_constants",
            content=constants_content.strip(),
            file_path=file_path,
            purpose="Module-level constants and configuration",
            constants=constants
        )
    
    def _extract_class(self, node: ast.ClassDef, file_path: str, content: str) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
        """Extract class and its methods"""
        relationships = []
        
        # Extract class methods
        methods = []
        method_chunks = []
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(item.name)
                
                # Create method chunk
                method_chunk = self._extract_method(item, file_path, content, node.name)
                if method_chunk:
                    method_chunks.append(method_chunk)
                    relationships.append({
                        "type": "contains",
                        "source": f"{file_path}:{node.name}",
                        "target": f"{file_path}:{node.name}.{item.name}",
                        "metadata": {"purpose": "class_method"}
                    })
        
        # Create class content (signatures only)
        class_content = f"class {node.name}:\n"
        if node.bases:
            base_classes = [ast.unparse(base) if hasattr(ast, 'unparse') else str(base) for base in node.bases]
            class_content += f"    # Inherits from: {', '.join(base_classes)}\n"
        
        class_content += f"    # Purpose: {self._extract_docstring(node) or 'No description available'}\n\n"
        
        for method in methods:
            class_content += f"    def {method}(self, ...):\n"
            class_content += f"        # Method implementation\n\n"
        
        # Create class chunk
        class_chunk = create_chunk(
            chunk_type=ChunkType.CLASS,
            name=node.name,
            content=class_content.strip(),
            file_path=file_path,
            purpose=self._extract_docstring(node) or f"Class {node.name}",
            class_name=node.name,
            methods=methods,
            base_classes=[ast.unparse(base) if hasattr(ast, 'unparse') else str(base) for base in node.bases],
            decorators=[ast.unparse(dec) if hasattr(ast, 'unparse') else str(dec) for dec in node.decorator_list]
        )
        
        return class_chunk, relationships + method_chunks
    
    def _extract_method(self, node: ast.FunctionDef, file_path: str, content: str, class_name: str) -> Optional[Dict[str, Any]]:
        """Extract method implementation"""
        # Get method source code
        method_content = self._extract_source_code(node, content)
        
        # Parse parameters
        parameters = []
        for arg in node.args.args:
            param = arg.arg
            if arg.annotation:
                param += f": {ast.unparse(arg.annotation) if hasattr(ast, 'unparse') else str(arg.annotation)}"
            parameters.append(param)
        
        # Get return type
        return_type = ""
        if node.returns:
            return_type = ast.unparse(node.returns) if hasattr(ast, 'unparse') else str(node.returns)
        
        # Determine access level
        access = "private" if node.name.startswith('_') else "public"
        
        return create_chunk(
            chunk_type=ChunkType.METHOD,
            name=f"{class_name}.{node.name}",
            content=method_content,
            file_path=file_path,
            purpose=self._extract_docstring(node) or f"Method {node.name}",
            class_name=class_name,
            method_name=node.name,
            parameters=parameters,
            return_type=return_type,
            access=access,
            decorators=[ast.unparse(dec) if hasattr(ast, 'unparse') else str(dec) for dec in node.decorator_list],
            is_async=isinstance(node, ast.AsyncFunctionDef)
        )
    
    def _extract_function(self, node: ast.FunctionDef, file_path: str, content: str) -> Optional[Dict[str, Any]]:
        """Extract standalone function"""
        # Get function source code
        function_content = self._extract_source_code(node, content)
        
        # Parse parameters
        parameters = []
        for arg in node.args.args:
            param = arg.arg
            if arg.annotation:
                param += f": {ast.unparse(arg.annotation) if hasattr(ast, 'unparse') else str(arg.annotation)}"
            parameters.append(param)
        
        # Get return type
        return_type = ""
        if node.returns:
            return_type = ast.unparse(node.returns) if hasattr(ast, 'unparse') else str(node.returns)
        
        return create_chunk(
            chunk_type=ChunkType.FUNCTION,
            name=node.name,
            content=function_content,
            file_path=file_path,
            purpose=self._extract_docstring(node) or f"Function {node.name}",
            function_name=node.name,
            parameters=parameters,
            return_type=return_type,
            decorators=[ast.unparse(dec) if hasattr(ast, 'unparse') else str(dec) for dec in node.decorator_list],
            is_async=isinstance(node, ast.AsyncFunctionDef)
        )
    
    def _extract_main_block(self, tree: ast.AST, file_path: str, content: str) -> Optional[Dict[str, Any]]:
        """Extract main block (if __name__ == "__main__")"""
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                if (isinstance(node.test, ast.Compare) and
                    isinstance(node.test.left, ast.Name) and
                    node.test.left.id == "__name__" and
                    len(node.test.comparators) == 1 and
                    isinstance(node.test.comparators[0], ast.Constant) and
                    node.test.comparators[0].value == "__main__"):
                    
                    main_content = self._extract_source_code(node, content)
                    calls = self._extract_function_calls(node)
                    
                    return create_chunk(
                        chunk_type=ChunkType.MAIN_BLOCK,
                        name="__main__",
                        content=main_content,
                        file_path=file_path,
                        purpose="Entry point when run as script",
                        calls=calls
                    )
        
        return None
    
    def _extract_source_code(self, node: ast.AST, content: str) -> str:
        """Extract source code for a node"""
        try:
            # This is a simplified approach - in practice, you'd want more robust source extraction
            lines = content.split('\n')
            start_line = node.lineno - 1
            end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 1
            
            return '\n'.join(lines[start_line:end_line])
        except:
            return f"# {type(node).__name__} at line {getattr(node, 'lineno', 'unknown')}"
    
    def _extract_docstring(self, node: ast.AST) -> Optional[str]:
        """Extract docstring from a node"""
        if (isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)) and
            node.body and
            isinstance(node.body[0], ast.Expr) and
            isinstance(node.body[0].value, ast.Constant) and
            isinstance(node.body[0].value.value, str)):
            return node.body[0].value.value.strip()
        return None
    
    def _is_method(self, node: ast.FunctionDef) -> bool:
        """Check if function is a method (inside a class)"""
        for parent in ast.walk(node):
            if isinstance(parent, ast.ClassDef):
                for item in parent.body:
                    if item == node:
                        return True
        return False
    
    def _extract_function_calls(self, node: ast.AST) -> List[str]:
        """Extract function calls from a node"""
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.append(child.func.attr)
        return calls
    
    def _generate_package_chunks(self):
        """Generate package-level chunks for directories"""
        # Get all unique package paths
        package_paths = set()
        for chunk in self.chunks:
            file_path = chunk['metadata']['file_path']
            package_path = str(Path(file_path).parent)
            if package_path != '.':
                package_paths.add(package_path)
        
        # Create package chunks
        for package_path in sorted(package_paths):
            package_chunk = self._create_package_chunk(package_path)
            if package_chunk:
                self.chunks.append(package_chunk)
    
    def _create_package_chunk(self, package_path: str) -> Optional[Dict[str, Any]]:
        """Create a package chunk for a directory"""
        # Find all files in this package
        package_files = []
        package_chunks = []
        
        for chunk in self.chunks:
            if chunk['metadata']['file_path'].startswith(package_path):
                package_files.append(chunk['metadata']['file_path'])
                package_chunks.append(chunk)
        
        if not package_files:
            return None
        
        # Analyze package content
        package_name = package_path.replace('/', '.')
        purpose = self._determine_package_purpose(package_chunks)
        features = self._extract_package_features(package_chunks)
        
        # Create package content
        content = f"Package: {package_name}\n"
        content += f"Purpose: {purpose}\n\n"
        content += f"Contains {len(package_files)} files:\n"
        
        for file_path in sorted(package_files):
            filename = Path(file_path).name
            content += f"- {filename}\n"
        
        if features:
            content += f"\nFeatures:\n"
            for feature in features:
                content += f"- {feature}\n"
        
        return create_chunk(
            chunk_type=ChunkType.PACKAGE,
            name=package_name,
            content=content,
            file_path=package_path,
            purpose=purpose,
            file_count=len(package_files),
            files=[Path(f).name for f in package_files],
            features=features
        )
    
    def _determine_package_purpose(self, chunks: List[Dict[str, Any]]) -> str:
        """Determine package purpose from its chunks"""
        purposes = {
            'api': 'API endpoints and HTTP handling',
            'models': 'Database models and data structures',
            'schemas': 'Data validation and serialization',
            'services': 'Business logic and external integrations',
            'utils': 'Utility functions and helpers',
            'core': 'Core application configuration',
            'tests': 'Test files and test utilities'
        }
        
        for chunk in chunks:
            file_path = chunk['metadata']['file_path']
            for key, purpose in purposes.items():
                if key in file_path.lower():
                    return purpose
        
        return "Package functionality"
    
    def _extract_package_features(self, chunks: List[Dict[str, Any]]) -> List[str]:
        """Extract features from package chunks"""
        features = set()
        
        for chunk in chunks:
            chunk_type = chunk['type']
            if chunk_type == 'class':
                features.add(f"Classes: {chunk['name']}")
            elif chunk_type == 'function':
                features.add(f"Functions: {chunk['name']}")
            elif chunk_type == 'method':
                features.add(f"Methods: {chunk['name']}")
        
        return list(features)
    
    def save_chunks(self, output_path: str):
        """Save chunks to JSON file"""
        import json
        
        # Convert ChunkType enums to strings for JSON serialization
        def convert_chunk_types(obj):
            if isinstance(obj, dict):
                return {k: convert_chunk_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_chunk_types(item) for item in obj]
            elif hasattr(obj, 'value'):  # ChunkType enum
                return obj.value
            else:
                return obj
        
        # Convert chunks and relationships
        converted_chunks = convert_chunk_types(self.chunks)
        converted_relationships = convert_chunk_types(self.relationships)
        
        output_data = {
            "chunks": converted_chunks,
            "relationships": converted_relationships,
            "total_chunks": len(self.chunks),
            "total_relationships": len(self.relationships)
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(self.chunks)} chunks and {len(self.relationships)} relationships to {output_path}")
    
    def print_summary(self):
        """Print chunking summary"""
        print(f"\n=== Code Chunking Summary ===")
        print(f"Total chunks: {len(self.chunks)}")
        print(f"Total relationships: {len(self.relationships)}")
        
        # Count by type
        type_counts = {}
        for chunk in self.chunks:
            chunk_type = chunk['type']
            type_counts[chunk_type] = type_counts.get(chunk_type, 0) + 1
        
        print(f"\nChunks by type:")
        for chunk_type, count in sorted(type_counts.items()):
            print(f"  {chunk_type}: {count}")
        
        # Show some examples
        print(f"\nExample chunks:")
        for i, chunk in enumerate(self.chunks[:5]):
            print(f"  {i+1}. {chunk['type']}: {chunk['name']} ({chunk['metadata']['file_path']})")
