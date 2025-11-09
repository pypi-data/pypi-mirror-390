#!/usr/bin/env python3
#exonware/xwsystem/src/exonware/xwsystem/io/serialization/formats/text/jsonlines.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.389
Generation Date: 02-Nov-2025

JSON Lines (JSONL/NDJSON) Serialization - Newline-Delimited JSON

JSON Lines format (also called NDJSON - Newline Delimited JSON):
- One JSON object per line
- Perfect for streaming data
- Log file friendly
- Easy to append

Priority 1 (Security): Safe JSON parsing per line
Priority 2 (Usability): Streaming-friendly format
Priority 3 (Maintainability): Simple line-based processing
Priority 4 (Performance): Memory-efficient streaming
Priority 5 (Extensibility): Compatible with standard JSON
"""

from typing import Any, Dict, Optional, Union, List
from pathlib import Path
import json

from ...base import ASerialization
from ...contracts import ISerialization


class XWJsonLinesSerializer(ASerialization):
    """
    JSON Lines (JSONL/NDJSON) serializer for streaming data.
    
    I: ISerialization (interface)
    A: ASerialization (abstract base)
    XW: XWJsonLinesSerializer (concrete implementation)
    """
    
    def __init__(self):
        """Initialize JSON Lines serializer."""
        super().__init__()
    
    @property
    def codec_id(self) -> str:
        """Codec identifier."""
        return "jsonl"
    
    @property
    def media_types(self) -> list[str]:
        """Supported MIME types."""
        return ["application/x-ndjson", "application/jsonl"]
    
    @property
    def file_extensions(self) -> list[str]:
        """Supported file extensions."""
        return [".jsonl", ".ndjson", ".jsonlines"]
    
    @property
    def aliases(self) -> list[str]:
        """Alternative names."""
        return ["jsonl", "JSONL", "ndjson", "NDJSON", "jsonlines"]
    
    @property
    def codec_types(self) -> list[str]:
        """JSON Lines is a data exchange format."""
        return ["data", "serialization"]
    
    def encode(self, data: Any, options: Optional[Dict[str, Any]] = None) -> str:
        """
        Encode data to JSON Lines string.
        
        Args:
            data: List of objects to encode (each becomes one line)
            options: Encoding options
            
        Returns:
            JSON Lines string (one JSON object per line)
        """
        if not isinstance(data, list):
            # Single object - wrap in list
            data = [data]
        
        lines = []
        for item in data:
            lines.append(json.dumps(item, ensure_ascii=False))
        
        return '\n'.join(lines)
    
    def decode(self, data: Union[str, bytes], options: Optional[Dict[str, Any]] = None) -> List[Any]:
        """
        Decode JSON Lines string to list of Python objects.
        
        Args:
            data: JSON Lines string or bytes
            options: Decoding options
            
        Returns:
            List of decoded Python objects
        """
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        
        # Split by newlines and parse each line
        lines = data.strip().split('\n')
        results = []
        
        for line in lines:
            line = line.strip()
            if line:  # Skip empty lines
                results.append(json.loads(line))
        
        return results


# Backward compatibility aliases
JsonLinesSerializer = XWJsonLinesSerializer
JsonlSerializer = XWJsonLinesSerializer
NDJsonSerializer = XWJsonLinesSerializer

