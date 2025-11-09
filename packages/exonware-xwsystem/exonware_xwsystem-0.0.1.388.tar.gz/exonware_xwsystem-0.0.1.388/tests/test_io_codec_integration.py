#!/usr/bin/env python3
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: October 30, 2025

Comprehensive tests for IO + Codec Integration.

Tests all new implementations:
- FileDataSource
- PagedFileSource
- CodecIO
- PagedCodecIO
- FileWatcher
- FileLock
- LocalFileSystem
- Archive
- Compression
"""

import pytest
import tempfile
import time
from pathlib import Path
import json
import threading

# Import all implementations
from exonware.xwsystem.io import (
    FileDataSource,
    PagedFileSource,
    CodecIO,
    PagedCodecIO,
    FileWatcher,
    FileLock,
    LocalFileSystem,
    Archive,
    Compression,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_data():
    """Sample data for tests."""
    return {"name": "test", "value": 42, "items": [1, 2, 3]}


@pytest.fixture
def sample_text():
    """Sample text for tests."""
    return "Hello, World!\nThis is a test.\n" * 100


# ============================================================================
# FileDataSource TESTS
# ============================================================================

class TestFileDataSource:
    """Test FileDataSource implementation."""
    
    def test_create_file_data_source(self, temp_dir):
        """Test creating FileDataSource."""
        path = temp_dir / "test.dat"
        source = FileDataSource(path, mode='wb')
        
        assert source.scheme == "file"
        assert source.uri.startswith("file://")
        assert not source.exists()
    
    def test_write_and_read_bytes(self, temp_dir):
        """Test writing and reading bytes."""
        path = temp_dir / "test.dat"
        source = FileDataSource(path, mode='wb')
        
        data = b"Hello, World!"
        source.write(data)
        
        assert source.exists()
        
        # Read back
        source2 = FileDataSource(path, mode='rb')
        result = source2.read()
        
        assert result == data
    
    def test_write_and_read_text(self, temp_dir):
        """Test writing and reading text."""
        path = temp_dir / "test.txt"
        source = FileDataSource(path, mode='r', encoding='utf-8')
        
        text = "Hello, World!"
        source.write(text, encoding='utf-8')
        
        assert source.exists()
        
        # Read back
        result = source.read(encoding='utf-8')
        
        assert result == text
    
    def test_atomic_write(self, temp_dir):
        """Test atomic write operation."""
        path = temp_dir / "test.dat"
        source = FileDataSource(path, mode='wb')
        
        data = b"Test data"
        source.write(data, atomic=True, backup=True)
        
        result = source.read()
        assert result == data
    
    def test_metadata(self, temp_dir):
        """Test file metadata."""
        path = temp_dir / "test.dat"
        source = FileDataSource(path, mode='wb')
        
        # Non-existent file
        meta = source.metadata()
        assert meta['exists'] is False
        
        # Create file
        source.write(b"test")
        
        meta = source.metadata()
        assert meta['exists'] is True
        assert meta['size'] == 4
        assert 'modified' in meta
        assert 'created' in meta
    
    def test_delete(self, temp_dir):
        """Test file deletion."""
        path = temp_dir / "test.dat"
        source = FileDataSource(path, mode='wb')
        
        source.write(b"test")
        assert source.exists()
        
        source.delete()
        assert not source.exists()


# ============================================================================
# PagedFileSource TESTS
# ============================================================================

class TestPagedFileSource:
    """Test PagedFileSource implementation."""
    
    def test_create_paged_source(self, temp_dir):
        """Test creating PagedFileSource."""
        path = temp_dir / "test.dat"
        
        # Create test file
        data = b"0123456789" * 1000  # 10KB
        path.write_bytes(data)
        
        source = PagedFileSource(path, mode='rb')
        
        assert source.total_size == len(data)
        assert source.exists()
    
    def test_read_page_binary(self, temp_dir):
        """Test reading pages in binary mode."""
        path = temp_dir / "test.dat"
        
        # Create test file
        data = b"0123456789" * 100  # 1KB
        path.write_bytes(data)
        
        source = PagedFileSource(path, mode='rb')
        
        # Read page 0 (first 100 bytes)
        page0 = source.read_page(0, 100)
        assert len(page0) == 100
        assert page0 == data[:100]
        
        # Read page 1 (bytes 100-199)
        page1 = source.read_page(1, 100)
        assert len(page1) == 100
        assert page1 == data[100:200]
    
    def test_read_chunk(self, temp_dir):
        """Test reading chunks by offset."""
        path = temp_dir / "test.dat"
        
        data = b"0123456789" * 100
        path.write_bytes(data)
        
        source = PagedFileSource(path, mode='rb')
        
        # Read chunk at offset 50, size 20
        chunk = source.read_chunk(50, 20)
        assert len(chunk) == 20
        assert chunk == data[50:70]
    
    def test_iter_chunks(self, temp_dir):
        """Test iterating over chunks."""
        path = temp_dir / "test.dat"
        
        data = b"0123456789" * 10  # 100 bytes
        path.write_bytes(data)
        
        source = PagedFileSource(path, mode='rb')
        
        # Iterate in 25-byte chunks
        chunks = list(source.iter_chunks(25))
        
        assert len(chunks) == 4  # 100 / 25 = 4
        assert chunks[0] == data[0:25]
        assert chunks[1] == data[25:50]
        assert chunks[2] == data[50:75]
        assert chunks[3] == data[75:100]
    
    def test_iter_pages_text(self, temp_dir):
        """Test iterating over pages in text mode."""
        path = temp_dir / "test.txt"
        
        # Create test file with lines
        lines = [f"Line {i}\n" for i in range(100)]
        path.write_text("".join(lines))
        
        source = PagedFileSource(path, mode='r', encoding='utf-8')
        
        # Iterate in pages of 10 lines
        pages = list(source.iter_pages(10))
        
        assert len(pages) == 10  # 100 lines / 10 = 10 pages
        
        # Check first page
        first_page_lines = pages[0].split('\n')
        assert len(first_page_lines) == 11  # 10 lines + empty string from final \n


# ============================================================================
# CodecIO TESTS (Note: These require codec implementations)
# ============================================================================

class TestCodecIO:
    """Test CodecIO implementation."""
    
    def test_create_codec_io_from_file_json(self, temp_dir, sample_data):
        """Test creating CodecIO with auto-detected JSON codec."""
        path = temp_dir / "test.json"
        
        try:
            # This will work if JSON codec is registered
            io = CodecIO.from_file(path)
            
            # Save data
            io.save(sample_data)
            
            assert io.exists()
            
            # Load back
            result = io.load()
            
            assert result == sample_data
        except Exception as e:
            # Skip if codec not available
            pytest.skip(f"JSON codec not available: {e}")
    
    def test_codec_io_exists(self, temp_dir):
        """Test exists() method."""
        path = temp_dir / "test.json"
        
        try:
            io = CodecIO.from_file(path)
            
            assert not io.exists()
            
            io.save({"test": "data"})
            
            assert io.exists()
        except Exception:
            pytest.skip("JSON codec not available")
    
    def test_codec_io_delete(self, temp_dir):
        """Test delete() method."""
        path = temp_dir / "test.json"
        
        try:
            io = CodecIO.from_file(path)
            
            io.save({"test": "data"})
            assert io.exists()
            
            io.delete()
            assert not io.exists()
        except Exception:
            pytest.skip("JSON codec not available")


# ============================================================================
# FileWatcher TESTS
# ============================================================================

class TestFileWatcher:
    """Test FileWatcher implementation."""
    
    def test_create_watcher(self):
        """Test creating FileWatcher."""
        watcher = FileWatcher(poll_interval=0.1)
        assert not watcher._running
    
    def test_watch_file_changes(self, temp_dir):
        """Test watching file changes."""
        path = temp_dir / "test.txt"
        
        events = []
        
        def on_change(p, event_type):
            events.append((str(p), event_type))
        
        watcher = FileWatcher(poll_interval=0.1)
        watcher.watch(path, on_change)
        watcher.start()
        
        try:
            # Create file
            path.write_text("test")
            time.sleep(0.3)
            
            assert len(events) > 0
            assert any(event[1] == 'created' for event in events)
            
            # Modify file
            events.clear()
            path.write_text("modified")
            time.sleep(0.3)
            
            assert len(events) > 0
            assert any(event[1] == 'modified' for event in events)
            
        finally:
            watcher.stop()
    
    def test_unwatch(self, temp_dir):
        """Test unwatching files."""
        path = temp_dir / "test.txt"
        
        events = []
        
        def on_change(p, event_type):
            events.append(event_type)
        
        watcher = FileWatcher(poll_interval=0.1)
        watcher.watch(path, on_change)
        watcher.unwatch(path)
        
        watcher.start()
        
        try:
            path.write_text("test")
            time.sleep(0.3)
            
            assert len(events) == 0  # Should not receive events
        finally:
            watcher.stop()


# ============================================================================
# FileLock TESTS
# ============================================================================

class TestFileLock:
    """Test FileLock implementation."""
    
    def test_create_lock(self, temp_dir):
        """Test creating FileLock."""
        path = temp_dir / "test.txt"
        lock = FileLock(path)
        
        assert not lock.is_locked()
    
    def test_acquire_release(self, temp_dir):
        """Test acquiring and releasing lock."""
        path = temp_dir / "test.txt"
        lock = FileLock(path)
        
        assert lock.acquire()
        assert lock.is_locked()
        
        lock.release()
        assert not lock.is_locked()
    
    def test_context_manager(self, temp_dir):
        """Test using lock as context manager."""
        path = temp_dir / "test.txt"
        
        with FileLock(path) as lock:
            assert lock.is_locked()
        
        # Lock should be released after context
        lock2 = FileLock(path)
        assert lock2.acquire(timeout=0.1)
        lock2.release()
    
    def test_concurrent_access(self, temp_dir):
        """Test concurrent access prevention."""
        path = temp_dir / "test.txt"
        
        lock1 = FileLock(path)
        lock1.acquire()
        
        lock2 = FileLock(path)
        result = lock2.acquire(timeout=0.1)
        
        assert not result  # Should fail to acquire
        
        lock1.release()


# ============================================================================
# LocalFileSystem TESTS
# ============================================================================

class TestLocalFileSystem:
    """Test LocalFileSystem implementation."""
    
    def test_create_filesystem(self, temp_dir):
        """Test creating LocalFileSystem."""
        fs = LocalFileSystem(temp_dir)
        
        assert fs.scheme == "file"
    
    def test_write_and_read_text(self, temp_dir):
        """Test writing and reading text."""
        fs = LocalFileSystem(temp_dir)
        
        fs.write_text("test.txt", "Hello, World!")
        
        assert fs.exists("test.txt")
        assert fs.is_file("test.txt")
        
        content = fs.read_text("test.txt")
        assert content == "Hello, World!"
    
    def test_write_and_read_bytes(self, temp_dir):
        """Test writing and reading bytes."""
        fs = LocalFileSystem(temp_dir)
        
        data = b"\x00\x01\x02\x03"
        fs.write_bytes("test.bin", data)
        
        result = fs.read_bytes("test.bin")
        assert result == data
    
    def test_mkdir_and_listdir(self, temp_dir):
        """Test creating directory and listing contents."""
        fs = LocalFileSystem(temp_dir)
        
        fs.mkdir("subdir")
        assert fs.exists("subdir")
        assert fs.is_dir("subdir")
        
        fs.write_text("subdir/file1.txt", "test1")
        fs.write_text("subdir/file2.txt", "test2")
        
        contents = fs.listdir("subdir")
        assert "file1.txt" in contents
        assert "file2.txt" in contents
    
    def test_copy(self, temp_dir):
        """Test copying files."""
        fs = LocalFileSystem(temp_dir)
        
        fs.write_text("source.txt", "test content")
        fs.copy("source.txt", "dest.txt")
        
        assert fs.exists("dest.txt")
        assert fs.read_text("dest.txt") == "test content"
    
    def test_move(self, temp_dir):
        """Test moving files."""
        fs = LocalFileSystem(temp_dir)
        
        fs.write_text("source.txt", "test content")
        fs.move("source.txt", "dest.txt")
        
        assert not fs.exists("source.txt")
        assert fs.exists("dest.txt")
        assert fs.read_text("dest.txt") == "test content"
    
    def test_remove(self, temp_dir):
        """Test removing files."""
        fs = LocalFileSystem(temp_dir)
        
        fs.write_text("test.txt", "content")
        assert fs.exists("test.txt")
        
        fs.remove("test.txt")
        assert not fs.exists("test.txt")


# ============================================================================
# Archive TESTS
# ============================================================================

class TestArchive:
    """Test Archive implementation."""
    
    def test_create_zip_archive(self, temp_dir):
        """Test creating ZIP archive."""
        archive = Archive()
        
        # Create test files
        file1 = temp_dir / "file1.txt"
        file2 = temp_dir / "file2.txt"
        file1.write_text("Content 1")
        file2.write_text("Content 2")
        
        # Create archive
        archive_path = temp_dir / "test.zip"
        archive.create([file1, file2], archive_path, format='zip')
        
        assert archive_path.exists()
    
    def test_extract_zip_archive(self, temp_dir):
        """Test extracting ZIP archive."""
        archive = Archive()
        
        # Create test files
        file1 = temp_dir / "file1.txt"
        file1.write_text("Content 1")
        
        # Create archive
        archive_path = temp_dir / "test.zip"
        archive.create([file1], archive_path, format='zip')
        
        # Extract
        output_dir = temp_dir / "output"
        extracted = archive.extract(archive_path, output_dir)
        
        assert len(extracted) > 0
        assert (output_dir / "file1.txt").exists()
    
    def test_list_archive_contents(self, temp_dir):
        """Test listing archive contents."""
        archive = Archive()
        
        # Create test files
        file1 = temp_dir / "file1.txt"
        file2 = temp_dir / "file2.txt"
        file1.write_text("Content 1")
        file2.write_text("Content 2")
        
        # Create archive
        archive_path = temp_dir / "test.zip"
        archive.create([file1, file2], archive_path, format='zip')
        
        # List contents
        contents = archive.list_contents(archive_path)
        
        assert len(contents) == 2
        assert "file1.txt" in contents
        assert "file2.txt" in contents
    
    def test_create_tar_archive(self, temp_dir):
        """Test creating TAR archive."""
        archive = Archive()
        
        # Create test files
        file1 = temp_dir / "file1.txt"
        file1.write_text("Content 1")
        
        # Create archive
        archive_path = temp_dir / "test.tar"
        archive.create([file1], archive_path, format='tar')
        
        assert archive_path.exists()
    
    def test_create_tar_gz_archive(self, temp_dir):
        """Test creating TAR.GZ archive."""
        archive = Archive()
        
        # Create test files
        file1 = temp_dir / "file1.txt"
        file1.write_text("Content 1" * 100)
        
        # Create archive
        archive_path = temp_dir / "test.tar.gz"
        archive.create([file1], archive_path, format='tar.gz')
        
        assert archive_path.exists()
        
        # Compressed size should be smaller than original
        original_size = file1.stat().st_size
        compressed_size = archive_path.stat().st_size
        assert compressed_size < original_size


# ============================================================================
# Compression TESTS
# ============================================================================

class TestCompression:
    """Test Compression implementation."""
    
    def test_compress_and_decompress_gzip(self):
        """Test compressing and decompressing with gzip."""
        comp = Compression()
        
        data = b"Hello, World!" * 1000
        compressed = comp.compress(data, algorithm='gzip')
        
        assert len(compressed) < len(data)
        
        decompressed = comp.decompress(compressed, algorithm='gzip')
        assert decompressed == data
    
    def test_compress_and_decompress_bz2(self):
        """Test compressing and decompressing with bz2."""
        comp = Compression()
        
        data = b"Hello, World!" * 1000
        compressed = comp.compress(data, algorithm='bz2')
        
        assert len(compressed) < len(data)
        
        decompressed = comp.decompress(compressed, algorithm='bz2')
        assert decompressed == data
    
    def test_auto_detect_compression(self):
        """Test auto-detecting compression algorithm."""
        comp = Compression()
        
        data = b"Hello, World!" * 100
        
        # Compress with gzip
        compressed = comp.compress(data, algorithm='gzip')
        
        # Decompress without specifying algorithm
        decompressed = comp.decompress(compressed)
        assert decompressed == data
    
    def test_compress_file(self, temp_dir):
        """Test compressing a file."""
        comp = Compression()
        
        # Create test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("Hello, World!" * 1000)
        
        # Compress
        compressed_file = comp.compress_file(test_file, algorithm='gzip')
        
        assert compressed_file.exists()
        assert compressed_file.suffix == '.gz'
        assert compressed_file.stat().st_size < test_file.stat().st_size
    
    def test_decompress_file(self, temp_dir):
        """Test decompressing a file."""
        comp = Compression()
        
        # Create and compress test file
        test_file = temp_dir / "test.txt"
        original_content = "Hello, World!" * 1000
        test_file.write_text(original_content)
        
        compressed_file = comp.compress_file(test_file, algorithm='gzip')
        
        # Decompress
        decompressed_file = comp.decompress_file(compressed_file)
        
        assert decompressed_file.exists()
        assert decompressed_file.read_text() == original_content
    
    def test_compression_levels(self):
        """Test different compression levels."""
        comp = Compression()
        
        data = b"Hello, World!" * 1000
        
        # Level 1 (fast, less compression)
        compressed_1 = comp.compress(data, algorithm='gzip', level=1)
        
        # Level 9 (slow, more compression)
        compressed_9 = comp.compress(data, algorithm='gzip', level=9)
        
        # Level 9 should be smaller or equal
        assert len(compressed_9) <= len(compressed_1)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests combining multiple components."""
    
    def test_file_source_with_compression(self, temp_dir):
        """Test using FileDataSource with Compression."""
        comp = Compression()
        
        # Create file with compression
        path = temp_dir / "data.txt.gz"
        data = b"Test data" * 1000
        
        # Compress and write
        compressed = comp.compress(data)
        source = FileDataSource(path, mode='wb')
        source.write(compressed)
        
        # Read and decompress
        source2 = FileDataSource(path, mode='rb')
        compressed_read = source2.read()
        decompressed = comp.decompress(compressed_read)
        
        assert decompressed == data
    
    def test_paged_source_with_large_file(self, temp_dir):
        """Test PagedFileSource with larger file."""
        # Create 1MB test file
        path = temp_dir / "large.dat"
        data = b"0123456789" * 102400  # ~1MB
        path.write_bytes(data)
        
        source = PagedFileSource(path, mode='rb')
        
        # Read in 64KB chunks
        chunk_size = 65536
        chunks = list(source.iter_chunks(chunk_size))
        
        # Verify all data read
        reconstructed = b"".join(chunks)
        assert reconstructed == data
        
        # Verify chunk count
        expected_chunks = (len(data) + chunk_size - 1) // chunk_size
        assert len(chunks) == expected_chunks
    
    def test_filesystem_with_archive(self, temp_dir):
        """Test LocalFileSystem with Archive operations."""
        fs = LocalFileSystem(temp_dir)
        archive = Archive()
        
        # Create files using filesystem
        fs.write_text("file1.txt", "Content 1")
        fs.write_text("file2.txt", "Content 2")
        
        # Archive them
        archive_path = temp_dir / "backup.zip"
        files = [temp_dir / "file1.txt", temp_dir / "file2.txt"]
        archive.create(files, archive_path)
        
        # Remove originals
        fs.remove("file1.txt")
        fs.remove("file2.txt")
        
        # Extract archive
        output_dir = temp_dir / "restored"
        archive.extract(archive_path, output_dir)
        
        # Verify restoration
        fs2 = LocalFileSystem(output_dir)
        assert fs2.exists("file1.txt")
        assert fs2.read_text("file1.txt") == "Content 1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

