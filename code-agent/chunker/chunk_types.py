"""
Chunk type definitions and metadata schemas
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


class ChunkType(Enum):
    """Types of code chunks"""
    PACKAGE = "package"
    CLASS = "class"
    METHOD = "method"
    FUNCTION = "function"
    IMPORTS = "imports"
    CONSTANTS = "constants"
    MAIN_BLOCK = "main_block"


@dataclass
class ChunkMetadata:
    """Base metadata for all chunks"""
    file_path: str
    chunk_type: ChunkType
    name: str
    purpose: str
    dependencies: List[str] = None
    access_level: str = "public"
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class PackageMetadata(ChunkMetadata):
    """Metadata for package chunks"""
    file_count: int = 0
    files: List[str] = None
    subpackages: List[str] = None
    api_routes: List[str] = None
    database_tables: List[str] = None
    features: List[str] = None
    
    def __post_init__(self):
        super().__post_init__()
        if self.files is None:
            self.files = []
        if self.subpackages is None:
            self.subpackages = []
        if self.api_routes is None:
            self.api_routes = []
        if self.database_tables is None:
            self.database_tables = []
        if self.features is None:
            self.features = []


@dataclass
class ClassMetadata(ChunkMetadata):
    """Metadata for class chunks"""
    class_name: str = ""
    methods: List[str] = None
    attributes: List[str] = None
    base_classes: List[str] = None
    decorators: List[str] = None
    
    def __post_init__(self):
        super().__post_init__()
        if self.methods is None:
            self.methods = []
        if self.attributes is None:
            self.attributes = []
        if self.base_classes is None:
            self.base_classes = []
        if self.decorators is None:
            self.decorators = []


@dataclass
class MethodMetadata(ChunkMetadata):
    """Metadata for method chunks"""
    class_name: str = ""
    method_name: str = ""
    parameters: List[str] = None
    return_type: str = ""
    access: str = "public"
    decorators: List[str] = None
    is_async: bool = False
    is_static: bool = False
    is_classmethod: bool = False
    
    def __post_init__(self):
        super().__post_init__()
        if self.parameters is None:
            self.parameters = []
        if self.decorators is None:
            self.decorators = []


@dataclass
class FunctionMetadata(ChunkMetadata):
    """Metadata for function chunks"""
    function_name: str = ""
    parameters: List[str] = None
    return_type: str = ""
    decorators: List[str] = None
    is_async: bool = False
    
    def __post_init__(self):
        super().__post_init__()
        if self.parameters is None:
            self.parameters = []
        if self.decorators is None:
            self.decorators = []


@dataclass
class ImportsMetadata(ChunkMetadata):
    """Metadata for imports chunks"""
    imports: List[Dict[str, str]] = None  # [{"module": "fastapi", "type": "third_party", "items": ["FastAPI"]}]
    
    def __post_init__(self):
        super().__post_init__()
        if self.imports is None:
            self.imports = []


@dataclass
class ConstantsMetadata(ChunkMetadata):
    """Metadata for constants chunks"""
    constant_name: str = ""
    constant_type: str = ""
    usage: str = ""
    constants: List[Dict[str, str]] = None
    
    def __post_init__(self):
        super().__post_init__()
        if self.constants is None:
            self.constants = []


@dataclass
class MainBlockMetadata(ChunkMetadata):
    """Metadata for main block chunks"""
    calls: List[str] = None
    
    def __post_init__(self):
        super().__post_init__()
        if self.calls is None:
            self.calls = []


def create_chunk(
    chunk_type: ChunkType,
    name: str,
    content: str,
    file_path: str,
    purpose: str,
    **kwargs
) -> Dict[str, Any]:
    """Create a chunk dictionary with proper metadata"""
    
    # Create appropriate metadata based on chunk type
    if chunk_type == ChunkType.PACKAGE:
        metadata = PackageMetadata(
            file_path=file_path,
            chunk_type=chunk_type,
            name=name,
            purpose=purpose,
            **kwargs
        )
    elif chunk_type == ChunkType.CLASS:
        metadata = ClassMetadata(
            file_path=file_path,
            chunk_type=chunk_type,
            name=name,
            purpose=purpose,
            **kwargs
        )
    elif chunk_type == ChunkType.METHOD:
        metadata = MethodMetadata(
            file_path=file_path,
            chunk_type=chunk_type,
            name=name,
            purpose=purpose,
            **kwargs
        )
    elif chunk_type == ChunkType.FUNCTION:
        metadata = FunctionMetadata(
            file_path=file_path,
            chunk_type=chunk_type,
            name=name,
            purpose=purpose,
            **kwargs
        )
    elif chunk_type == ChunkType.IMPORTS:
        metadata = ImportsMetadata(
            file_path=file_path,
            chunk_type=chunk_type,
            name=name,
            purpose=purpose,
            **kwargs
        )
    elif chunk_type == ChunkType.CONSTANTS:
        metadata = ConstantsMetadata(
            file_path=file_path,
            chunk_type=chunk_type,
            name=name,
            purpose=purpose,
            **kwargs
        )
    elif chunk_type == ChunkType.MAIN_BLOCK:
        metadata = MainBlockMetadata(
            file_path=file_path,
            chunk_type=chunk_type,
            name=name,
            purpose=purpose,
            **kwargs
        )
    else:
        metadata = ChunkMetadata(
            file_path=file_path,
            chunk_type=chunk_type,
            name=name,
            purpose=purpose,
            **kwargs
        )
    
    return {
        "type": chunk_type.value,
        "name": name,
        "content": content,
        "metadata": metadata.__dict__
    }
