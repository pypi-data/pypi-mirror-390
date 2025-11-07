# -*- coding: utf-8 -*-
"""
压缩和解压工具模块
"""

from __future__ import print_function
import zipfile
import shutil
import os


class CompressionUtils(object):
    """压缩工具类"""
    
    @staticmethod
    def create_zip_from_directory(source_dir, zip_path):
        """将目录压缩为ZIP文件"""
        def add_files_to_zip(zipf, folder, base_path=""):
            for item in os.listdir(folder):
                item_path = os.path.join(folder, item)
                arcname = os.path.join(base_path, item)
                
                if os.path.isfile(item_path):
                    zipf.write(item_path, arcname)
                elif os.path.isdir(item_path):
                    add_files_to_zip(zipf, item_path, arcname)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            add_files_to_zip(zipf, source_dir)
    
    @staticmethod
    def combine_binary_and_zip(binary_path, zip_path, output_path):
        """将二进制文件和ZIP文件合并为单个二进制文件"""
        # 简单的文件合并：二进制文件 + ZIP文件
        with open(output_path, 'wb') as outfile:
            # 先写入二进制启动器
            with open(binary_path, 'rb') as binfile:
                outfile.write(binfile.read())
            
            # 写入分隔符（可选，用于识别ZIP部分）
            outfile.write(b'\x50\x4B\x03\x04')  # ZIP文件头作为分隔符
            
            # 再写入ZIP文件内容
            with open(zip_path, 'rb') as zipfile:
                outfile.write(zipfile.read())
    
    @staticmethod
    def extract_zip_from_combined(combined_path, output_dir):
        """从合并文件中提取ZIP部分"""
        # 这里需要根据实际的合并格式来实现
        # 简化实现：假设ZIP部分在特定偏移量开始
        with open(combined_path, 'rb') as infile:
            content = infile.read()
        
        # 查找ZIP文件头位置
        zip_header = b'\x50\x4B\x03\x04'
        zip_start = content.find(zip_header)
        
        if zip_start == -1:
            raise ValueError("Could not find ZIP section in combined file")
        
        # 提取ZIP部分
        zip_content = content[zip_start:]
        zip_output_path = os.path.join(output_dir, "extracted.zip")
        
        with open(zip_output_path, 'wb') as zipfile:
            zipfile.write(zip_content)
        
        return zip_output_path