"""
pyRofex-To-Excel

Aplicación en Python para obtener y gestionar datos de mercado
con integración a Excel usando la API de pyRofex.
"""

from importlib.metadata import PackageNotFoundError, version as package_version


try:
	__version__ = package_version("pyrofex-to-excel")
except PackageNotFoundError:
	__version__ = "unknown"

__author__ = "pyRofex-To-Excel"
__email__ = "your.email@domain.com"

# Public API exports
from .main import main

__all__ = ["main"]
