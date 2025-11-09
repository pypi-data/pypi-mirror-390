"""
exonware package - Enterprise-grade Python framework ecosystem

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.388
Generation Date: September 04, 2025

This is a namespace package allowing multiple exonware subpackages
to coexist (xwsystem, xwnode, xwdata, etc.)
"""

# Make this a namespace package
__path__ = __import__('pkgutil').extend_path(__path__, __name__)

# Only import version if xwsystem is available (lazy import)
try:
    from .xwsystem.version import __version__
except ImportError:
    __version__ = '0.0.1'

__author__ = 'Eng. Muhammad AlShehri'
__email__ = 'connect@exonware.com'
__company__ = 'eXonware.com'
