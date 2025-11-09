#!/usr/bin/env python3
#exonware/xwsystem/tests/1.unit/io_tests/serialization_tests/formats_tests/binary_tests/test_ubjson.py
"""
Unit tests for UBJSON serializer.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.387
Generation Date: 02-Nov-2025
"""

import pytest
from exonware.xwsystem.io.serialization.formats.binary import XWUbjsonSerializer


@pytest.mark.xwsystem_unit
class TestUBJSONSerializer:
    """Unit tests for UBJSON serializer."""
    
    def test_serializer_initialization(self):
        """Test UBJSON serializer can be initialized."""
        serializer = XWUbjsonSerializer()
        assert serializer is not None
        assert serializer.codec_id == "ubjson"
        assert serializer.format_name == "UBJSON"
    
    def test_encode_simple_dict(self):
        """Test encoding simple dictionary."""
        serializer = XWUbjsonSerializer()
        data = {"name": "Alice", "age": 30}
        
        result = serializer.encode(data)
        assert result is not None
        assert isinstance(result, bytes)
    
    def test_decode_ubjson_bytes(self):
        """Test decoding UBJSON bytes."""
        serializer = XWUbjsonSerializer()
        data = {"name": "Alice", "age": 30}
        
        # Encode first
        encoded = serializer.encode(data)
        
        # Then decode
        result = serializer.decode(encoded)
        assert result == data
    
    def test_roundtrip_encoding(self):
        """Test encoding and decoding preserves data."""
        serializer = XWUbjsonSerializer()
        original_data = {
            "string": "value",
            "number": 42,
            "float": 3.14,
            "boolean": True,
            "null": None,
            "array": [1, 2, 3],
            "nested": {"key": "value"}
        }
        
        encoded = serializer.encode(original_data)
        decoded = serializer.decode(encoded)
        
        assert decoded == original_data
    
    def test_binary_format_is_compact(self):
        """Test that binary format is more compact than JSON."""
        serializer = XWUbjsonSerializer()
        data = {"key": "value", "number": 42}
        
        encoded = serializer.encode(data)
        json_equivalent = '{"key": "value", "number": 42}'
        
        # UBJSON should be roughly same size or smaller
        assert isinstance(encoded, bytes)
        assert len(encoded) <= len(json_equivalent)
    
    def test_encode_list(self):
        """Test encoding list data."""
        serializer = XWUbjsonSerializer()
        data = [1, 2, 3, 4, 5]
        
        encoded = serializer.encode(data)
        decoded = serializer.decode(encoded)
        
        assert decoded == data
    
    def test_encode_nested_structures(self):
        """Test encoding complex nested structures."""
        serializer = XWUbjsonSerializer()
        data = {
            "users": [
                {"id": 1, "name": "Alice", "active": True},
                {"id": 2, "name": "Bob", "active": False}
            ],
            "metadata": {
                "version": 1.0,
                "count": 2
            }
        }
        
        encoded = serializer.encode(data)
        decoded = serializer.decode(encoded)
        
        assert decoded == data
    
    def test_mime_types(self):
        """Test UBJSON MIME types are correct."""
        serializer = XWUbjsonSerializer()
        assert "application/ubjson" in serializer.media_types
    
    def test_file_extensions(self):
        """Test UBJSON file extensions are correct."""
        serializer = XWUbjsonSerializer()
        assert ".ubj" in serializer.file_extensions
        assert ".ubjson" in serializer.file_extensions

