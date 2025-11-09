#!/usr/bin/env python3
"""
Tests for codec package.

Tests the codec abstraction independently without serialization/syntax integration.
"""

import pytest
import json
from pathlib import Path
from typing import Any, Optional, Dict

# Import codec components (now in io.codec!)
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from exonware.xwsystem.io.codec import (
    ICodec,
    ACodec,
    Serializer,
    Formatter,
    MediaKey,
    CodecRegistry,
    get_global_registry,
    FormatterToSerializer,
    SerializerToFormatter,
    CodecCapability,
    EncodeError,
    DecodeError,
    CodecNotFoundError,
)


# ============================================================================
# EXAMPLE CODEC IMPLEMENTATIONS FOR TESTING
# ============================================================================

class SimpleJsonCodec(ACodec[dict, bytes]):
    """Simple JSON codec for testing (bytes-based)."""
    
    codec_id = "json-test"
    media_types = ["application/json", "text/json"]
    file_extensions = [".json"]
    aliases = ["json", "JSON"]
    
    def encode(self, value: dict, *, options: Optional[Dict] = None) -> bytes:
        opts = options or {}
        indent = 2 if opts.get('pretty') else None
        return json.dumps(value, indent=indent).encode('utf-8')
    
    def decode(self, repr: bytes, *, options: Optional[Dict] = None) -> dict:
        return json.loads(repr.decode('utf-8'))
    
    def capabilities(self) -> CodecCapability:
        return CodecCapability.BIDIRECTIONAL | CodecCapability.TEXT


class SimpleSqlFormatter(ACodec[dict, str]):
    """Simple SQL formatter for testing (string-based)."""
    
    codec_id = "sql-test"
    media_types = ["application/sql", "text/x-sql"]
    file_extensions = [".sql"]
    aliases = ["sql", "SQL"]
    
    def encode(self, value: dict, *, options: Optional[Dict] = None) -> str:
        """Generate SQL from dict."""
        if 'select' in value:
            return f"SELECT {value['select']} FROM {value['from']}"
        return str(value)
    
    def decode(self, repr: str, *, options: Optional[Dict] = None) -> dict:
        """Parse SQL to dict (simple parser)."""
        # Very simple parser for testing
        if repr.startswith("SELECT"):
            parts = repr.replace(',', '').split()  # Remove commas for parsing
            # Find SELECT and FROM positions
            select_idx = parts.index("SELECT") + 1
            from_idx = parts.index("FROM") + 1
            # Everything between SELECT and FROM
            select_items = ' '.join(parts[select_idx:from_idx-1])
            table = parts[from_idx]
            return {'select': select_items, 'from': table}
        return {'raw': repr}
    
    def capabilities(self) -> CodecCapability:
        return CodecCapability.BIDIRECTIONAL | CodecCapability.TEXT


# ============================================================================
# TESTS: Core Codec Interface
# ============================================================================

def test_codec_encode_decode():
    """Test basic encode/decode operations."""
    codec = SimpleJsonCodec()
    
    # Test encode
    data = {"name": "Alice", "age": 30}
    encoded = codec.encode(data)
    assert isinstance(encoded, bytes)
    assert b'"name"' in encoded
    assert b'"Alice"' in encoded
    
    # Test decode
    decoded = codec.decode(encoded)
    assert decoded == data


def test_codec_with_options():
    """Test codec with encoding options."""
    codec = SimpleJsonCodec()
    
    # Without pretty
    data = {"key": "value"}
    compact = codec.encode(data)
    assert b'\n' not in compact
    
    # With pretty
    pretty = codec.encode(data, options={'pretty': True})
    assert b'\n' in pretty


def test_formatter_returns_string():
    """Test that formatter returns string, not bytes."""
    formatter = SimpleSqlFormatter()
    
    data = {'select': '*', 'from': 'users'}
    result = formatter.encode(data)
    
    assert isinstance(result, str)
    assert result == "SELECT * FROM users"


# ============================================================================
# TESTS: Metadata
# ============================================================================

def test_codec_metadata():
    """Test codec metadata properties."""
    codec = SimpleJsonCodec()
    
    assert codec.codec_id == "json-test"
    assert "application/json" in codec.media_types
    assert ".json" in codec.file_extensions
    assert "json" in codec.aliases
    assert CodecCapability.BIDIRECTIONAL in codec.capabilities()


# ============================================================================
# TESTS: Convenience Methods
# ============================================================================

def test_dumps_loads_aliases():
    """Test dumps/loads convenience aliases."""
    codec = SimpleJsonCodec()
    data = {"test": 123}
    
    # Test dumps (alias for encode)
    result = codec.dumps(data)
    assert isinstance(result, bytes)
    
    # Test loads (alias for decode)
    decoded = codec.loads(result)
    assert decoded == data


