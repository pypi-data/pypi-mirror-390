#!/usr/bin/env python3
#exonware/xwsystem/tests/1.unit/io_tests/serialization_tests/formats_tests/scientific_tests/test_mat.py
"""
Unit tests for MATLAB MAT file serializer.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.387
Generation Date: 02-Nov-2025
"""

import pytest
from pathlib import Path
from exonware.xwsystem.io.serialization.formats.scientific import XWMatSerializer


@pytest.mark.xwsystem_unit
class TestMATSerializer:
    """Unit tests for MATLAB MAT file serializer."""
    
    def test_serializer_initialization(self):
        """Test MAT serializer can be initialized."""
        serializer = XWMatSerializer()
        assert serializer is not None
        assert serializer.codec_id == "mat"
        assert serializer.format_name == "MAT"
    
    def test_encode_raises_not_implemented(self):
        """Test encode method raises NotImplementedError (requires file)."""
        serializer = XWMatSerializer()
        data = {"array": [[1, 2], [3, 4]]}
        
        with pytest.raises(NotImplementedError, match="MAT encoding to bytes not supported"):
            serializer.encode(data)
    
    def test_encode_to_file_basic(self, tmp_path):
        """Test encoding to MAT file."""
        serializer = XWMatSerializer()
        output_file = tmp_path / "test.mat"
        
        data = {
            "array": [[1, 2, 3], [4, 5, 6]],
            "scalar": 42,
            "string": "test"
        }
        
        # Should not raise error
        serializer.encode_to_file(data, output_file)
        assert output_file.exists()
    
    def test_decode_from_file_basic(self, tmp_path):
        """Test decoding from MAT file."""
        serializer = XWMatSerializer()
        output_file = tmp_path / "test.mat"
        
        # Create file first
        data = {
            "array": [[1, 2, 3], [4, 5, 6]],
            "scalar": 42
        }
        serializer.encode_to_file(data, output_file)
        
        # Read it back
        result = serializer.decode_from_file(output_file)
        
        assert "array" in result
        assert "scalar" in result
        # MAT files store scalars as arrays, so check value
        assert result["scalar"] == 42 or result["scalar"][0][0] == 42
    
    def test_roundtrip_file_operations(self, tmp_path):
        """Test encoding and decoding preserves data structure."""
        serializer = XWMatSerializer()
        output_file = tmp_path / "roundtrip.mat"
        
        original_data = {
            "matrix": [[1.0, 2.0], [3.0, 4.0]],
            "vector": [10, 20, 30],
            "value": 3.14
        }
        
        serializer.encode_to_file(original_data, output_file)
        decoded = serializer.decode_from_file(output_file)
        
        # Verify keys are preserved
        assert "matrix" in decoded
        assert "vector" in decoded
        assert "value" in decoded
    
    def test_encode_non_dict_wraps_in_dict(self, tmp_path):
        """Test that non-dict data is wrapped."""
        serializer = XWMatSerializer()
        output_file = tmp_path / "wrapped.mat"
        
        data = [1, 2, 3, 4, 5]
        
        serializer.encode_to_file(data, output_file)
        decoded = serializer.decode_from_file(output_file)
        
        # Should have 'data' key
        assert "data" in decoded
    
    def test_encode_with_compression(self, tmp_path):
        """Test encoding with compression option."""
        serializer = XWMatSerializer()
        output_file = tmp_path / "compressed.mat"
        
        data = {"large_array": [[i * j for j in range(100)] for i in range(100)]}
        
        # Should not raise error
        serializer.encode_to_file(data, output_file, options={"do_compression": True})
        assert output_file.exists()
    
    def test_mime_types(self):
        """Test MAT file MIME types are correct."""
        serializer = XWMatSerializer()
        assert "application/x-matlab-data" in serializer.media_types
        assert "application/matlab" in serializer.media_types
    
    def test_file_extensions(self):
        """Test MAT file extensions are correct."""
        serializer = XWMatSerializer()
        assert ".mat" in serializer.file_extensions

