#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyInstallerEx命令行入口点
"""

from __future__ import print_function
import argparse
import sys
import os

from .core.packager import PackageBuilder
from .core.config import PackageConfig
from .utils.logging import setup_logging
from .utils.file_utils import FileUtils


def main():
    """主函数 - 命令行接口"""
    parser = argparse.ArgumentParser(
        description="PyInstallerEx - Enhanced PyInstaller packaging tool",
        epilog="Example: python -m PyInstallerEx main.py --cfg config.json"
    )
    
    parser.add_argument("script", help="Python script to package")
    parser.add_argument("--cfg", "--config", dest="config", 
                       help="Custom configuration file path")
    parser.add_argument("--output", "-o", help="Output directory")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Verbose output")
    parser.add_argument("--name", "-n", help="Output filename (default: script name)")
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.verbose)
    
    try:
        # 加载配置
        if args.config:
            config = PackageConfig.from_file(args.config)
        else:
            # 使用默认配置
            config = PackageConfig()
        
        # 如果通过-n指定了名称，则覆盖配置中的filename
        if args.name:
            config.filename = args.name
        # 如果配置中filename仍然是默认值"{filename}"，则使用脚本名
        elif config.filename == "{filename}":
            script_name = FileUtils.get_script_name(args.script)
            config.filename = script_name
        
        # 创建构建器
        builder = PackageBuilder(config, verbose=args.verbose)
        
        # 执行打包
        script_path = args.script
        output_dir = args.output if args.output else None
        
        result_path = builder.build(script_path, output_dir)
        
        print("\n✅ Packaging completed successfully!")
        print("📦 Output file: {0}".format(result_path))
        
    except Exception as e:
        print("\n❌ Packaging failed: {0}".format(e), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()