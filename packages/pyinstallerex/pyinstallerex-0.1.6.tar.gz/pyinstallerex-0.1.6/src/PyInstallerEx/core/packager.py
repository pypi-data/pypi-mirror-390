# -*- coding: utf-8 -*-
"""
核心打包逻辑模块
"""

from __future__ import print_function
import subprocess
import tempfile
import os
import logging
import sys
import json

from ..utils.system_utils import SystemInfo
from ..utils.file_utils import FileUtils
from ..utils.compression import CompressionUtils
from ..utils.logging import PackageError, handle_error
from .config import PackageConfig


class PackageBuilder(object):
    """包构建器类"""

    def __init__(self, config, verbose=False):
        self.config = config
        self.verbose = verbose
        self.logger = None
        self._initialize_logger()

    def _initialize_logger(self):
        """初始化日志系统"""
        try:
            # 尝试获取logger
            self.logger = logging.getLogger(__name__)
            # 确保logger有处理器
            if not self.logger.handlers:
                # 添加一个默认处理器
                handler = logging.StreamHandler(sys.stdout)
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
                self.logger.setLevel(logging.INFO)
        except:
            # 如果日志初始化失败，使用备用方案
            class DummyLogger:
                def info(self, msg):
                    print("INFO: {0}".format(msg))

                def warning(self, msg):
                    print("WARNING: {0}".format(msg))

                def error(self, msg):
                    print("ERROR: {0}".format(msg))

                def debug(self, msg):
                    if self.verbose:
                        print("DEBUG: {0}".format(msg))

            self.logger = DummyLogger()

    def build(self, script_path, output_dir=None):
        """执行完整的打包流程"""
        try:
            # 1. 验证输入
            self._validate_inputs(script_path, output_dir)

            # 2. 调用PyInstaller --onedir打包
            pyinstaller_dir = self._run_pyinstaller(script_path)

            # 3. 处理配置文件
            rendered_config = self._process_configuration(script_path, pyinstaller_dir)

            # 4. 压缩目录为ZIP文件
            zip_path = self._compress_directory(pyinstaller_dir)

            # 5. 获取对应的二进制启动器
            binary_path = self._get_binary_launcher()

            # 6. 合并为最终的单文件
            final_output = self._combine_final_file(binary_path, zip_path, output_dir, script_path)

            return final_output

        except Exception as e:
            handle_error(e, "Packaging process failed")

    def _validate_inputs(self, script_path, output_dir):
        """验证输入参数"""
        if not os.path.exists(script_path):
            raise PackageError("Script file not found: {0}".format(script_path))

        if output_dir and not os.path.exists(output_dir):
            FileUtils.ensure_directory_exists(output_dir)

        self.config.validate()

    def _run_pyinstaller(self, script_path):
        """步骤1: 调用PyInstaller --onedir打包"""
        self.logger.info("Step 1: Running PyInstaller...")

        # 获取脚本的绝对路径和所在目录
        script_path = os.path.abspath(script_path)
        script_dir = os.path.dirname(script_path)

        # 在脚本所在目录创建临时工作目录
        work_dir = os.path.join(script_dir, "_pyinstallerex_temp")
        FileUtils.ensure_directory_exists(work_dir)

        # 清理之前的输出目录
        dist_dir = os.path.join(work_dir, "dist")
        if os.path.exists(dist_dir):
            import shutil
            shutil.rmtree(dist_dir)

        # 构建PyInstaller命令（添加-y选项自动覆盖）
        cmd = [
            "pyinstaller",
            "--onedir",
            "--distpath", os.path.abspath(dist_dir),
            "--workpath", os.path.abspath(os.path.join(work_dir, "build")),
            "--specpath", os.path.abspath(work_dir),
            "--clean",
            "-y",  # 自动覆盖现有输出目录
            script_path  # 使用完整路径
        ]

        if self.verbose:
            cmd.append("--log-level")
            cmd.append("DEBUG")

        self.logger.debug("Running command: {0}".format(" ".join(cmd)))

        try:
            # 在脚本目录中运行PyInstaller
            result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    cwd=script_dir, universal_newlines=True)
            stdout, stderr = result.communicate()

            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, cmd, stderr)

            if self.verbose:
                self.logger.debug("PyInstaller output: {0}".format(stdout))
                self.logger.debug("PyInstaller errors: {0}".format(stderr))
        except subprocess.CalledProcessError as e:
            raise PackageError("PyInstaller failed: {0}".format(e.output or e.stderr))

        # 等待一段时间确保文件系统同步
        import time
        time.sleep(1)

        # 查找生成的目录（直接在dist目录下）
        if not os.path.exists(dist_dir):
            self.logger.error("PyInstaller dist directory not found: {0}".format(dist_dir))
            if os.path.exists(work_dir):
                self.logger.error("Current contents of work_dir: {0}".format(os.listdir(work_dir)))
            raise PackageError("PyInstaller output directory not found: {0}".format(dist_dir))

        # 获取dist目录下的内容
        dist_contents = os.listdir(dist_dir)
        if not dist_contents:
            self.logger.error("PyInstaller dist directory is empty: {0}".format(dist_dir))
            raise PackageError("PyInstaller output directory is empty: {0}".format(dist_dir))

        # PyInstaller在dist目录下创建了脚本名称的目录
        script_name = FileUtils.get_script_name(script_path)
        expected_dist_path = os.path.join(dist_dir, script_name)

        # 检查预期的目录是否存在
        if os.path.exists(expected_dist_path):
            self.logger.info("Found PyInstaller output directory: {0}".format(expected_dist_path))
            return expected_dist_path
        else:
            # 如果预期目录不存在，但dist目录中有内容，则使用dist目录
            self.logger.warning("Expected PyInstaller output directory not found: {0}".format(expected_dist_path))
            self.logger.info("Using dist directory: {0}".format(dist_dir))
            self.logger.info("Contents of dist directory: {0}".format(dist_contents))
            return dist_dir

    def _get_binary_launcher(self):
        """获取对应平台的二进制启动器"""
        # 确定平台
        system_info = SystemInfo()
        platform_name = system_info.get_platform()

        # 根据平台选择启动器（处理不同平台名称）
        if platform_name in ["windows", "win"]:
            launcher_name = "launcher_windows.exe" if sys.maxsize > 2**32 else "launcher_windows.exe"
        elif platform_name in ["linux", "linux2", "linux_x86"]:
            launcher_name = "launcher_linux_x86"
        elif platform_name in ["linux_arm"]:
            launcher_name = "launcher_linux_arm"
        elif platform_name in ["linux_arm64"]:
            launcher_name = "launcher_linux_arm64"
        else:
            raise PackageError("Unsupported platform: {0}".format(platform_name))

        # 多种方式查找启动器文件
        launcher_paths = []
        
        # 1. 首先尝试从安装包的数据文件中查找启动器
        try:
            import pkg_resources
            launcher_path = pkg_resources.resource_filename(
                'pyinstallerex', 
                'bin/' + launcher_name
            )
            launcher_paths.append(launcher_path)
        except:
            pass

        # 2. 尝试从包数据中查找启动器 (新增)
        try:
            import pkg_resources
            launcher_path = pkg_resources.resource_filename(
                'PyInstallerEx', 
                '../bin/' + launcher_name
            )
            launcher_paths.append(launcher_path)
        except:
            pass

        # 3. 尝试从源码目录查找启动器
        launcher_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),  # src/PyInstallerEx
            "..",  # src
            "..",  # 项目根目录
            "bin",
            launcher_name
        )
        launcher_paths.append(os.path.abspath(launcher_path))
        
        # 4. 尝试从site-packages的数据目录查找启动器
        try:
            # 获取当前模块的路径
            current_module_path = os.path.dirname(os.path.abspath(__file__))
            # 构造从site-packages开始的路径
            launcher_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(current_module_path))),  # site-packages
                "..",  # 安装根目录
                "bin",
                launcher_name
            )
            launcher_paths.append(os.path.abspath(launcher_path))
        except:
            pass
        
        # 5. 尝试从通过data_files安装的数据目录查找启动器
        try:
            import sys
            # 查找通过data_files安装的文件通常在site-packages/pyinstallerex-<version>.data/data/bin目录下
            for path in sys.path:
                # 检查标准的data_files安装路径
                launcher_path = os.path.join(
                    path, 
                    "pyinstallerex-" + self.__class__.__module__.split('.')[0] + ".data", 
                    "data", 
                    "bin", 
                    launcher_name
                )
                launcher_paths.append(os.path.abspath(launcher_path))
                
                # 检查另一种可能的安装路径
                launcher_path = os.path.join(
                    path, 
                    "pyinstallerex-" + "0.1.2" + ".data", 
                    "data", 
                    "bin", 
                    launcher_name
                )
                launcher_paths.append(os.path.abspath(launcher_path))
                
                # 检查site-packages下的bin目录（直接安装）
                launcher_path = os.path.join(path, "bin", launcher_name)
                launcher_paths.append(os.path.abspath(launcher_path))
        except:
            pass

        # 6. 尝试从标准数据目录查找
        try:
            import sys
            for path in sys.path:
                launcher_path = os.path.join(path, "bin", launcher_name)
                launcher_paths.append(os.path.abspath(launcher_path))
        except:
            pass

        # 查找第一个存在的启动器文件
        found_launcher_path = None
        for launcher_path in launcher_paths:
            if os.path.exists(launcher_path):
                found_launcher_path = launcher_path
                break

        # 如果找不到启动器文件，则提供详细的错误信息
        if not found_launcher_path:
            error_msg = "Binary launcher not found: {0}".format(launcher_name)
            error_msg += "\nSearched platform: {0}".format(platform_name)
            error_msg += "\nTried paths:"
            for path in launcher_paths:
                error_msg += "\n  - {0} (exists: {1})".format(path, os.path.exists(path))
            raise PackageError(error_msg)

        self.logger.info("Using binary launcher: {0}".format(found_launcher_path))
        return found_launcher_path

    def _process_configuration(self, script_path, pyinstaller_dir):
        """处理配置文件"""
        # 获取脚本名称
        script_name = FileUtils.get_script_name(script_path)

        # 生成配置内容
        config_data = {
            "main": "{0}/{0}".format(script_name),
            "name": self.config.filename or script_name,
            "version": self.config.version or "1.0.0",
            "description": self.config.description or "Application packaged with PyInstallerEx",
            "tmp_dir": self.config.tmp_dir or "ex_{name}_{md5}",
            "author": self.config.author or "Unknown"
        }

        # 渲染配置为JSON
        rendered_config = json.dumps(config_data, indent=2, ensure_ascii=False)

        # 将配置写入PyInstaller输出目录
        config_path = FileUtils.copy_config_to_dir(rendered_config, pyinstaller_dir, "ex.config.json")

        self.logger.info("Configuration written to: {0}".format(config_path))
        return rendered_config

    def _compress_directory(self, directory):
        """压缩目录为ZIP文件"""
        self.logger.info("Step 4: Compressing directory to ZIP...")

        # 创建临时ZIP文件路径
        zip_path = directory + ".zip"

        # 压缩目录
        CompressionUtils.create_zip_from_directory(directory, zip_path)

        self.logger.info("ZIP file created: {0}".format(zip_path))
        return zip_path

    def _combine_final_file(self, binary_path, zip_path, output_dir, script_path):
        """合并启动器和ZIP文件为最终输出"""
        self.logger.info("Step 6: Combining launcher and ZIP file...")

        # 确定输出目录
        if output_dir is None:
            output_dir = os.path.dirname(script_path)

        FileUtils.ensure_directory_exists(output_dir)

        # 确定输出文件名
        script_name = FileUtils.get_script_name(script_path)
        if SystemInfo().get_platform() in ["windows", "win"]:
            output_filename = script_name + ".exe"
        else:
            output_filename = script_name

        output_path = os.path.join(output_dir, output_filename)

        # 合并文件
        with open(output_path, "wb") as output_file:
            # 写入启动器
            with open(binary_path, "rb") as launcher_file:
                output_file.write(launcher_file.read())

            # 追加ZIP数据
            with open(zip_path, "rb") as zip_file:
                output_file.write(zip_file.read())

        # 在Unix系统上设置可执行权限
        if SystemInfo().get_platform() not in ["windows", "win"]:
            os.chmod(output_path, 0o755)

        self.logger.info("Final executable created: {0}".format(output_path))
        return output_path