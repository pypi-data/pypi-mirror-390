"""
#exonware/xwsystem/tests/conftest.py

Pytest configuration and fixtures for xwsystem tests.
Provides reusable test data and setup utilities.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.388
Generation Date: 01-Nov-2025
"""

import pytest
from pathlib import Path
import sys
import time
from typing import Any, Dict, List

# Ensure src is in path for imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


# ============================================================================
# BASIC DATA FIXTURES
# ============================================================================

@pytest.fixture
def simple_dict_data():
    """Simple dictionary test data."""
    return {
        'name': 'Alice',
        'age': 30,
        'city': 'New York',
        'active': True
    }


@pytest.fixture
def nested_data():
    """Complex nested hierarchical test data."""
    return {
        'users': [
            {
                'id': 1,
                'name': 'Alice',
                'profile': {
                    'email': 'alice@example.com',
                    'preferences': {'theme': 'dark'}
                }
            }
        ],
        'metadata': {
            'version': 1.0,
            'created': '2024-01-01'
        }
    }


@pytest.fixture
def simple_data():
    """Simple data for basic tests."""
    return {"key": "value", "number": 42, "boolean": True}


@pytest.fixture
def complex_data():
    """Complex nested data for advanced tests."""
    return {
        "users": [
            {"id": 1, "name": "John", "settings": {"theme": "dark"}},
            {"id": 2, "name": "Jane", "settings": {"theme": "light"}}
        ],
        "metadata": {"version": "1.0", "created": "2024-01-01"}
    }


# ============================================================================
# CACHING-SPECIFIC FIXTURES
# ============================================================================

@pytest.fixture
def cache_test_data():
    """Standard test data for caching operations."""
    return {
        'key1': 'value1',
        'key2': 'value2',
        'key3': 'value3',
        'key4': 'value4',
        'key5': 'value5',
    }


@pytest.fixture
def large_cache_dataset():
    """Large dataset for performance testing (1,000 items)."""
    return {f'key_{i}': f'value_{i}' for i in range(1000)}


@pytest.fixture
def very_large_cache_dataset():
    """Very large dataset for stress testing (10,000 items)."""
    return {f'key_{i}': f'value_{i}' for i in range(10000)}


@pytest.fixture
def multilingual_cache_data():
    """Multilingual and emoji data for Unicode testing."""
    return {
        "english": "Hello World",
        "chinese": "你好世界",
        "arabic": "مرحبا بالعالم",
        "emoji": "🚀🎉✅❌🔥💯",
        "special": "Special chars: åäö ñ ç ß €",
        "mixed": "Mixed: Hello 世界 🌍 مرحبا"
    }


@pytest.fixture
def edge_case_keys():
    """Edge case keys for robustness testing."""
    return [
        "",  # Empty string
        " ",  # Single space
        "a" * 100,  # Long key
        "key with spaces",
        "key-with-dashes",
        "key_with_underscores",
        "key.with.dots",
        "123",  # Numeric string
        "CamelCaseKey",
        "UPPERCASE_KEY",
    ]


@pytest.fixture
def malicious_inputs():
    """Malicious input patterns for security testing."""
    return [
        "../../../etc/passwd",  # Path traversal
        "<script>alert('xss')</script>",  # XSS attempt
        "'; DROP TABLE cache; --",  # SQL injection pattern
        "\x00\x01\x02",  # Null bytes
        "A" * 10000,  # Very long input
        {"depth": {"very": {"deep": {"nested": "data" * 100}}}},  # Deep nesting
    ]


# ============================================================================
# DIRECTORY FIXTURES
# ============================================================================

@pytest.fixture
def test_data_dir():
    """Get the test data directory."""
    return Path(__file__).parent / "0.core" / "data"


@pytest.fixture
def temp_test_dir(tmp_path):
    """Create a temporary directory for test files."""
    test_dir = tmp_path / "test_data"
    test_dir.mkdir()
    return test_dir


# ============================================================================
# PERFORMANCE FIXTURES
# ============================================================================

@pytest.fixture
def performance_timer():
    """Fixture for timing operations."""
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            
        def start(self):
            self.start_time = time.time()
            
        def stop(self):
            self.end_time = time.time()
            
        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
    
    return Timer()