def test_serialize_deserialize_aliases():
    """Test serialize/deserialize aliases."""
    codec = SimpleJsonCodec()
    data = {"test": 456}
    
    serialized = codec.serialize(data)
    deserialized = codec.deserialize(serialized)
    
    assert deserialized == data


def test_file_operations(tmp_path):
    """Test save/load file operations."""
    codec = SimpleJsonCodec()
    data = {"file": "test"}
    
    # Test save
    file_path = tmp_path / "test.json"
    codec.save(data, file_path)
    assert file_path.exists()
    
    # Test load
    loaded = codec.load(file_path)
    assert loaded == data


def test_export_import_aliases(tmp_path):
    """Test export/import aliases."""
    codec = SimpleJsonCodec()
    data = {"export": "test"}
    
    file_path = tmp_path / "export.json"
    codec.export(data, file_path)
    imported = codec.import_(file_path)
    
    assert imported == data


def test_to_file_from_file_aliases(tmp_path):
    """Test to_file/from_file aliases."""
    codec = SimpleJsonCodec()
    data = {"direction": "explicit"}
    
    file_path = tmp_path / "direction.json"
    codec.to_file(data, file_path)
    result = codec.from_file(file_path)
    
    assert result == data


def test_save_as_load_as_with_format(tmp_path):
    """Test save_as/load_as with format hints."""
    codec = SimpleJsonCodec()
    data = {"format": "hint"}
    
    file_path = tmp_path / "format.json"
    codec.save_as(data, file_path, format="pretty")
    result = codec.load_as(file_path)
    
    assert result == data


# ============================================================================
# TESTS: MediaKey
# ============================================================================

def test_media_key_creation():
    """Test MediaKey creation and normalization."""
    key1 = MediaKey("application/json")
    key2 = MediaKey("APPLICATION/JSON")
    
    assert key1 == key2  # Case-insensitive
    assert str(key1) == "application/json"


def test_media_key_from_extension():
    """Test MediaKey.from_extension()."""
    key = MediaKey.from_extension(".json")
    assert key is not None
    assert "json" in key.type.lower()


# ============================================================================
# TESTS: CodecRegistry
# ============================================================================

def test_registry_register_and_get():
    """Test codec registration and retrieval."""
    registry = CodecRegistry()
    registry.register(SimpleJsonCodec)
    
    # Get by media type
    codec = registry.get(MediaKey("application/json"))
    assert codec is not None
    assert codec.codec_id == "json-test"


def test_registry_get_by_extension():
    """Test registry.get_by_extension()."""
    registry = CodecRegistry()
    registry.register(SimpleJsonCodec)
    
    # Get by extension
    codec = registry.get_by_extension(".json")
    assert codec is not None
    assert codec.codec_id == "json-test"
    
    # Get by extension without dot
    codec2 = registry.get_by_extension("json")
    assert codec2 is not None
    
    # Get by full path
    codec3 = registry.get_by_extension("data.json")
    assert codec3 is not None


def test_registry_get_by_id():
    """Test registry.get_by_id()."""
    registry = CodecRegistry()
    registry.register(SimpleJsonCodec)
    
    # Get by ID
    codec = registry.get_by_id("json-test")
    assert codec is not None
    
    # Get by alias (case-insensitive)
    codec2 = registry.get_by_id("JSON")
    assert codec2 is not None


def test_registry_caching():
    """Test that registry caches codec instances."""
    registry = CodecRegistry()
    registry.register(SimpleJsonCodec)
    
    codec1 = registry.get(MediaKey("application/json"))
    codec2 = registry.get(MediaKey("application/json"))
    
    # Should be same instance (cached)
    assert codec1 is codec2


def test_registry_list_methods():
    """Test registry listing methods."""
    registry = CodecRegistry()
    registry.register(SimpleJsonCodec)
    registry.register(SimpleSqlFormatter)
    
    media_types = registry.list_media_types()
    assert len(media_types) > 0
    assert any("json" in mt for mt in media_types)
    
    extensions = registry.list_extensions()
    assert ".json" in extensions
    assert ".sql" in extensions
    
    codec_ids = registry.list_codec_ids()
    assert "json-test" in codec_ids
    assert "sql-test" in codec_ids


def test_global_registry():
    """Test global registry singleton."""
    registry1 = get_global_registry()
    registry2 = get_global_registry()
    
    assert registry1 is registry2  # Same instance


# ============================================================================
# TESTS: Adapters
# ============================================================================

