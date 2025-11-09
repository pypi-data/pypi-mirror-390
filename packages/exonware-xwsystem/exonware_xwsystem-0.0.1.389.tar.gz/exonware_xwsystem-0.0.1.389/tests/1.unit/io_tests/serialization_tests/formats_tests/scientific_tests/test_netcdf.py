#!/usr/bin/env python3
#exonware/xwsystem/tests/1.unit/io_tests/serialization_tests/formats_tests/scientific_tests/test_netcdf.py
"""
Unit tests for NetCDF serializer.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.387
Generation Date: 02-Nov-2025
"""

import pytest
from pathlib import Path
from exonware.xwsystem.io.serialization.formats.scientific import XWNetcdfSerializer


@pytest.mark.xwsystem_unit
class TestNetCDFSerializer:
    """Unit tests for NetCDF serializer."""
    
    def test_serializer_initialization(self):
        """Test NetCDF serializer can be initialized."""
        serializer = XWNetcdfSerializer()
        assert serializer is not None
        assert serializer.codec_id == "netcdf"
        assert serializer.format_name == "NETCDF"
    
    def test_encode_raises_not_implemented(self):
        """Test encode method raises NotImplementedError (requires file)."""
        serializer = XWNetcdfSerializer()
        data = {"dimensions": {"time": 10}}
        
        with pytest.raises(NotImplementedError, match="file-based operations"):
            serializer.encode(data)
    
    def test_decode_raises_not_implemented(self):
        """Test decode method raises NotImplementedError (requires file)."""
        serializer = XWNetcdfSerializer()
        
        with pytest.raises(NotImplementedError, match="file-based operations"):
            serializer.decode(b"dummy data")
    
    def test_encode_to_file_basic(self, tmp_path):
        """Test encoding to NetCDF file."""
        serializer = XWNetcdfSerializer()
        output_file = tmp_path / "test.nc"
        
        data = {
            "dimensions": {"time": 10, "x": 5},
            "variables": {
                "temperature": {
                    "data": [[15.0] * 5 for _ in range(10)],
                    "dtype": "f4",
                    "dimensions": ("time", "x"),
                    "attributes": {"units": "Celsius"}
                }
            },
            "attributes": {"description": "Test data"}
        }
        
        # Should not raise error
        serializer.encode_to_file(data, output_file)
        assert output_file.exists()
    
    def test_decode_from_file_basic(self, tmp_path):
        """Test decoding from NetCDF file."""
        serializer = XWNetcdfSerializer()
        output_file = tmp_path / "test.nc"
        
        # Create file first
        data = {
            "dimensions": {"time": 10, "x": 5},
            "variables": {
                "temperature": {
                    "data": [[15.0] * 5 for _ in range(10)],
                    "dtype": "f4",
                    "dimensions": ("time", "x"),
                    "attributes": {"units": "Celsius"}
                }
            },
            "attributes": {"description": "Test data"}
        }
        serializer.encode_to_file(data, output_file)
        
        # Read it back
        result = serializer.decode_from_file(output_file)
        
        assert "dimensions" in result
        assert "variables" in result
        assert "attributes" in result
        assert result["dimensions"]["time"] == 10
        assert result["dimensions"]["x"] == 5
    
    def test_roundtrip_file_operations(self, tmp_path):
        """Test encoding and decoding preserves structure."""
        serializer = XWNetcdfSerializer()
        output_file = tmp_path / "roundtrip.nc"
        
        original_data = {
            "dimensions": {"lat": 3, "lon": 4},
            "variables": {
                "data_var": {
                    "data": [[1.0, 2.0, 3.0, 4.0] for _ in range(3)],
                    "dtype": "f8",
                    "dimensions": ("lat", "lon")
                }
            },
            "attributes": {"title": "Test Dataset"}
        }
        
        serializer.encode_to_file(original_data, output_file)
        decoded = serializer.decode_from_file(output_file)
        
        # Verify structure is preserved
        assert decoded["dimensions"]["lat"] == 3
        assert decoded["dimensions"]["lon"] == 4
        assert "data_var" in decoded["variables"]
    
    def test_mime_types(self):
        """Test NetCDF MIME types are correct."""
        serializer = XWNetcdfSerializer()
        assert "application/netcdf" in serializer.media_types
        assert "application/x-netcdf" in serializer.media_types
    
    def test_file_extensions(self):
        """Test NetCDF file extensions are correct."""
        serializer = XWNetcdfSerializer()
        assert ".nc" in serializer.file_extensions
        assert ".nc4" in serializer.file_extensions
        assert ".netcdf" in serializer.file_extensions

