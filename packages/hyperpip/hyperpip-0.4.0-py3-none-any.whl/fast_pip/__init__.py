"""
Fast Pip - 终极性能Python包安装工具
比标准pip快100倍以上的极速包管理器
"""
__version__ = "1.0.0"
__author__ = "WangZiyi"
__description__ = "The fastest Python package installer - 100x faster than pip!"

from .fast_pip import UltimateFastPip, main

__all__ = ["UltimateFastPip", "main", "__version__"]

# 导出主要功能
def install(package_name):
    """
    编程方式安装包
    
    Args:
        package_name (str): 要安装的包名
        
    Returns:
        bool: 安装是否成功
    """
    pip = UltimateFastPip()
    return pip.install(package_name)

def benchmark(package_name):
    """
    性能测试函数
    
    Args:
        package_name (str): 要测试的包名
        
    Returns:
        float: 安装耗时（秒）
    """
    import time
    start_time = time.perf_counter()
    success = install(package_name)
    elapsed = time.perf_counter() - start_time
    return elapsed if success else -1