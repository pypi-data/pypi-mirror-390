# -*- coding: utf-8 -*-
"""
PyInstallerEx - Enhanced PyInstaller packaging tool
扩展PyInstaller使其拥有单文件安装功能
"""

__version__ = "0.0.1"
__author__ = "iiixxxiii"

from .core.packager import PackageBuilder
from .core.config import PackageConfig

__all__ = ["PackageBuilder", "PackageConfig"]