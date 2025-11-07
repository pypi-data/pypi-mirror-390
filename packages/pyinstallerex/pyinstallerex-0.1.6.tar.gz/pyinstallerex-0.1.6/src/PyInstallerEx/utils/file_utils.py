# -*- coding: utf-8 -*-
"""
文件操作工具函数
"""

from __future__ import print_function
import hashlib
import shutil
import os


class FileUtils(object):
    """文件操作工具类"""
    
    @staticmethod
    def calculate_md5(file_path):
        """计算文件的MD5哈希值"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    @staticmethod
    def copy_config_to_dir(config_content, target_dir, config_name="config.json"):
        """将配置内容复制到目标目录"""
        config_path = os.path.join(target_dir, config_name)
        with open(config_path, 'w') as f:
            f.write(config_content)
        return config_path
    
    @staticmethod
    def ensure_directory_exists(directory):
        """确保目录存在，不存在则创建"""
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    @staticmethod
    def clean_directory(directory):
        """清空目录内容"""
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.makedirs(directory)
    
    @staticmethod
    def get_script_name(script_path):
        """从脚本路径获取脚本名称（不含扩展名）"""
        base_name = os.path.basename(script_path)
        script_name = os.path.splitext(base_name)[0]
        return script_name