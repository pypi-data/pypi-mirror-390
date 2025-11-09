#!/usr/bin/env python3
# exonware/xwsystem/io/codec/base.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.388
Generation Date: October 30, 2025

Base classes, registry, adapters, and helper functions for codec system.
"""

from __future__ import annotations
from typing import TypeVar, Generic, Optional, Dict, Any, Type, IO
from pathlib import Path
from dataclasses import dataclass
from abc import ABC, abstractmethod
import mimetypes

from .contracts import ICodec, ICodecMetadata
from ..contracts import Serializer, Formatter, EncodeOptions, DecodeOptions
from ..defs import CodecCapability
from ..errors import EncodeError, DecodeError, CodecNotFoundError, CodecRegistrationError

__all__ = [
    'ACodec',
    'MediaKey',
    'CodecRegistry',
    'get_global_registry',
    'FormatterToSerializer',
    'SerializerToFormatter',
]

T = TypeVar("T")
R = TypeVar("R")


# ============================================================================
# MEDIA KEY
# ============================================================================

@dataclass(frozen=True)
class MediaKey:
    """
    Media type key for codec lookup (RFC 2046 compliant).
    
    Attributes:
        type: Media type string (e.g., "application/json")
    
    Examples:
        >>> MediaKey("application/json")
        >>> MediaKey("application/sql")
        >>> MediaKey("text/x-python")
    """
    
    type: str
    
    def __post_init__(self):
        # Normalize to lowercase
        object.__setattr__(self, 'type', self.type.lower())
    
    def __str__(self) -> str:
        return self.type
    
    @classmethod
    def from_extension(cls, ext: str) -> Optional[MediaKey]:
        """
        Create MediaKey from file extension.
        
        Args:
            ext: File extension (with or without dot)
        
        Returns:
            MediaKey if extension is recognized, None otherwise
        
        Examples:
            >>> MediaKey.from_extension('.json')
            MediaKey(type='application/json')
            
            >>> MediaKey.from_extension('sql')
            MediaKey(type='application/sql')
        """
        if not ext.startswith('.'):
            ext = f'.{ext}'
        
        mime_type = mimetypes.guess_type(f'file{ext}')[0]
        return cls(mime_type) if mime_type else None


# ============================================================================
# CODEC REGISTRY
# ============================================================================

class CodecRegistry:
    """
    Global codec registry with media-type based lookup.
    
    NO HARDCODING - codecs self-register with their metadata!
    
    Lookup strategies:
        1. Media type (primary): get(MediaKey("application/json"))
        2. File extension (convenience): get_by_extension(".json")
        3. Codec ID / alias (direct): get_by_id("json")
    
    Examples:
        >>> registry = CodecRegistry()
        >>> registry.register(JsonCodec)
        >>> 
        >>> codec = registry.get(MediaKey("application/json"))
        >>> codec = registry.get_by_extension('.json')
        >>> codec = registry.get_by_id('json')
    """
    
    def __init__(self) -> None:
        self._by_media_type: Dict[MediaKey, Type[ICodec]] = {}
        self._by_extension: Dict[str, Type[ICodec]] = {}
        self._by_id: Dict[str, Type[ICodec]] = {}
        self._instances: Dict[str, ICodec] = {}  # Cached instances
    
    def register(self, codec_class: Type[ICodec]) -> None:
        """
        Register a codec class.
        
        The codec must implement ICodecMetadata protocol to provide:
        - codec_id
        - media_types
        - file_extensions
        - aliases
        
        Args:
            codec_class: Codec class to register
        
        Raises:
            CodecRegistrationError: If codec doesn't implement ICodecMetadata
        
        Examples:
            >>> registry.register(JsonCodec)
            >>> registry.register(SqlFormatter)
        """
        # Create instance to read metadata
        try:
            instance = codec_class()
        except Exception as e:
            raise CodecRegistrationError(
                f"Failed to instantiate {codec_class.__name__}: {e}"
            ) from e
        
        # Verify it has metadata
        if not hasattr(instance, 'codec_id'):
            raise CodecRegistrationError(
                f"{codec_class.__name__} must implement ICodecMetadata protocol "
                f"(missing 'codec_id' property)"
            )
        
        codec_id = instance.codec_id
        
        # Register by media types
        if hasattr(instance, 'media_types'):
            for media_type in instance.media_types:
                key = MediaKey(media_type)
                self._by_media_type[key] = codec_class
        
        # Register by extensions
        if hasattr(instance, 'file_extensions'):
            for ext in instance.file_extensions:
                if not ext.startswith('.'):
                    ext = f'.{ext}'
                self._by_extension[ext.lower()] = codec_class
        
        # Register by ID and aliases
        self._by_id[codec_id.lower()] = codec_class
        if hasattr(instance, 'aliases'):
            for alias in instance.aliases:
                self._by_id[alias.lower()] = codec_class
    
    def get(self, key: MediaKey) -> Optional[ICodec]:
        """
        Get codec by media type key.
        
        Args:
            key: Media type key
        
        Returns:
            Codec instance (cached) or None if not found
        
        Examples:
            >>> codec = registry.get(MediaKey("application/json"))
            >>> codec.encode({"key": "value"})
        """
        codec_class = self._by_media_type.get(key)
        if not codec_class:
            return None
        
        # Return cached instance
        codec_id = codec_class().codec_id
        if codec_id not in self._instances:
            self._instances[codec_id] = codec_class()
        
        return self._instances[codec_id]
    
    def get_by_extension(self, ext: str) -> Optional[ICodec]:
        """
        Get codec by file extension.
        
        Args:
            ext: File extension (with or without dot) or file path
        
        Returns:
            Codec instance or None
        
        Examples:
            >>> codec = registry.get_by_extension('.json')
            >>> codec = registry.get_by_extension('sql')
            >>> codec = registry.get_by_extension('data.json')  # Extracts .json
        """
        # Extract extension if full path given
        path_obj = Path(ext)
        if path_obj.suffix:
            ext = path_obj.suffix
        
        if not ext.startswith('.'):
            ext = f'.{ext}'
        
        codec_class = self._by_extension.get(ext.lower())
        if not codec_class:
            return None
        
        codec_id = codec_class().codec_id
        if codec_id not in self._instances:
            self._instances[codec_id] = codec_class()
        
        return self._instances[codec_id]
    
    def get_by_id(self, codec_id: str) -> Optional[ICodec]:
        """
        Get codec by ID or alias.
        
        Args:
            codec_id: Codec identifier or alias (case-insensitive)
        
        Returns:
            Codec instance or None
        
        Examples:
            >>> codec = registry.get_by_id('json')
            >>> codec = registry.get_by_id('JSON')  # Case insensitive
        """
        codec_class = self._by_id.get(codec_id.lower())
        if not codec_class:
            return None
        
        actual_id = codec_class().codec_id
        if actual_id not in self._instances:
            self._instances[actual_id] = codec_class()
        
        return self._instances[actual_id]
    
    def list_media_types(self) -> list[str]:
        """List all registered media types."""
        return [str(k) for k in self._by_media_type.keys()]
    
    def list_extensions(self) -> list[str]:
        """List all registered file extensions."""
        return list(self._by_extension.keys())
    
    def list_codec_ids(self) -> list[str]:
        """List all registered codec IDs."""
        return [
            cls().codec_id 
            for cls in set(self._by_id.values())
        ]


# Global registry singleton
_global_registry: Optional[CodecRegistry] = None


def get_global_registry() -> CodecRegistry:
    """
    Get the global codec registry.
    
    Lazy-initializes on first access.
    
    Returns:
        Global CodecRegistry instance
    """
    global _global_registry
    
    if _global_registry is None:
        _global_registry = CodecRegistry()
    
    return _global_registry


# ============================================================================
# BASE CODEC CLASS WITH CONVENIENCE METHODS
# ============================================================================

class ACodec(Generic[T, R], ICodec[T, R], ICodecMetadata, ABC):
    """
    Base codec class with all convenience methods.
    
    Provides:
    - Core encode/decode (abstract - must implement)
    - All convenience aliases (dumps/loads/serialize/etc.)
    - File I/O helpers (save/load/export/import)
    - Stream operations (write/read)
    
    Subclasses only need to implement:
    - encode()
    - decode()
    - Metadata properties (codec_id, media_types, etc.)
    
    Example:
        >>> class JsonCodec(ACodec[dict, bytes]):
        ...     codec_id = "json"
        ...     media_types = ["application/json"]
        ...     file_extensions = [".json"]
        ...     aliases = ["JSON"]
        ...     
        ...     def encode(self, value, *, options=None):
        ...         return json.dumps(value).encode('utf-8')
        ...     
        ...     def decode(self, repr, *, options=None):
        ...         return json.loads(repr.decode('utf-8'))
        ...     
        ...     def capabilities(self):
        ...         return CodecCapability.BIDIRECTIONAL | CodecCapability.TEXT
    """
    
    # ========================================================================
    # CORE METHODS (Must implement in subclasses)
    # ========================================================================
    
    @abstractmethod
    def encode(self, value: T, *, options: Optional[EncodeOptions] = None) -> R:
        """Encode value to representation. Must implement."""
        pass
    
    @abstractmethod
    def decode(self, repr: R, *, options: Optional[DecodeOptions] = None) -> T:
        """Decode representation to value. Must implement."""
        pass
    
    # ========================================================================
    # METADATA PROPERTIES (Must implement in subclasses)
    # ========================================================================
    
    @property
    @abstractmethod
    def codec_id(self) -> str:
        """Unique codec identifier."""
        pass
    
    @property
    @abstractmethod
    def media_types(self) -> list[str]:
        """Supported media types."""
        pass
    
    @property
    @abstractmethod
    def file_extensions(self) -> list[str]:
        """Supported file extensions."""
        pass
    
    @property
    def aliases(self) -> list[str]:
        """Alternative names (default: [codec_id])."""
        return [self.codec_id.lower(), self.codec_id.upper()]
    
    @abstractmethod
    def capabilities(self) -> CodecCapability:
        """Supported capabilities."""
        pass
    
    # ========================================================================
    # CONVENIENCE ALIASES - Memory Operations
    # ========================================================================
    
    def dumps(self, value: T, **opts) -> R:
        """Alias for encode() - Python convention."""
        return self.encode(value, options=opts or None)
    
    def loads(self, repr: R, **opts) -> T:
        """Alias for decode() - Python convention."""
        return self.decode(repr, options=opts or None)
    
    def serialize(self, value: T, **opts) -> R:
        """Alias for encode() - explicit intent."""
        return self.encode(value, options=opts or None)
    
    def deserialize(self, repr: R, **opts) -> T:
        """Alias for decode() - explicit intent."""
        return self.decode(repr, options=opts or None)
    
    # ========================================================================
    # FILE OPERATIONS
    # ========================================================================
    
    def save(self, value: T, path: Path | str, **opts) -> None:
        """
        Encode and write to file.
        
        Args:
            value: Value to encode
            path: File path to write to
            **opts: Encoding options
        
        Example:
            >>> codec.save(data, "output.json")
        """
        path = Path(path)
        repr = self.encode(value, options=opts or None)
        
        if isinstance(repr, bytes):
            path.write_bytes(repr)
        else:
            path.write_text(repr, encoding='utf-8')
    
    def load(self, path: Path | str, **opts) -> T:
        """
        Read from file and decode.
        
        Args:
            path: File path to read from
            **opts: Decoding options
        
        Returns:
            Decoded value
        
        Example:
            >>> data = codec.load("input.json")
        """
        path = Path(path)
        
        # Try to guess if binary or text based on codec type
        # This is a heuristic - subclasses can override
        try:
            # Try binary first
            repr = path.read_bytes()
            if isinstance(self._get_repr_type_hint(), str):
                # Text codec, decode bytes to str
                repr = repr.decode('utf-8')
        except:
            # Fall back to text
            repr = path.read_text(encoding='utf-8')
        
        return self.decode(repr, options=opts or None)
    
    def export(self, value: T, path: Path | str, **opts) -> None:
        """Alias for save() - business terminology."""
        return self.save(value, path, **opts)
    
    def import_(self, path: Path | str, **opts) -> T:
        """Alias for load() - business terminology (_ for keyword)."""
        return self.load(path, **opts)
    
    def to_file(self, value: T, path: Path | str, **opts) -> None:
        """Alias for save() - explicit direction."""
        return self.save(value, path, **opts)
    
    def from_file(self, path: Path | str, **opts) -> T:
        """Alias for load() - explicit direction."""
        return self.load(path, **opts)
    
    def save_as(self, value: T, path: Path | str, format: Optional[str] = None, **opts) -> None:
        """
        Save with optional format hint.
        
        Args:
            value: Value to save
            path: File path
            format: Optional format hint (added to options)
            **opts: Other encoding options
        """
        if format:
            opts['format'] = format
        return self.save(value, path, **opts)
    
    def load_as(self, path: Path | str, format: Optional[str] = None, **opts) -> T:
        """
        Load with optional format hint.
        
        Args:
            path: File path
            format: Optional format hint (added to options)
            **opts: Other decoding options
        """
        if format:
            opts['format'] = format
        return self.load(path, **opts)
    
    # ========================================================================
    # STREAM OPERATIONS
    # ========================================================================
    
    def write(self, value: T, stream: IO, **opts) -> None:
        """
        Encode and write to stream.
        
        Args:
            value: Value to encode
            stream: IO stream to write to
            **opts: Encoding options
        
        Example:
            >>> with open("output.json", "wb") as f:
            ...     codec.write(data, f)
        """
        repr = self.encode(value, options=opts or None)
        stream.write(repr)
    
    def read(self, stream: IO, **opts) -> T:
        """
        Read from stream and decode.
        
        Args:
            stream: IO stream to read from
            **opts: Decoding options
        
        Returns:
            Decoded value
        
        Example:
            >>> with open("input.json", "rb") as f:
            ...     data = codec.read(f)
        """
        repr = stream.read()
        return self.decode(repr, options=opts or None)
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _get_repr_type_hint(self) -> type:
        """Get representation type hint (bytes or str) from class."""
        # Try to extract from __orig_bases__ or default to bytes
        return bytes  # Default, subclasses can override


# ============================================================================
# ADAPTERS (Bytes ↔ String)
# ============================================================================

class FormatterToSerializer(Generic[T]):
    """
    Adapter: Formatter[T, str] → Serializer[T, bytes].
    
    Wraps a string-based formatter to provide bytes interface via UTF-8 encoding.
    
    Use case: Language formatters (SQL, GraphQL) need to be saved to files
    as bytes, but work with strings internally.
    
    Example:
        >>> sql_formatter = SqlFormatter()  # Returns str
        >>> sql_serializer = FormatterToSerializer(sql_formatter)
        >>> bytes_data = sql_serializer.encode(query_ast)  # Returns bytes
        >>> with open('query.sql', 'wb') as f:
        ...     f.write(bytes_data)
    """
    
    def __init__(
        self, 
        formatter: Formatter[T, str], 
        encoding: str = "utf-8",
        errors: str = "strict"
    ) -> None:
        """
        Initialize adapter.
        
        Args:
            formatter: String formatter to wrap
            encoding: Text encoding (default: UTF-8)
            errors: Error handling strategy
        """
        self._formatter = formatter
        self._encoding = encoding
        self._errors = errors
    
    def encode(self, value: T, *, options: Optional[EncodeOptions] = None) -> bytes:
        """Encode to bytes via string."""
        text = self._formatter.encode(value, options=options)
        return text.encode(self._encoding, errors=self._errors)
    
    def decode(self, repr: bytes, *, options: Optional[DecodeOptions] = None) -> T:
        """Decode from bytes via string."""
        text = repr.decode(self._encoding, errors=self._errors)
        return self._formatter.decode(text, options=options)


class SerializerToFormatter(Generic[T]):
    """
    Adapter: Serializer[T, bytes] → Formatter[T, str].
    
    Wraps a bytes-based serializer to provide string interface via UTF-8 decoding.
    
    Use case: Text serializers (JSON, YAML) may work with bytes internally but
    need to provide string interface for templating/generation.
    
    Example:
        >>> json_serializer = JsonSerializer()  # Returns bytes
        >>> json_formatter = SerializerToFormatter(json_serializer)
        >>> text = json_formatter.encode({"key": "value"})  # Returns str
        >>> template = f"const data = {text};"
    """
    
    def __init__(
        self, 
        serializer: Serializer[T, bytes], 
        encoding: str = "utf-8",
        errors: str = "strict"
    ) -> None:
        """
        Initialize adapter.
        
        Args:
            serializer: Bytes serializer to wrap
            encoding: Text encoding (default: UTF-8)
            errors: Error handling strategy
        """
        self._serializer = serializer
        self._encoding = encoding
        self._errors = errors
    
    def encode(self, value: T, *, options: Optional[EncodeOptions] = None) -> str:
        """Encode to string via bytes."""
        data = self._serializer.encode(value, options=options)
        return data.decode(self._encoding, errors=self._errors)
    
    def decode(self, repr: str, *, options: Optional[DecodeOptions] = None) -> T:
        """Decode from string via bytes."""
        data = repr.encode(self._encoding, errors=self._errors)
        return self._serializer.decode(data, options=options)

