"""
#exonware/xwsystem/src/exonware/xwsystem/utils/lazy_package/lazy_base.py

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.388
Generation Date: 10-Oct-2025

Abstract Base Classes for Lazy Loading System

This module defines all abstract base classes for the lazy loading system
following DEV_GUIDELINES.md structure. All abstract classes start with 'A'
and extend interfaces from lazy_contracts.py.

Design Patterns:
- Template Method: Base classes define common workflows with abstract steps
- Strategy: Different implementations can be plugged in
- Abstract Factory: Factory methods for creating instances
"""

import threading
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from types import ModuleType

from .lazy_contracts import (
    IPackageDiscovery,
    IPackageInstaller,
    IImportHook,
    IPackageCache,
    ILazyLoader,
    DependencyInfo,
    LazyInstallMode,
)


# =============================================================================
# ABSTRACT DISCOVERY (Template Method Pattern)
# =============================================================================

class APackageDiscovery(IPackageDiscovery, ABC):
    """
    Abstract base for package discovery.
    
    Implements Template Method pattern where discover_all_dependencies()
    defines the overall workflow, and subclasses implement specific steps.
    """
    
    __slots__ = ('project_root', 'discovered_dependencies', '_discovery_sources', 
                 '_cached_dependencies', '_file_mtimes', '_cache_valid')
    
    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize package discovery.
        
        Args:
            project_root: Root directory of project (auto-detected if None)
        """
        self.project_root = Path(project_root) if project_root else self._find_project_root()
        self.discovered_dependencies: Dict[str, DependencyInfo] = {}
        self._discovery_sources: List[str] = []
        self._cached_dependencies: Dict[str, str] = {}
        self._file_mtimes: Dict[str, float] = {}
        self._cache_valid = False
    
    def _find_project_root(self) -> Path:
        """Find the project root directory by looking for markers."""
        current = Path(__file__).parent
        while current != current.parent:
            if (current / 'pyproject.toml').exists() or (current / 'setup.py').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def discover_all_dependencies(self) -> Dict[str, str]:
        """
        Template method: Discover all dependencies from all sources.
        
        Workflow:
        1. Check if cache is valid
        2. If not, discover from sources
        3. Add common mappings
        4. Update cache
        5. Return dependencies
        
        Returns:
            Dict mapping import_name -> package_name
        """
        # Return cached result if still valid
        if self._is_cache_valid():
            return self._cached_dependencies.copy()
        
        # Cache invalid - rediscover
        self.discovered_dependencies.clear()
        self._discovery_sources.clear()
        
        # Discover from all sources (abstract method)
        self._discover_from_sources()
        
        # Add common mappings
        self._add_common_mappings()
        
        # Convert to simple dict format and cache
        result = {}
        for import_name, dep_info in self.discovered_dependencies.items():
            result[import_name] = dep_info.package_name
        
        # Update cache
        self._cached_dependencies = result.copy()
        self._cache_valid = True
        self._update_file_mtimes()
        
        return result
    
    @abstractmethod
    def _discover_from_sources(self) -> None:
        """
        Discover dependencies from all sources (abstract step).
        
        Implementations should discover from:
        - pyproject.toml
        - requirements.txt
        - setup.py
        - custom config files
        """
        pass
    
    @abstractmethod
    def _is_cache_valid(self) -> bool:
        """
        Check if cached dependencies are still valid (abstract step).
        
        Returns:
            True if cache is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def _add_common_mappings(self) -> None:
        """Add common import -> package mappings (abstract step)."""
        pass
    
    @abstractmethod
    def _update_file_mtimes(self) -> None:
        """Update file modification times for cache validation (abstract step)."""
        pass
    
    def get_discovery_sources(self) -> List[str]:
        """Get list of sources used for discovery."""
        return self._discovery_sources.copy()


# =============================================================================
# ABSTRACT INSTALLER (Strategy Pattern)
# =============================================================================

