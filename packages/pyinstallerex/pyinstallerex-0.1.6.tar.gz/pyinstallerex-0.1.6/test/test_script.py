#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试脚本 - 用于验证PyInstallerEx打包功能
"""

print("Hello from PyInstallerEx test script!")
print("Python version: {0}".format(__import__('sys').version))

if __name__ == "__main__":
    # 简单的用户交互测试
    try:
        name = raw_input("What's your name? ") if hasattr(__builtins__, 'raw_input') else input("What's your name? ")
        print("Hello, {0}!".format(name))
        print("Test script completed successfully.")
    except Exception as e:
        print("Error during execution: {0}".format(str(e)))
