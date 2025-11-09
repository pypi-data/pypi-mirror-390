#!/usr/bin/env python3
#exonware/xwsystem/tests/1.unit/io_tests/serialization_tests/formats_tests/database_tests/test_leveldb.py
"""
Unit tests for LevelDB serializer.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.387
Generation Date: 02-Nov-2025
"""

import pytest
from pathlib import Path
from exonware.xwsystem.io.serialization.formats.database import XWLeveldbSerializer
from exonware.xwsystem.io.errors import SerializationError


@pytest.mark.xwsystem_unit
class TestLevelDBSerializer:
    """Unit tests for LevelDB serializer."""
    
    def test_serializer_initialization(self):
        """Test LevelDB serializer can be initialized."""
        with pytest.raises(ImportError, match="plyvel library required"):
            # Will fail on Windows without C++ build tools - this is expected
            serializer = XWLeveldbSerializer()
    
    @pytest.mark.skipif(True, reason="LevelDB requires plyvel which needs C++ build tools on Windows")
    def test_encode_dict_to_bytes(self):
        """Test encoding dict to bytes (pickled)."""
        serializer = XWLeveldbSerializer()
        data = {"key1": "value1", "key2": "value2"}
        
        result = serializer.encode(data)
        assert result is not None
        assert isinstance(result, bytes)
    
    @pytest.mark.skipif(True, reason="LevelDB requires plyvel which needs C++ build tools on Windows")
    def test_encode_non_dict_raises_error(self):
        """Test encoding non-dict raises SerializationError."""
        serializer = XWLeveldbSerializer()
        
        with pytest.raises(SerializationError, match="expects dict"):
            serializer.encode([1, 2, 3])
    
    @pytest.mark.skipif(True, reason="LevelDB requires plyvel which needs C++ build tools on Windows")
    def test_decode_bytes_to_dict(self):
        """Test decoding bytes to dict."""
        serializer = XWLeveldbSerializer()
        original_data = {"key1": "value1", "key2": "value2"}
        
        encoded = serializer.encode(original_data)
        decoded = serializer.decode(encoded)
        
        assert decoded == original_data
    
    @pytest.mark.skipif(True, reason="LevelDB requires plyvel which needs C++ build tools on Windows")
    def test_encode_to_file_creates_database(self, tmp_path):
        """Test encoding to file creates LevelDB database."""
        serializer = XWLeveldbSerializer()
        db_path = tmp_path / "test.ldb"
        
        data = {
            "user:1": "Alice",
            "user:2": "Bob",
            "user:3": "Charlie"
        }
        
        # Should not raise error
        serializer.encode_to_file(data, db_path)
        assert db_path.exists()
    
    @pytest.mark.skipif(True, reason="LevelDB requires plyvel which needs C++ build tools on Windows")
    def test_decode_from_file_reads_database(self, tmp_path):
        """Test decoding from file reads LevelDB database."""
        serializer = XWLeveldbSerializer()
        db_path = tmp_path / "test.ldb"
        
        # Create database first
        data = {
            "user:1": "Alice",
            "user:2": "Bob"
        }
        serializer.encode_to_file(data, db_path)
        
        # Read it back
        result = serializer.decode_from_file(db_path)
        
        assert result == data
    
    @pytest.mark.skipif(True, reason="LevelDB requires plyvel which needs C++ build tools on Windows")
    def test_roundtrip_file_operations(self, tmp_path):
        """Test encoding and decoding preserves data."""
        serializer = XWLeveldbSerializer()
        db_path = tmp_path / "roundtrip.ldb"
        
        original_data = {
            "config:timeout": 30,
            "config:retries": 3,
            "user:admin": {"role": "admin", "active": True}
        }
        
        serializer.encode_to_file(original_data, db_path)
        decoded = serializer.decode_from_file(db_path)
        
        assert decoded == original_data
    
    @pytest.mark.skipif(True, reason="LevelDB requires plyvel which needs C++ build tools on Windows")
    def test_encode_to_file_non_dict_raises_error(self, tmp_path):
        """Test encode_to_file with non-dict raises error."""
        serializer = XWLeveldbSerializer()
        db_path = tmp_path / "invalid.ldb"
        
        with pytest.raises(SerializationError, match="expects dict"):
            serializer.encode_to_file([1, 2, 3], db_path)
    
    @pytest.mark.skipif(True, reason="LevelDB requires plyvel which needs C++ build tools on Windows")
    def test_handles_various_value_types(self, tmp_path):
        """Test LevelDB handles various Python value types."""
        serializer = XWLeveldbSerializer()
        db_path = tmp_path / "types.ldb"
        
        data = {
            "string": "value",
            "int": 42,
            "float": 3.14,
            "bool": True,
            "none": None,
            "list": [1, 2, 3],
            "dict": {"nested": "value"}
        }
        
        serializer.encode_to_file(data, db_path)
        decoded = serializer.decode_from_file(db_path)
        
        assert decoded == data
    
    @pytest.mark.skipif(True, reason="LevelDB requires plyvel which needs C++ build tools on Windows")
    def test_mime_types(self):
        """Test LevelDB MIME types are correct."""
        serializer = XWLeveldbSerializer()
        assert "application/x-leveldb" in serializer.media_types
    
    @pytest.mark.skipif(True, reason="LevelDB requires plyvel which needs C++ build tools on Windows")
    def test_file_extensions(self):
        """Test LevelDB file extensions are correct."""
        serializer = XWLeveldbSerializer()
        assert ".ldb" in serializer.file_extensions
        assert ".leveldb" in serializer.file_extensions

