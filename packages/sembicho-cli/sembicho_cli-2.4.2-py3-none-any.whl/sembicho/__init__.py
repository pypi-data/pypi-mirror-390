"""
SemBicho - Static Application Security Testing Tool
Paquete principal para análisis estático de seguridad
"""

__version__ = "1.0.0"
__author__ = "SemBicho Team"
__license__ = "MIT"

from .scanner import SemBichoScanner, Vulnerability, ScanResult

"""
SemBicho Scanner Package
"""

try:
    from .__version__ import __version__
except ImportError:
    __version__ = "2.1.4"

__all__ = ['SemBichoScanner', '__version__']