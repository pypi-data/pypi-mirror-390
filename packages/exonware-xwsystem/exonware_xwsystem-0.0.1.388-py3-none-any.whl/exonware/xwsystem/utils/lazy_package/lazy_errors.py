"""
#exonware/xwsystem/src/exonware/xwsystem/utils/lazy_package/lazy_errors.py

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.388
Generation Date: 10-Oct-2025

Errors for Lazy Loading System

This module defines all exception classes for the lazy loading system
following DEV_GUIDELINES.md structure.
"""

from typing import Optional


# =============================================================================
# BASE EXCEPTION
# =============================================================================

class LazySystemError(Exception):
    """
    Base exception for all lazy system errors.
    
    All lazy system exceptions inherit from this for easy error handling.
    """
    
    def __init__(self, message: str, package_name: Optional[str] = None):
        """
        Initialize lazy system error.
        
        Args:
            message: Error message
            package_name: Optional package name for scoped errors
        """
        self.package_name = package_name
        if package_name:
            message = f"[{package_name}] {message}"
        super().__init__(message)


# =============================================================================
# SPECIFIC EXCEPTIONS
# =============================================================================

class LazyInstallError(LazySystemError):
    """
    Raised when package installation fails.
    
    Examples:
        - pip install command fails
        - Package not found in PyPI
        - Network error during installation
    """
    pass


class LazyDiscoveryError(LazySystemError):
    """
    Raised when dependency discovery fails.
    
    Examples:
        - Cannot read pyproject.toml
        - Invalid TOML syntax
        - Missing dependency configuration
    """
    pass


class LazyHookError(LazySystemError):
    """
    Raised when import hook operation fails.
    
    Examples:
        - Cannot install hook in sys.meta_path
        - Hook is already installed
        - Hook interception fails
    """
    pass


class LazySecurityError(LazySystemError):
    """
    Raised when security policy is violated.
    
    Examples:
        - Package not in allow list
        - Package in deny list
        - Untrusted package source
    """
    pass


class ExternallyManagedError(LazyInstallError):
    """
    Raised when environment is externally managed (PEP 668).
    
    This happens when the Python environment has an EXTERNALLY-MANAGED
    marker file, preventing pip installations. Common in system Python
    installations on Linux distributions.
    
    Solutions:
        1. Use a virtual environment
        2. Use pipx for isolated installations
        3. Override with --break-system-packages (not recommended)
    """
    
    def __init__(self, package_name: str):
        """
        Initialize externally managed error.
        
        Args:
            package_name: Package that cannot be installed
        """
        message = (
            f"Cannot install '{package_name}': Environment is externally managed (PEP 668). "
            f"Please use a virtual environment or pipx."
        )
        super().__init__(message, package_name=None)


class DeferredImportError(Exception):
    """
    Placeholder for a failed import that will be retried when accessed.
    
    This enables two-stage lazy loading:
    - Stage 1: Import fails → Return DeferredImportError placeholder
    - Stage 2: On first use → Install missing package and replace with real module
    
    Performance optimized:
    - Zero overhead until user actually accesses the deferred import
    - Only installs dependencies when truly needed
    - Caches successful imports to avoid repeated installs
    
    Note: This is both an error class and a proxy object. It stays in
    lazy_errors.py because it represents an error state, but acts as
    a proxy until resolved.
    """
    
    __slots__ = ('_import_name', '_original_error', '_installer_package', '_retry_attempted', '_real_module')
    
    def __init__(self, import_name: str, original_error: Exception, installer_package: str):
        """
        Initialize deferred import placeholder.
        
        Args:
            import_name: Name of the module that failed to import (e.g., 'fastavro')
            original_error: The original ImportError that was caught
            installer_package: Package name to use for lazy installation (e.g., 'xwsystem')
        """
        self._import_name = import_name
        self._original_error = original_error
        self._installer_package = installer_package
        self._retry_attempted = False
        self._real_module = None
        super().__init__(f"Deferred import: {import_name}")
    
    def _try_install_and_import(self):
        """
        Attempt to install missing package and import it.
        
        Returns:
            The real module if installation succeeds
            
        Raises:
            Original ImportError if installation fails or is disabled
        """
        # Import here to avoid circular imports
        from ..lazy_package.lazy_core import lazy_import_with_install, is_lazy_install_enabled
        from ...config.logging_setup import get_logger
        
        logger = get_logger("xwsystem.utils.lazy_package")
        logger.info(f"[STAGE 2] _try_install_and_import called for '{self._import_name}'")
        
        # Return cached module if already installed
        if self._real_module is not None:
            logger.info(f"[STAGE 2] Using cached module for '{self._import_name}'")
            return self._real_module
        
        # Only try once to avoid repeated failures
        if self._retry_attempted:
            logger.warning(f"[STAGE 2] Already attempted installation for '{self._import_name}', raising original error")
            raise self._original_error
        
        self._retry_attempted = True
        
        if not is_lazy_install_enabled(self._installer_package):
            logger.warning(f"[STAGE 2] Lazy install disabled for {self._installer_package}, cannot load {self._import_name}")
            raise self._original_error
        
        logger.info(f"⏳ [STAGE 2] Installing '{self._import_name}' on first use...")
        
        # Try to install and import
        module, success = lazy_import_with_install(
            self._import_name,
            installer_package=self._installer_package
        )
        
        if success and module:
            self._real_module = module
            logger.info(f"✅ [STAGE 2] Successfully installed and loaded '{self._import_name}'")
            return module
        else:
            logger.error(f"❌ [STAGE 2] Failed to install '{self._import_name}'")
            raise self._original_error
    
    def __call__(self, *args, **kwargs):
        """
        When user tries to instantiate, install dependency first.
        
        This enables: serializer = AvroSerializer() → installs fastavro → creates instance
        """
        module = self._try_install_and_import()
        # If module is callable (a class), instantiate it
        if callable(module):
            return module(*args, **kwargs)
        return module
    
    def __getattr__(self, name):
        """
        When user accesses attributes, install dependency first.
        
        This enables: from fastavro import reader → installs fastavro → returns reader
        """
        module = self._try_install_and_import()
        return getattr(module, name)
    
    def __repr__(self):
        """Show helpful message about deferred import."""
        if self._real_module is not None:
            return f"<DeferredImport: {self._import_name} (loaded)>"
        return f"<DeferredImport: {self._import_name} (will install on first use)>"


# =============================================================================
# EXPORT ALL
# =============================================================================

__all__ = [
    # Base exception
    'LazySystemError',
    # Specific exceptions
    'LazyInstallError',
    'LazyDiscoveryError',
    'LazyHookError',
    'LazySecurityError',
    'ExternallyManagedError',
    # Two-stage loading
    'DeferredImportError',
]

