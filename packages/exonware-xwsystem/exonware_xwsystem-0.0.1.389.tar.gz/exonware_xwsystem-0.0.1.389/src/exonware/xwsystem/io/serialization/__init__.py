"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.389
Generation Date: November 2, 2025

Serialization module - 29+ serialization formats with I→A→XW pattern.

This module provides comprehensive serialization support following the
universal codec architecture.

Following I→A→XW pattern:
- I: ISerialization (interface)
- A: ASerialization (abstract base)
- XW: XW{Format}Serializer (concrete implementations)
"""

# Contracts and base classes
from .contracts import ISerialization
from .base import ASerialization, ASchemaRegistry

# Registry
from .registry import SerializationRegistry, get_serialization_registry

# NOTE: Schema Registry moved to exonware-xwschema
# from .schema_registry import (
#     SchemaInfo,
#     ConfluentSchemaRegistry,
#     AwsGlueSchemaRegistry,
#     SchemaRegistry,
# )
# Available in: pip install exonware-xwschema

# Text formats (8 formats)
from .formats.text import (
    XWJsonSerializer, JsonSerializer,
    XWYamlSerializer, YamlSerializer,
    XWTomlSerializer, TomlSerializer,
    XWXmlSerializer, XmlSerializer,
    XWCsvSerializer, CsvSerializer,
    XWConfigParserSerializer, ConfigParserSerializer,
    XWFormDataSerializer, FormDataSerializer,
    XWMultipartSerializer, MultipartSerializer,
)

# Binary formats (6 formats)
from .formats.binary import (
    XWMsgPackSerializer, MsgPackSerializer,
    XWPickleSerializer, PickleSerializer,
    XWBsonSerializer, BsonSerializer,
    XWMarshalSerializer, MarshalSerializer,
    XWCborSerializer, CborSerializer,
    XWPlistSerializer, PlistlibSerializer,
)

# NOTE: Enterprise schema formats moved to exonware-xwformats
# Available in: pip install exonware-xwformats
# - Protobuf, Avro, Parquet, Thrift, ORC, Cap'n Proto, FlatBuffers (7 formats)

# NOTE: Enterprise scientific formats moved to exonware-xwformats
# Available in: pip install exonware-xwformats
# - HDF5, Feather, Zarr (3 formats)

# Database formats (3 core formats)
from .formats.database import (
    XWSqlite3Serializer, Sqlite3Serializer,
    XWDbmSerializer, DbmSerializer,
    XWShelveSerializer, ShelveSerializer,
)

# NOTE: Enterprise database formats moved to exonware-xwformats
# Available in: pip install exonware-xwformats
# - LMDB, GraphDB, LevelDB (3 formats)

# Supporting utilities
from .defs import SerializationFormat, SerializationMode, SerializationType, SerializationCapability
from .errors import SerializationError
from .flyweight import get_serializer, get_flyweight_stats, clear_serializer_cache, get_cache_info, create_serializer, SerializerPool
from .format_detector import detect_format
from .auto_serializer import AutoSerializer
from .serializer import XWSerializer

# Auto-register all serializers with UniversalCodecRegistry
from ..codec.registry import get_registry

_codec_registry = get_registry()

# Register all core serializers
for _serializer_class in [
    # Text formats (8)
    XWJsonSerializer, XWYamlSerializer, XWTomlSerializer, XWXmlSerializer,
    XWCsvSerializer, XWConfigParserSerializer, XWFormDataSerializer, XWMultipartSerializer,
    # Binary formats (6)
    XWMsgPackSerializer, XWPickleSerializer, XWBsonSerializer, XWMarshalSerializer,
    XWCborSerializer, XWPlistSerializer,
    # Database formats (3)
    XWSqlite3Serializer, XWDbmSerializer, XWShelveSerializer,
]:
    try:
        _codec_registry.register(_serializer_class)
    except Exception:
        pass  # Skip if already registered or missing dependencies

# NOTE: xwformats auto-discovery removed per DEV_GUIDELINES.md
# "NO TRY/EXCEPT FOR IMPORTS" - Users should explicitly import xwformats when needed:
# from exonware.xwformats import AvroSerializer, ProtobufSerializer, ...
# xwformats auto-registers its formats on import

__all__ = [
    # Interfaces and base classes
    "ISerialization",
    "ASerialization",
    "ASchemaRegistry",
    
    # Registry
    "SerializationRegistry",
    "get_serialization_registry",
    
    # Text formats (8 - I→A→XW pattern)
    "XWJsonSerializer", "JsonSerializer",
    "XWYamlSerializer", "YamlSerializer",
    "XWTomlSerializer", "TomlSerializer",
    "XWXmlSerializer", "XmlSerializer",
    "XWCsvSerializer", "CsvSerializer",
    "XWConfigParserSerializer", "ConfigParserSerializer",
    "XWFormDataSerializer", "FormDataSerializer",
    "XWMultipartSerializer", "MultipartSerializer",
    
    # Binary formats (6 - I→A→XW pattern)
    "XWMsgPackSerializer", "MsgPackSerializer",
    "XWPickleSerializer", "PickleSerializer",
    "XWBsonSerializer", "BsonSerializer",
    "XWMarshalSerializer", "MarshalSerializer",
    "XWCborSerializer", "CborSerializer",
    "XWPlistSerializer", "PlistlibSerializer",
    
    # Database formats (3 - I→A→XW pattern)
    "XWSqlite3Serializer", "Sqlite3Serializer",
    "XWDbmSerializer", "DbmSerializer",
    "XWShelveSerializer", "ShelveSerializer",
    
    # Supporting utilities
    "SerializationFormat",
    "SerializationMode",
    "SerializationType",
    "SerializationCapability",
    "SerializationError",
    "get_serializer",
    "get_flyweight_stats",
    "clear_serializer_cache",
    "get_cache_info",
    "create_serializer",
    "SerializerPool",
    "detect_format",
    "AutoSerializer",
    "XWSerializer",
]

# NOTE: Enterprise formats available in exonware-xwformats:
# - Schema: Protobuf, Avro, Parquet, Thrift, ORC, Cap'n Proto, FlatBuffers (7 formats)
# - Scientific: HDF5, Feather, Zarr, NetCDF, MAT (5 formats)
# - Database: LMDB, GraphDB, LevelDB (3 formats)
# - Binary: UBJSON (1 format)
# Total: 16 enterprise formats (~87 MB)
# Install with: pip install exonware-xwformats

