# -*- coding: utf-8 -*-
"""
日志记录和错误处理模块
"""

from __future__ import print_function
import sys


def setup_logging(verbose=False):
    """设置统一的日志格式"""
    # Python 2.7 兼容性处理 - 动态导入 logging 模块并添加缺失的功能
    import logging
    
    # 确保在Python 2.7中也能正确导入logging模块常量
    if not hasattr(logging, 'INFO'):
        logging.INFO = 20
    if not hasattr(logging, 'DEBUG'):
        logging.DEBUG = 10
    if not hasattr(logging, 'WARNING'):
        logging.WARNING = 30
    if not hasattr(logging, 'ERROR'):
        logging.ERROR = 40
    if not hasattr(logging, 'CRITICAL'):
        logging.CRITICAL = 50
    
    level = logging.DEBUG if verbose else logging.INFO
    
    # 确保至少有一个处理器
    try:
        if hasattr(logging, 'getLogger'):
            root_logger = logging.getLogger()
        else:
            # 如果没有 getLogger，尝试使用 root 属性
            root_logger = getattr(logging, 'root', None)
            
        if root_logger is not None:
            if not hasattr(root_logger, 'handlers') or not root_logger.handlers:
                # 添加一个默认的处理器以避免 "No handlers could be found" 警告
                try:
                    if hasattr(logging, 'StreamHandler'):
                        handler = logging.StreamHandler(sys.stdout)
                        if hasattr(logging, 'Formatter'):
                            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                            handler.setFormatter(formatter)
                        root_logger.addHandler(handler)
                except:
                    # 如果无法创建处理器，至少确保日志级别被设置
                    pass
            root_logger.setLevel(level)
    except:
        # 忽略日志初始化错误
        pass
    
    # Python 2.7 兼容性处理
    if hasattr(logging, 'basicConfig'):
        # Python 2.7.9+ 和 Python 3 中有 basicConfig 函数
        try:
            # 尝试使用 handlers 参数
            logging.basicConfig(
                level=level,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[logging.StreamHandler(sys.stdout)]
            )
        except (TypeError, AttributeError):
            # 更早版本的 Python 2.7 不支持 handlers 参数
            try:
                logging.basicConfig(
                    level=level,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            except:
                pass
    else:
        # 如果没有 basicConfig 函数，则手动配置根日志记录器
        try:
            if hasattr(logging, 'getLogger'):
                root_logger = logging.getLogger()
            else:
                root_logger = getattr(logging, 'root', None)
                
            if root_logger is not None:
                root_logger.setLevel(level)
                
                # 清除现有的处理器
                if hasattr(root_logger, 'handlers'):
                    for handler in root_logger.handlers[:]:
                        root_logger.removeHandler(handler)
                    
                    # 添加新的处理器
                    if hasattr(logging, 'StreamHandler'):
                        try:
                            handler = logging.StreamHandler(sys.stdout)
                        except:
                            # 如果无法创建 StreamHandler，使用备用方案
                            handler = None
                    else:
                        handler = None
                        
                    if handler is not None:
                        if hasattr(logging, 'Formatter'):
                            try:
                                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                                handler.setFormatter(formatter)
                            except:
                                pass  # 忽略格式化器错误
                        
                        try:
                            root_logger.addHandler(handler)
                        except:
                            pass  # 忽略添加处理器的错误
        except:
            pass


class PackageError(Exception):
    """自定义打包异常"""
    pass


def handle_error(error, message=""):
    """统一的错误处理"""
    # Python 2.7 兼容性处理 - 动态导入 logging 模块
    import logging
    
    # 尝试使用 logging 记录错误，如果失败则直接打印
    try:
        # 检查是否有 getLogger 函数
        if hasattr(logging, 'getLogger'):
            try:
                logger = logging.getLogger(__name__)
            except:
                # 如果无法获取特定名称的 logger，则使用 None
                logger = None
        else:
            logger = None
            
        if logger is not None:
            # 尝试记录错误日志
            try:
                logger.error("{0}: {1}".format(message, error))
            except:
                # 如果记录日志失败，则使用 print
                print("ERROR: {0}: {1}".format(message, error))
        else:
            # 直接使用 print 输出错误
            print("ERROR: {0}: {1}".format(message, error))
    except:
        # 最后的备用方案
        print("ERROR: {0}: {1}".format(message, error))
        
    # Python 2兼容的异常抛出方式
    new_error = PackageError("{0}: {1}".format(message, error))
    raise new_error