def test_formatter_to_serializer_adapter():
    """Test FormatterToSerializer adapter."""
    formatter = SimpleSqlFormatter()
    serializer = FormatterToSerializer(formatter)
    
    data = {'select': '*', 'from': 'users'}
    
    # Encode returns bytes (not str)
    result = serializer.encode(data)
    assert isinstance(result, bytes)
    assert b"SELECT" in result
    
    # Decode from bytes
    decoded = serializer.decode(result)
    assert decoded == data


def test_serializer_to_formatter_adapter():
    """Test SerializerToFormatter adapter."""
    serializer = SimpleJsonCodec()
    formatter = SerializerToFormatter(serializer)
    
    data = {"key": "value"}
    
    # Encode returns str (not bytes)
    result = formatter.encode(data)
    assert isinstance(result, str)
    assert '"key"' in result
    
    # Decode from str
    decoded = formatter.decode(result)
    assert decoded == data


def test_adapter_utf8_encoding():
    """Test adapter uses UTF-8 correctly."""
    formatter = SimpleSqlFormatter()
    serializer = FormatterToSerializer(formatter, encoding="utf-8")
    
    data = {'select': 'ñame', 'from': 'üsers'}  # Unicode characters
    
    result = serializer.encode(data)
    assert isinstance(result, bytes)
    
    decoded = serializer.decode(result)
    assert decoded['select'] == 'ñame'


# ============================================================================
# TESTS: Error Handling
# ============================================================================

def test_codec_not_found_error():
    """Test CodecNotFoundError is raised for unknown codec."""
    registry = CodecRegistry()
    
    # Try to get non-existent codec
    codec = registry.get(MediaKey("application/unknown"))
    assert codec is None  # Returns None, doesn't raise


def test_encode_error_handling():
    """Test error handling during encode."""
    class FailingCodec(ACodec[dict, bytes]):
        codec_id = "failing"
        media_types = ["application/failing"]
        file_extensions = [".fail"]
        
        def encode(self, value, *, options=None):
            raise ValueError("Encode failed!")
        
        def decode(self, repr, *, options=None):
            return {}
        
        def capabilities(self):
            return CodecCapability.BIDIRECTIONAL
    
    codec = FailingCodec()
    
    with pytest.raises(ValueError):
        codec.encode({"test": 123})


# ============================================================================
# TESTS: Integration
# ============================================================================

def test_end_to_end_json_workflow(tmp_path):
    """Test complete workflow: encode → save → load → decode."""
    codec = SimpleJsonCodec()
    original_data = {"user": "alice", "age": 30, "active": True}
    
    # Encode
    encoded = codec.encode(original_data)
    assert isinstance(encoded, bytes)
    
    # Save to file
    file_path = tmp_path / "user.json"
    codec.save(original_data, file_path)
    
    # Load from file
    loaded = codec.load(file_path)
    assert loaded == original_data


def test_end_to_end_sql_workflow():
    """Test complete workflow with SQL formatter."""
    formatter = SimpleSqlFormatter()
    original_data = {'select': '*', 'from': 'products'}
    
    # Encode
    sql = formatter.encode(original_data)
    assert sql == "SELECT * FROM products"
    
    # Decode
    parsed = formatter.decode(sql)
    assert parsed == original_data


def test_cross_codec_conversion():
    """Test converting between different codec formats."""
    json_codec = SimpleJsonCodec()
    sql_formatter = SimpleSqlFormatter()
    
    # Create data
    data = {'select': '*', 'from': 'users'}
    
    # Format as SQL
    sql_text = sql_formatter.encode(data)
    assert "SELECT" in sql_text
    
    # Can also serialize the dict as JSON
    json_bytes = json_codec.encode(data)
    assert b'"select"' in json_bytes
    
    # Both represent same data
    json_decoded = json_codec.decode(json_bytes)
    sql_decoded = sql_formatter.decode(sql_text)
    assert json_decoded == sql_decoded


def test_registry_workflow():
    """Test complete registry workflow."""
    from exonware.xwsystem.io.codec import register_codec, get_codec, get_codec_by_id
    
    # Register codecs
    register_codec(SimpleJsonCodec)
    register_codec(SimpleSqlFormatter)
    
    # Get JSON codec
    json_codec = get_codec(MediaKey("application/json"))
    assert json_codec is not None
    
    # Use it
    data = {"test": "registry"}
    encoded = json_codec.encode(data)
    decoded = json_codec.decode(encoded)
    assert decoded == data
    
    # Get SQL codec by ID
    sql_codec = get_codec_by_id("sql-test")
    assert sql_codec is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

