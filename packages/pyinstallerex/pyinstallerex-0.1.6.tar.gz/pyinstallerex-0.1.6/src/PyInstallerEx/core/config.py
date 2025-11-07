# -*- coding: utf-8 -*-
"""
配置管理模块
"""

from __future__ import print_function
import json
import os
import hashlib


class PackageConfig(object):
    """打包配置数据类"""
    
    def __init__(self, filename="{filename}", version="1.0.0", installer=None, 
                 tmp_dir="ex_{filename}_{md5}", description="Application packaged with PyInstallerEx", 
                 author="Unknown"):
        self.filename = filename
        self.version = version
        self.installer = installer
        self.tmp_dir = tmp_dir
        self.description = description
        self.author = author
    
    @classmethod
    def from_file(cls, config_path):
        """从配置文件加载配置"""
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
            return cls(**data)
        except (ValueError, IOError) as e:
            raise ValueError("Invalid configuration file {0}: {1}".format(config_path, e))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'filename': self.filename,
            'version': self.version,
            'installer': self.installer,
            'tmp_dir': self.tmp_dir,
            'description': self.description,
            'author': self.author
        }
    
    def validate(self):
        """验证配置有效性"""
        # 不再强制要求filename必须指定，因为会在运行时根据脚本名设置
        if not self.version:
            raise ValueError("Version must be specified")
        return True
    
    def render_template(self, script_name, script_md5):
        """渲染配置模板，替换占位符"""
        filename = self.filename.replace("{filename}", script_name)
        tmp_dir = self.tmp_dir.replace("{filename}", script_name).replace("{md5}", script_md5)
        
        # 处理installer默认值
        installer = self.installer
        if not installer:
            if os.name == 'nt':  # Windows
                installer = os.environ.get('TEMP', '/tmp')
            else:  # Unix/Linux
                installer = '/tmp'
        
        return PackageConfig(
            filename=filename,
            version=self.version,
            installer=installer,
            tmp_dir=tmp_dir,
            description=self.description,
            author=self.author
        )
    
    def save_to_file(self, output_path):
        """保存配置到文件"""
        with open(output_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)