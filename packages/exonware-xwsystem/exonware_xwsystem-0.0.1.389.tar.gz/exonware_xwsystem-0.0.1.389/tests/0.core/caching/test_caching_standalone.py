"""
#exonware/xwsystem/tests/0.core/caching/test_caching_standalone.py

Standalone core tests for caching - tests cache logic directly without package imports.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.388
Generation Date: 01-Nov-2025
"""

import pytest
import sys
from pathlib import Path

# Add caching module directly to path (bypass package __init__.py)
caching_path = Path(__file__).parent.parent.parent.parent / "src" / "exonware" / "xwsystem" / "caching"
sys.path.insert(0, str(caching_path.parent.parent.parent))


# Mock the logger to avoid package dependencies
class MockLogger:
    def debug(self, msg): pass
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass


# Monkey-patch the logger before importing
import exonware.xwsystem.caching
original_get_logger = None
try:
    from exonware.xwsystem.config import logging_setup
    original_get_logger = logging_setup.get_logger
    logging_setup.get_logger = lambda name: MockLogger()
except:
    # If config module doesn't work, we'll catch it later
    pass


@pytest.mark.xsystem_core
@pytest.mark.xsystem_caching
class TestCachingStandalone:
    """Standalone caching tests without package dependencies."""
    
    def test_lru_basic_operations(self):
        """Test LRU cache basic put/get operations."""
        # Direct import to test in isolation
        import importlib.util
        
        lru_path = caching_path / "lru_cache.py"
        spec = importlib.util.spec_from_file_location("lru_cache", lru_path)
        lru_module = importlib.util.module_from_spec(spec)
        
        # Mock logger in module
        import types
        mock_logger = MockLogger()
        lru_module.logger = mock_logger
        
        # Mock base class
        class MockACache:
            def __init__(self, capacity=128, ttl=None):
                self.capacity = capacity
                self.ttl = ttl
        
        # Inject mock base
        sys.modules['exonware.xwsystem.caching.base'] = types.ModuleType('base')
        sys.modules['exonware.xwsystem.caching.base'].ACache = MockACache
        
        # Now load the module
        spec.loader.exec_module(lru_module)
        
        # Test the cache
        cache = lru_module.LRUCache(capacity=10)
        cache.put('key1', 'value1')
        result = cache.get('key1')
        
        assert result == 'value1'
        assert cache.size() == 1

