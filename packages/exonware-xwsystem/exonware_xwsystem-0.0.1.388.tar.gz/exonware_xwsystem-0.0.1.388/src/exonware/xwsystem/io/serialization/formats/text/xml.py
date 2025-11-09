"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.388
Generation Date: November 2, 2025

XML serialization - Extensible Markup Language.

Following I→A→XW pattern:
- I: ISerialization (interface)
- A: ASerialization (abstract base)
- XW: XWXmlSerializer (concrete implementation)
"""

from typing import Any, Optional, Union
from pathlib import Path

from ...base import ASerialization
from ....contracts import EncodeOptions, DecodeOptions
from ....defs import CodecCapability
from ....errors import SerializationError

# Use defusedxml for security
try:
    import defusedxml.ElementTree as ET
    from defusedxml import defuse_stdlib
    defuse_stdlib()
except ImportError:
    import xml.etree.ElementTree as ET

try:
    import dicttoxml
    import xmltodict
except ImportError:
    dicttoxml = None
    xmltodict = None


class XWXmlSerializer(ASerialization):
    """
    XML serializer - follows I→A→XW pattern.
    
    I: ISerialization (interface)
    A: ASerialization (abstract base)
    XW: XWXmlSerializer (concrete implementation)
    
    Uses defusedxml, dicttoxml, and xmltodict for secure XML handling.
    
    Examples:
        >>> serializer = XWXmlSerializer()
        >>> 
        >>> # Encode data
        >>> xml_str = serializer.encode({"user": {"name": "John", "age": 30}})
        >>> 
        >>> # Decode data
        >>> data = serializer.decode("<user><name>John</name></user>")
        >>> 
        >>> # Save to file
        >>> serializer.save_file({"config": {"debug": True}}, "config.xml")
        >>> 
        >>> # Load from file
        >>> config = serializer.load_file("config.xml")
    """
    
    def __init__(self):
        """Initialize XML serializer."""
        super().__init__()
        if dicttoxml is None or xmltodict is None:
            raise ImportError(
                "dicttoxml and xmltodict are required for XML serialization. "
                "Install with: pip install dicttoxml xmltodict defusedxml"
            )
    
    # ========================================================================
    # CODEC METADATA
    # ========================================================================
    
    @property
    def codec_id(self) -> str:
        return "xml"
    
    @property
    def media_types(self) -> list[str]:
        return ["application/xml", "text/xml"]
    
    @property
    def file_extensions(self) -> list[str]:
        return [".xml", ".svg", ".rss", ".atom", ".xhtml", ".xsd", ".wsdl", ".plist", ".csproj", ".xaml"]
    
    @property
    def format_name(self) -> str:
        return "XML"
    
    @property
    def mime_type(self) -> str:
        return "application/xml"
    
    @property
    def is_binary_format(self) -> bool:
        return False  # XML is text-based
    
    @property
    def supports_streaming(self) -> bool:
        return True  # XML supports streaming via SAX/iterparse
    
    @property
    def capabilities(self) -> CodecCapability:
        return CodecCapability.BIDIRECTIONAL
    
    @property
    def aliases(self) -> list[str]:
        return ["xml", "XML"]
    
    @property
    def codec_types(self) -> list[str]:
        """XML is both a serialization and markup language."""
        return ["serialization", "markup"]
    
    # ========================================================================
    # CORE ENCODE/DECODE (Using dicttoxml + xmltodict)
    # ========================================================================
    
    def encode(self, value: Any, *, options: Optional[EncodeOptions] = None) -> Union[bytes, str]:
        """
        Encode data to XML string.
        
        Uses dicttoxml.dicttoxml().
        
        Args:
            value: Data to serialize
            options: XML options (root, attr_type, etc.)
        
        Returns:
            XML string
        
        Raises:
            SerializationError: If encoding fails
        """
        try:
            opts = options or {}
            
            # Encode to XML bytes
            xml_bytes = dicttoxml.dicttoxml(
                value,
                custom_root=opts.get('root', 'root'),
                attr_type=opts.get('attr_type', False),
                item_func=opts.get('item_func', lambda x: 'item')
            )
            
            # Convert to string
            xml_str = xml_bytes.decode('utf-8')
            
            # Pretty print if requested
            if opts.get('pretty', False):
                import xml.dom.minidom
                dom = xml.dom.minidom.parseString(xml_bytes)
                xml_str = dom.toprettyxml(indent=opts.get('indent', '  '))
            
            return xml_str
            
        except Exception as e:
            raise SerializationError(
                f"Failed to encode XML: {e}",
                format_name=self.format_name,
                original_error=e
            )
    
    def decode(self, repr: Union[bytes, str], *, options: Optional[DecodeOptions] = None) -> Any:
        """
        Decode XML string to data.
        
        Uses xmltodict.parse().
        
        Args:
            repr: XML string (bytes or str)
            options: XML options (process_namespaces, etc.)
        
        Returns:
            Decoded Python dict
        
        Raises:
            SerializationError: If decoding fails
        """
        try:
            # Convert bytes to str if needed
            if isinstance(repr, bytes):
                repr = repr.decode('utf-8')
            
            opts = options or {}
            
            # Decode from XML string
            data = xmltodict.parse(
                repr,
                process_namespaces=opts.get('process_namespaces', False),
                namespace_separator=opts.get('namespace_separator', ':'),
                disable_entities=True,  # Security: disable external entities
                forbid_dtd=True,  # Security: forbid DTD
                forbid_entities=True  # Security: forbid entities
            )
            
            return data
            
        except (Exception, UnicodeDecodeError) as e:
            raise SerializationError(
                f"Failed to decode XML: {e}",
                format_name=self.format_name,
                original_error=e
            )


# Backward compatibility alias
XmlSerializer = XWXmlSerializer

