#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试Python 2.7兼容性
"""

import sys
print("Python version:", sys.version)

# 测试导入所有模块
try:
    from src.PyInstallerEx.core.config import PackageConfig
    print("✓ PackageConfig imported successfully")
    
    # 测试配置类功能
    config = PackageConfig()
    print("✓ PackageConfig instance created")
    
    config_dict = config.to_dict()
    print("✓ to_dict() method works")
    
    config.validate()
    print("✓ validate() method works")
    
    rendered = config.render_template("test_script", "abc123")
    print("✓ render_template() method works")
    
except Exception as e:
    print("✗ PackageConfig failed:", str(e))

try:
    from src.PyInstallerEx.utils.file_utils import FileUtils
    print("✓ FileUtils imported successfully")
    
    # 测试文件工具功能
    script_name = FileUtils.get_script_name("/path/to/test.py")
    print("✓ get_script_name() method works")
    
except Exception as e:
    print("✗ FileUtils failed:", str(e))

try:
    from src.PyInstallerEx.utils.compression import CompressionUtils
    print("✓ CompressionUtils imported successfully")
except Exception as e:
    print("✗ CompressionUtils failed:", str(e))

try:
    from src.PyInstallerEx.utils.system_utils import SystemInfo
    print("✓ SystemInfo imported successfully")
    
    platform = SystemInfo.get_platform()
    print("✓ get_platform() method works:", platform)
    
except Exception as e:
    print("✗ SystemInfo failed:", str(e))

try:
    from src.PyInstallerEx.utils.logging import setup_logging, PackageError
    print("✓ Logging utilities imported successfully")
    
    setup_logging(verbose=False)
    print("✓ setup_logging() method works")
    
except Exception as e:
    print("✗ Logging utilities failed:", str(e))

try:
    from src.PyInstallerEx.core.packager import PackageBuilder
    print("✓ PackageBuilder imported successfully")
except Exception as e:
    print("✗ PackageBuilder failed:", str(e))

print("\n=== Python 2.7 Compatibility Test Complete ===")
print("All core modules should work with Python 2.7+")