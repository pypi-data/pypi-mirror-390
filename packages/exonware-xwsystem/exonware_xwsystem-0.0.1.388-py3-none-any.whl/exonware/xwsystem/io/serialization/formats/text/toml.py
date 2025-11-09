"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.388
Generation Date: November 2, 2025

TOML serialization - Configuration file format.

Following I→A→XW pattern:
- I: ISerialization (interface)
- A: ASerialization (abstract base)
- XW: XWTomlSerializer (concrete implementation)
"""

import sys
from typing import Any, Optional, Union
from pathlib import Path

from ...base import ASerialization
from ....contracts import EncodeOptions, DecodeOptions
from ....defs import CodecCapability
from ....errors import SerializationError

# Python 3.11+ has tomllib built-in, earlier versions need tomli
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

# For writing TOML
try:
    import tomli_w
except ImportError:
    tomli_w = None


class XWTomlSerializer(ASerialization):
    """
    TOML serializer - follows I→A→XW pattern.
    
    I: ISerialization (interface)
    A: ASerialization (abstract base)
    XW: XWTomlSerializer (concrete implementation)
    
    Uses tomllib/tomli for reading and tomli_w for writing.
    
    Examples:
        >>> serializer = XWTomlSerializer()
        >>> 
        >>> # Encode data
        >>> toml_str = serializer.encode({"database": {"port": 5432}})
        >>> 
        >>> # Decode data
        >>> data = serializer.decode("[database]\\nport = 5432")
        >>> 
        >>> # Save to file
        >>> serializer.save_file({"tool": {"poetry": {}}}, "pyproject.toml")
        >>> 
        >>> # Load from file
        >>> config = serializer.load_file("pyproject.toml")
    """
    
    def __init__(self):
        """Initialize TOML serializer."""
        super().__init__()
        if tomllib is None:
            raise ImportError(
                "tomli is required for TOML deserialization. "
                "Install with: pip install tomli (Python <3.11)"
            )
        if tomli_w is None:
            raise ImportError(
                "tomli-w is required for TOML serialization. "
                "Install with: pip install tomli-w"
            )
    
    # ========================================================================
    # CODEC METADATA
    # ========================================================================
    
    @property
    def codec_id(self) -> str:
        return "toml"
    
    @property
    def media_types(self) -> list[str]:
        return ["application/toml", "text/toml"]
    
    @property
    def file_extensions(self) -> list[str]:
        return [".toml", ".tml"]
    
    @property
    def format_name(self) -> str:
        return "TOML"
    
    @property
    def mime_type(self) -> str:
        return "application/toml"
    
    @property
    def is_binary_format(self) -> bool:
        return False  # TOML is text-based
    
    @property
    def supports_streaming(self) -> bool:
        return False  # TOML doesn't support streaming
    
    @property
    def capabilities(self) -> CodecCapability:
        return CodecCapability.BIDIRECTIONAL
    
    @property
    def aliases(self) -> list[str]:
        return ["toml", "TOML"]
    
    @property
    def codec_types(self) -> list[str]:
        """TOML is both a configuration and serialization format."""
        return ["config", "serialization"]
    
    # ========================================================================
    # CORE ENCODE/DECODE (Using tomllib/tomli + tomli_w)
    # ========================================================================
    
    def encode(self, value: Any, *, options: Optional[EncodeOptions] = None) -> Union[bytes, str]:
        """
        Encode data to TOML string.
        
        Uses tomli_w.dumps().
        
        Args:
            value: Data to serialize (must be dict)
            options: TOML options (multiline_strings, etc.)
        
        Returns:
            TOML string
        
        Raises:
            SerializationError: If encoding fails
        """
        try:
            if not isinstance(value, dict):
                raise TypeError("TOML can only serialize dictionaries")
            
            opts = options or {}
            
            # Encode to TOML string
            toml_str = tomli_w.dumps(
                value,
                multiline_strings=opts.get('multiline_strings', False)
            )
            
            return toml_str
            
        except (TypeError, ValueError) as e:
            raise SerializationError(
                f"Failed to encode TOML: {e}",
                format_name=self.format_name,
                original_error=e
            )
    
    def decode(self, repr: Union[bytes, str], *, options: Optional[DecodeOptions] = None) -> Any:
        """
        Decode TOML string to data.
        
        Uses tomllib.loads() (Python 3.11+) or tomli.loads().
        
        Args:
            repr: TOML string (bytes or str)
            options: TOML options
        
        Returns:
            Decoded dictionary
        
        Raises:
            SerializationError: If decoding fails
        """
        try:
            # Convert bytes to str if needed
            if isinstance(repr, bytes):
                repr = repr.decode('utf-8')
            
            # Decode from TOML string
            data = tomllib.loads(repr)
            
            return data
            
        except (tomllib.TOMLDecodeError if hasattr(tomllib, 'TOMLDecodeError') else Exception, UnicodeDecodeError) as e:
            raise SerializationError(
                f"Failed to decode TOML: {e}",
                format_name=self.format_name,
                original_error=e
            )


# Backward compatibility alias
TomlSerializer = XWTomlSerializer

