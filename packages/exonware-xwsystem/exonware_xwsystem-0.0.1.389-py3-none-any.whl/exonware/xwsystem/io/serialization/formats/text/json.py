"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.389
Generation Date: November 2, 2025

JSON serialization - Universal, human-readable data interchange format.

Following I→A→XW pattern:
- I: ISerialization (interface)
- A: ASerialization (abstract base)
- XW: XWJsonSerializer (concrete implementation)
"""

import json
from typing import Any, Optional, Union
from pathlib import Path

from ...base import ASerialization
from ....contracts import EncodeOptions, DecodeOptions
from ....defs import CodecCapability
from ....errors import SerializationError


class XWJsonSerializer(ASerialization):
    """
    JSON serializer - follows I→A→XW pattern.
    
    I: ISerialization (interface)
    A: ASerialization (abstract base)
    XW: XWJsonSerializer (concrete implementation)
    
    Uses Python's built-in `json` library for reliable JSON handling.
    
    Examples:
        >>> serializer = XWJsonSerializer()
        >>> 
        >>> # Encode data
        >>> json_str = serializer.encode({"key": "value"})
        >>> # b'{"key": "value"}'
        >>> 
        >>> # Decode data
        >>> data = serializer.decode(b'{"key": "value"}')
        >>> # {'key': 'value'}
        >>> 
        >>> # Save to file
        >>> serializer.save_file({"name": "John"}, "user.json")
        >>> 
        >>> # Load from file
        >>> user = serializer.load_file("user.json")
    """
    
    # ========================================================================
    # CODEC METADATA
    # ========================================================================
    
    @property
    def codec_id(self) -> str:
        return "json"
    
    @property
    def media_types(self) -> list[str]:
        return ["application/json", "text/json"]
    
    @property
    def file_extensions(self) -> list[str]:
        return [".json", ".webmanifest", ".mcmeta", ".geojson", ".topojson"]
    
    @property
    def format_name(self) -> str:
        return "JSON"
    
    @property
    def mime_type(self) -> str:
        return "application/json"
    
    @property
    def is_binary_format(self) -> bool:
        return False  # JSON is text-based
    
    @property
    def supports_streaming(self) -> bool:
        return False  # Standard JSON doesn't support streaming
    
    @property
    def capabilities(self) -> CodecCapability:
        return CodecCapability.BIDIRECTIONAL
    
    @property
    def aliases(self) -> list[str]:
        return ["json", "JSON"]
    
    # ========================================================================
    # CORE ENCODE/DECODE (Using official json library)
    # ========================================================================
    
    def encode(self, value: Any, *, options: Optional[EncodeOptions] = None) -> Union[bytes, str]:
        """
        Encode data to JSON string.
        
        Uses Python's built-in json.dumps().
        
        Args:
            value: Data to serialize
            options: JSON options (indent, sort_keys, ensure_ascii, etc.)
        
        Returns:
            JSON string (as text, not bytes for compatibility)
        
        Raises:
            SerializationError: If encoding fails
        """
        try:
            opts = options or {}
            
            # Common JSON options
            indent = opts.get('indent', opts.get('pretty', None))
            if indent is True:
                indent = 2
            
            sort_keys = opts.get('sort_keys', False)
            ensure_ascii = opts.get('ensure_ascii', False)
            
            # Encode to JSON string
            json_str = json.dumps(
                value,
                indent=indent,
                sort_keys=sort_keys,
                ensure_ascii=ensure_ascii,
                default=opts.get('default', None),
                cls=opts.get('cls', None)
            )
            
            return json_str
            
        except (TypeError, ValueError, OverflowError) as e:
            raise SerializationError(
                f"Failed to encode JSON: {e}",
                format_name=self.format_name,
                original_error=e
            )
    
    def decode(self, repr: Union[bytes, str], *, options: Optional[DecodeOptions] = None) -> Any:
        """
        Decode JSON string to data.
        
        Uses Python's built-in json.loads().
        
        Args:
            repr: JSON string (bytes or str)
            options: JSON options (object_hook, parse_float, etc.)
        
        Returns:
            Decoded Python object
        
        Raises:
            SerializationError: If decoding fails
        """
        try:
            # Convert bytes to str if needed
            if isinstance(repr, bytes):
                repr = repr.decode('utf-8')
            
            opts = options or {}
            
            # Decode from JSON string
            data = json.loads(
                repr,
                object_hook=opts.get('object_hook', None),
                parse_float=opts.get('parse_float', None),
                parse_int=opts.get('parse_int', None),
                parse_constant=opts.get('parse_constant', None),
                cls=opts.get('cls', None)
            )
            
            return data
            
        except (json.JSONDecodeError, ValueError, UnicodeDecodeError) as e:
            raise SerializationError(
                f"Failed to decode JSON: {e}",
                format_name=self.format_name,
                original_error=e
            )


# Backward compatibility alias
JsonSerializer = XWJsonSerializer

