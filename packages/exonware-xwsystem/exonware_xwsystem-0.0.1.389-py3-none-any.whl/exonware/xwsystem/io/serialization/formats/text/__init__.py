"""Text-based serialization formats."""

from .json import XWJsonSerializer, JsonSerializer
from .json5 import XWJson5Serializer, Json5Serializer
from .jsonlines import XWJsonLinesSerializer, JsonLinesSerializer, JsonlSerializer, NDJsonSerializer
from .yaml import XWYamlSerializer, YamlSerializer
from .toml import XWTomlSerializer, TomlSerializer
from .xml import XWXmlSerializer, XmlSerializer
from .csv import XWCsvSerializer, CsvSerializer
from .configparser import XWConfigParserSerializer, ConfigParserSerializer
from .formdata import XWFormDataSerializer, FormDataSerializer
from .multipart import XWMultipartSerializer, MultipartSerializer

__all__ = [
    # I→A→XW pattern (XW prefix)
    "XWJsonSerializer",
    "XWJson5Serializer",
    "XWJsonLinesSerializer",
    "XWYamlSerializer",
    "XWTomlSerializer",
    "XWXmlSerializer",
    "XWCsvSerializer",
    "XWConfigParserSerializer",
    "XWFormDataSerializer",
    "XWMultipartSerializer",
    
    # Backward compatibility aliases
    "JsonSerializer",
    "Json5Serializer",
    "JsonLinesSerializer",
    "JsonlSerializer",
    "NDJsonSerializer",
    "YamlSerializer",
    "TomlSerializer",
    "XmlSerializer",
    "CsvSerializer",
    "ConfigParserSerializer",
    "FormDataSerializer",
    "MultipartSerializer",
]