class APackageInstaller(IPackageInstaller, ABC):
    """
    Abstract base for package installation.
    
    Implements Strategy pattern for different installation modes:
    - AUTO: Automatically install without asking
    - INTERACTIVE: Ask user before installing
    - WARN: Log warning but don't install
    - DISABLED: Don't install anything
    - DRY_RUN: Show what would be installed but don't install
    """
    
    __slots__ = ('_package_name', '_enabled', '_mode', '_installed_packages', 
                 '_failed_packages', '_lock')
    
    def __init__(self, package_name: str = 'default'):
        """
        Initialize package installer.
        
        Args:
            package_name: Name of package this installer is for (for isolation)
        """
        self._package_name = package_name
        self._enabled = False
        self._mode = LazyInstallMode.AUTO
        self._installed_packages: Set[str] = set()
        self._failed_packages: Set[str] = set()
        self._lock = threading.RLock()
    
    def get_package_name(self) -> str:
        """Get the package name this installer is for."""
        return self._package_name
    
    def set_mode(self, mode: LazyInstallMode) -> None:
        """Set the installation mode."""
        with self._lock:
            self._mode = mode
    
    def get_mode(self) -> LazyInstallMode:
        """Get the current installation mode."""
        return self._mode
    
    def enable(self) -> None:
        """Enable lazy installation."""
        with self._lock:
            self._enabled = True
    
    def disable(self) -> None:
        """Disable lazy installation."""
        with self._lock:
            self._enabled = False
    
    def is_enabled(self) -> bool:
        """Check if lazy installation is enabled."""
        return self._enabled
    
    @abstractmethod
    def install_package(self, package_name: str, module_name: str = None) -> bool:
        """
        Install a package (abstract method).
        
        Args:
            package_name: Name of package to install
            module_name: Name of module being imported (for interactive mode)
            
        Returns:
            True if installation successful, False otherwise
        """
        pass
    
    @abstractmethod
    def _check_security_policy(self, package_name: str) -> Tuple[bool, str]:
        """
        Check security policy for package (abstract method).
        
        Args:
            package_name: Package to check
            
        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        pass
    
    @abstractmethod
    def _run_pip_install(self, package_name: str, args: List[str]) -> bool:
        """
        Run pip install with arguments (abstract method).
        
        Args:
            package_name: Package to install
            args: Additional pip arguments
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get installation statistics."""
        with self._lock:
            return {
                'enabled': self._enabled,
                'mode': self._mode.value,
                'package_name': self._package_name,
                'installed_packages': list(self._installed_packages),
                'failed_packages': list(self._failed_packages),
                'total_installed': len(self._installed_packages),
                'total_failed': len(self._failed_packages)
            }


# =============================================================================
# ABSTRACT IMPORT HOOK (Observer Pattern)
# =============================================================================

class AImportHook(IImportHook, ABC):
    """
    Abstract base for import hooks.
    
    Implements Observer pattern to observe import failures and trigger
    lazy installation when needed.
    """
    
    __slots__ = ('_package_name', '_enabled')
    
    def __init__(self, package_name: str = 'default'):
        """
        Initialize import hook.
        
        Args:
            package_name: Package this hook is for
        """
        self._package_name = package_name
        self._enabled = True
    
    def enable(self) -> None:
        """Enable the import hook."""
        self._enabled = True
    
    def disable(self) -> None:
        """Disable the import hook."""
        self._enabled = False
    
    def is_enabled(self) -> bool:
        """Check if hook is enabled."""
        return self._enabled
    
    @abstractmethod
    def install_hook(self) -> None:
        """Install the import hook into sys.meta_path (abstract method)."""
        pass
    
    @abstractmethod
    def uninstall_hook(self) -> None:
        """Uninstall the import hook from sys.meta_path (abstract method)."""
        pass
    
    @abstractmethod
    def handle_import_error(self, module_name: str) -> Optional[Any]:
        """
        Handle ImportError by attempting to install and re-import (abstract method).
        
        Args:
            module_name: Name of module that failed to import
            
        Returns:
            Imported module if successful, None otherwise
        """
        pass


# =============================================================================
# ABSTRACT CACHE (Proxy Pattern)
# =============================================================================

class APackageCache(IPackageCache, ABC):
    """
    Abstract base for package caching.
    
    Implements Proxy pattern to provide cached access to packages
    and avoid repeated operations.
    """
    
    __slots__ = ('_cache', '_lock')
    
    def __init__(self):
        """Initialize package cache."""
        self._cache: Dict[str, Any] = {}
        self._lock = threading.RLock()
    
    @abstractmethod
    def get_cached(self, key: str) -> Optional[Any]:
        """
        Get cached value (abstract method).
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        pass
    
    @abstractmethod
    def set_cached(self, key: str, value: Any) -> None:
        """
        Set cached value (abstract method).
        
        Args:
            key: Cache key
            value: Value to cache
        """
        pass
    
    def clear_cache(self) -> None:
        """Clear all cached values."""
        with self._lock:
            self._cache.clear()
    
    @abstractmethod
    def is_cache_valid(self, key: str) -> bool:
        """
        Check if cache entry is still valid (abstract method).
        
        Args:
            key: Cache key
            
        Returns:
            True if valid, False otherwise
        """
        pass


# =============================================================================
# ABSTRACT LAZY LOADER (Proxy Pattern)
# =============================================================================

class ALazyLoader(ILazyLoader, ABC):
    """
    Abstract base for lazy loading.
    
    Implements Proxy pattern to defer module loading until first access.
    """
    
    __slots__ = ('_module_path', '_cached_module', '_lock', '_loading')
    
    def __init__(self, module_path: str):
        """
        Initialize lazy loader.
        
        Args:
            module_path: Full module path to load
        """
        self._module_path = module_path
        self._cached_module: Optional[ModuleType] = None
        self._lock = threading.RLock()
        self._loading = False
    
    @abstractmethod
    def load_module(self, module_path: str) -> ModuleType:
        """
        Load a module lazily (abstract method).
        
        Args:
            module_path: Full module path to load
            
        Returns:
            Loaded module
        """
        pass
    
    def is_loaded(self, module_path: str = None) -> bool:
        """
        Check if module is already loaded.
        
        Args:
            module_path: Module path to check (uses self._module_path if None)
            
        Returns:
            True if loaded, False otherwise
        """
        return self._cached_module is not None
    
    @abstractmethod
    def unload_module(self, module_path: str) -> None:
        """
        Unload a module from cache (abstract method).
        
        Args:
            module_path: Module path to unload
        """
        pass


# =============================================================================
# EXPORT ALL
# =============================================================================

__all__ = [
    # Abstract base classes
    'APackageDiscovery',
    'APackageInstaller',
    'AImportHook',
    'APackageCache',
    'ALazyLoader',
]

