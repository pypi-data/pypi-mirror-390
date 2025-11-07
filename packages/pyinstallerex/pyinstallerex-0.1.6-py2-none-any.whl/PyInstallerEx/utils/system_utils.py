# -*- coding: utf-8 -*-
"""
系统检测和平台相关工具
"""

from __future__ import print_function
import platform
import sys
import tempfile
import os


class SystemInfo(object):
    """系统信息检测类"""
    
    @staticmethod
    def get_platform():
        """获取当前平台标识"""
        system = platform.system().lower()
        arch = platform.machine().lower()
        
        if system == "windows":
            return "win"
        elif system == "linux":
            if "arm" in arch or "aarch" in arch:
                # 根据架构位数判断是arm还是arm64
                if "64" in arch or "aarch64" in arch:
                    return "linux_arm64"
                else:
                    return "linux_arm"
            else:
                return "linux_x86"
        else:
            raise ValueError("Unsupported platform: {0}_{1}".format(system, arch))
    
    @staticmethod
    def get_temp_dir():
        """获取系统临时目录"""
        return tempfile.gettempdir()
    
    @staticmethod
    def get_binary_name(platform_type):
        """根据平台类型获取对应的二进制启动器名称"""
        binary_map = {
            "win": "launcher_windows.exe",
            "linux_x86": "launcher_linux_x86",
            "linux_arm": "launcher_linux_arm",
            "linux_arm64": "launcher_linux_arm64"
        }
        
        if platform_type not in binary_map:
            raise ValueError("Unsupported platform type: {0}".format(platform_type))
        
        return binary_map[platform_type]
    
    @staticmethod
    def is_windows():
        """判断是否为Windows系统"""
        return platform.system().lower() in ["windows", "win32", "win64"]