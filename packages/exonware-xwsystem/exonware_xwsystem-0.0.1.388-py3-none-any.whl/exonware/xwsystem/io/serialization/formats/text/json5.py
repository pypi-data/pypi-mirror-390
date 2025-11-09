#!/usr/bin/env python3
#exonware/xwsystem/src/exonware/xwsystem/io/serialization/formats/text/json5.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.388
Generation Date: 02-Nov-2025

JSON5 Serialization - Extended JSON with Comments and Trailing Commas

JSON5 is a superset of JSON that allows:
- Comments (// and /* */)
- Trailing commas
- Single quotes
- Unquoted keys
- More lenient syntax

Priority 1 (Security): Safe JSON5 parsing with validation
Priority 2 (Usability): Human-friendly JSON with comments
Priority 3 (Maintainability): Extends JSON serialization cleanly
Priority 4 (Performance): Efficient parsing via json5 library
Priority 5 (Extensibility): Compatible with standard JSON
"""

from typing import Any, Dict, Optional, Union
from pathlib import Path

try:
    import json5
except ImportError:
    json5 = None

from ...base import ASerialization
from ...contracts import ISerialization


class XWJson5Serializer(ASerialization):
    """
    JSON5 serializer with comment support.
    
    I: ISerialization (interface)
    A: ASerialization (abstract base)
    XW: XWJson5Serializer (concrete implementation)
    """
    
    def __init__(self):
        """Initialize JSON5 serializer."""
        super().__init__()
        if json5 is None:
            raise ImportError("json5 library required. Install with: pip install json5")
    
    @property
    def codec_id(self) -> str:
        """Codec identifier."""
        return "json5"
    
    @property
    def media_types(self) -> list[str]:
        """Supported MIME types."""
        return ["application/json5", "application/json"]
    
    @property
    def file_extensions(self) -> list[str]:
        """Supported file extensions."""
        return [".json5", ".json"]
    
    @property
    def aliases(self) -> list[str]:
        """Alternative names."""
        return ["json5", "JSON5"]
    
    @property
    def codec_types(self) -> list[str]:
        """JSON5 is a serialization and config format (supports comments)."""
        return ["serialization", "config"]
    
    def encode(self, data: Any, options: Optional[Dict[str, Any]] = None) -> str:
        """
        Encode data to JSON5 string.
        
        Args:
            data: Data to encode
            options: Encoding options (indent, etc.)
            
        Returns:
            JSON5 string
        """
        opts = options or {}
        indent = opts.get('indent', 2)
        
        # json5 uses same API as json but with extended syntax support
        return json5.dumps(data, indent=indent)
    
    def decode(self, data: Union[str, bytes], options: Optional[Dict[str, Any]] = None) -> Any:
        """
        Decode JSON5 string to Python data.
        
        Args:
            data: JSON5 string or bytes
            options: Decoding options
            
        Returns:
            Decoded Python data
        """
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        
        return json5.loads(data)


# Backward compatibility alias
Json5Serializer = XWJson5Serializer

