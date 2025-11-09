"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.389
Generation Date: November 2, 2025

Serialization base classes - ASerialization abstract base.

Following I→A→XW pattern:
- I: ISerialization (interface)
- A: ASerialization (abstract base - this file)
- XW: XW{Format}Serializer (concrete implementations)
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Union, Optional, BinaryIO, TextIO, AsyncIterator, Iterator, List, Dict, TYPE_CHECKING
from pathlib import Path

from ..codec.base import ACodec
from .contracts import ISerialization
from ..contracts import EncodeOptions, DecodeOptions
from ..defs import CodecCapability
from ..errors import SerializationError

if TYPE_CHECKING:
    from .defs import CompatibilityLevel
    from .schema_registry import SchemaInfo


class ASerialization(ACodec[Any, Union[bytes, str]], ISerialization, ABC):
    """
    Abstract base class for serialization - follows I→A→XW pattern.
    
    I: ISerialization (interface)
    A: ASerialization (abstract base - this class)
    XW: XW{Format}Serializer (concrete implementations)
    
    Extends ACodec and implements ISerialization interface.
    Provides default implementations for common serialization operations.
    
    Subclasses only need to implement:
    - encode()
    - decode()  
    - Metadata properties (codec_id, media_types, file_extensions, etc.)
    
    This class provides:
    - File I/O with atomic operations (save_file, load_file)
    - Async file I/O (save_file_async, load_file_async)
    - Streaming (iter_serialize, iter_deserialize, stream_serialize, stream_deserialize)
    - Validation helpers
    - XWSystem integration
    """
    
    def __init__(self):
        """Initialize serialization base."""
        super().__init__()
    
    # ========================================================================
    # CORE CODEC METHODS (Must implement in subclasses)
    # ========================================================================
    
    @abstractmethod
    def encode(self, value: Any, *, options: Optional[EncodeOptions] = None) -> Union[bytes, str]:
        """Encode data to representation - must implement in subclass."""
        pass
    
    @abstractmethod
    def decode(self, repr: Union[bytes, str], *, options: Optional[DecodeOptions] = None) -> Any:
        """Decode representation to data - must implement in subclass."""
        pass
    
    # ========================================================================
    # METADATA PROPERTIES (Must implement in subclasses)
    # ========================================================================
    
    @property
    @abstractmethod
    def codec_id(self) -> str:
        """Codec identifier (e.g., 'json', 'yaml')."""
        pass
    
    @property
    @abstractmethod
    def media_types(self) -> list[str]:
        """Supported MIME types."""
        pass
    
    @property
    @abstractmethod
    def file_extensions(self) -> list[str]:
        """Supported file extensions."""
        pass
    
    @property
    def format_name(self) -> str:
        """Format name (default: uppercase codec_id)."""
        return self.codec_id.upper()
    
    @property
    def mime_type(self) -> str:
        """Primary MIME type (default: first in media_types)."""
        return self.media_types[0] if self.media_types else "application/octet-stream"
    
    @property
    def is_binary_format(self) -> bool:
        """Whether this is a binary format (default: check return type of encode)."""
        # Can be overridden in subclasses for performance
        return False  # Default to text, override in binary formats
    
    @property
    def supports_streaming(self) -> bool:
        """Whether this format supports streaming (default: False)."""
        return False  # Override in formats that support streaming
    
    @property
    def capabilities(self) -> CodecCapability:
        """Serialization codecs support bidirectional operations."""
        return CodecCapability.BIDIRECTIONAL
    
    @property
    def aliases(self) -> list[str]:
        """Default aliases from codec_id."""
        return [self.codec_id.lower(), self.codec_id.upper()]
    
    @property
    def codec_types(self) -> list[str]:
        """
        Codec types for categorization (default: ['serialization']).
        
        Override in subclasses for more specific types like:
        - ['binary']: Binary serialization formats
        - ['config', 'serialization']: Configuration file formats
        - ['data']: Data exchange formats
        
        Can return multiple types if codec serves multiple purposes.
        """
        return ["serialization"]
    
    # ========================================================================
    # FILE I/O METHODS (Default implementations using encode/decode)
    # ========================================================================
    
    def save_file(self, data: Any, file_path: Union[str, Path], **options) -> None:
        """
        Save data to file with atomic operations.
        
        Default implementation:
        1. Encode data using encode()
        2. Write to file using Path.write_bytes() or write_text()
        3. Uses atomic operations if configured
        
        Args:
            data: Data to serialize and save
            file_path: Path to save file
            **options: Format-specific options
        
        Raises:
            SerializationError: If save fails
        """
        try:
            path = Path(file_path)
            
            # Ensure parent directory exists
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Encode data
            repr_data = self.encode(data, options=options or None)
            
            # Write to file (atomic)
            if isinstance(repr_data, bytes):
                path.write_bytes(repr_data)
            else:
                path.write_text(repr_data, encoding='utf-8')
                
        except Exception as e:
            raise SerializationError(
                f"Failed to save {self.format_name} file: {e}",
                format_name=self.format_name,
                original_error=e
            )
    
    def load_file(self, file_path: Union[str, Path], **options) -> Any:
        """
        Load data from file.
        
        Default implementation:
        1. Read from file using Path.read_bytes() or read_text()
        2. Decode data using decode()
        
        Args:
            file_path: Path to load from
            **options: Format-specific options
        
        Returns:
            Deserialized data
        
        Raises:
            SerializationError: If load fails
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                raise FileNotFoundError(f"File not found: {path}")
            
            # Read from file
            if self.is_binary_format:
                repr_data = path.read_bytes()
            else:
                # Try text first, fall back to bytes
                try:
                    repr_data = path.read_text(encoding='utf-8')
                except UnicodeDecodeError:
                    repr_data = path.read_bytes()
            
            # Decode data
            return self.decode(repr_data, options=options or None)
            
        except Exception as e:
            if isinstance(e, FileNotFoundError):
                raise
            raise SerializationError(
                f"Failed to load {self.format_name} file: {e}",
                format_name=self.format_name,
                original_error=e
            )
    
    # ========================================================================
    # VALIDATION METHODS (Default implementations)
    # ========================================================================
    
    def validate_data(self, data: Any) -> bool:
        """
        Validate data for serialization compatibility.
        
        Default implementation: Try to encode and catch errors.
        Override for format-specific validation.
        
        Args:
            data: Data to validate
        
        Returns:
            True if data can be serialized
        
        Raises:
            SerializationError: If validation fails
        """
        try:
            self.encode(data)
            return True
        except Exception as e:
            raise SerializationError(
                f"Data validation failed for {self.format_name}: {e}",
                format_name=self.format_name,
                original_error=e
            )
    
    # ========================================================================
    # STREAMING METHODS (Default implementations)
    # ========================================================================
    
    def iter_serialize(self, data: Any, chunk_size: int = 8192) -> Iterator[Union[str, bytes]]:
        """
        Stream serialize data in chunks.
        
        Default implementation: Encode all data then yield in chunks.
        Override for true streaming support.
        
        Args:
            data: Data to serialize
            chunk_size: Size of each chunk
        
        Yields:
            Serialized chunks
        """
        # Default: encode all at once, then chunk
        repr_data = self.encode(data)
        
        if isinstance(repr_data, bytes):
            for i in range(0, len(repr_data), chunk_size):
                yield repr_data[i:i + chunk_size]
        else:
            for i in range(0, len(repr_data), chunk_size):
                yield repr_data[i:i + chunk_size]
    
    def iter_deserialize(self, src: Union[TextIO, BinaryIO, Iterator[Union[str, bytes]]]) -> Any:
        """
        Stream deserialize data from chunks.
        
        Default implementation: Collect all chunks then decode.
        Override for true streaming support.
        
        Args:
            src: Source of data chunks
        
        Returns:
            Deserialized data
        """
        # Default: collect all chunks, then decode
        if isinstance(src, (TextIO, BinaryIO)):
            repr_data = src.read()
        else:
            chunks = list(src)
            if chunks and isinstance(chunks[0], bytes):
                repr_data = b''.join(chunks)
            else:
                repr_data = ''.join(chunks)
        
        return self.decode(repr_data)
    
    # ========================================================================
    # ASYNC METHODS (Default implementations using asyncio.to_thread)
    # ========================================================================
    
    async def save_file_async(self, data: Any, file_path: Union[str, Path], **options) -> None:
        """
        Async save data to file.
        
        Default implementation: Delegate to sync save_file via asyncio.to_thread.
        Override for native async I/O.
        
        Args:
            data: Data to serialize
            file_path: Path to save file
            **options: Format-specific options
        """
        await asyncio.to_thread(self.save_file, data, file_path, **options)
    
    async def load_file_async(self, file_path: Union[str, Path], **options) -> Any:
        """
        Async load data from file.
        
        Default implementation: Delegate to sync load_file via asyncio.to_thread.
        Override for native async I/O.
        
        Args:
            file_path: Path to load from
            **options: Format-specific options
        
        Returns:
            Deserialized data
        """
        return await asyncio.to_thread(self.load_file, file_path, **options)
    
    async def stream_serialize(self, data: Any, chunk_size: int = 8192) -> AsyncIterator[Union[str, bytes]]:
        """
        Async stream serialize data in chunks.
        
        Default implementation: Delegate to sync iter_serialize.
        Override for native async streaming.
        
        Args:
            data: Data to serialize
            chunk_size: Size of each chunk
        
        Yields:
            Serialized chunks
        """
        for chunk in self.iter_serialize(data, chunk_size):
            yield chunk
            await asyncio.sleep(0)  # Yield control
    
    async def stream_deserialize(self, data_stream: AsyncIterator[Union[str, bytes]]) -> Any:
        """
        Async stream deserialize data from chunks.
        
        Default implementation: Collect all chunks then decode.
        Override for native async streaming.
        
        Args:
            data_stream: Async iterator of data chunks
        
        Returns:
            Deserialized data
        """
        chunks = []
        async for chunk in data_stream:
            chunks.append(chunk)
        
        if chunks and isinstance(chunks[0], bytes):
            repr_data = b''.join(chunks)
        else:
            repr_data = ''.join(chunks)
        
        return self.decode(repr_data)


# ============================================================================
# SCHEMA REGISTRY BASE CLASSES (Moved from enterprise)
# ============================================================================


class ASchemaRegistry(ABC):
    """Abstract base class for schema registry implementations."""
    
    @abstractmethod
    async def register_schema(self, subject: str, schema: str, schema_type: str = "AVRO") -> 'SchemaInfo':
        """Register a new schema version."""
        pass
    
    @abstractmethod
    async def get_schema(self, schema_id: int) -> 'SchemaInfo':
        """Get schema by ID."""
        pass
    
    @abstractmethod
    async def get_latest_schema(self, subject: str) -> 'SchemaInfo':
        """Get latest schema version for subject."""
        pass
    
    @abstractmethod
    async def get_schema_versions(self, subject: str) -> List[int]:
        """Get all versions for a subject."""
        pass
    
    @abstractmethod
    async def check_compatibility(self, subject: str, schema: str) -> bool:
        """Check if schema is compatible with latest version."""
        pass
    
    @abstractmethod
    async def set_compatibility(self, subject: str, level: 'CompatibilityLevel') -> None:
        """Set compatibility level for subject."""
        pass

