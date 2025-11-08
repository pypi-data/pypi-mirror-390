"""
MCP 证件照生成服务器

基于 Model Context Protocol (MCP) 的服务器，使用阿里云百炼 DashScope
通义万相-通用图像编辑生成标准证件照（支持一寸/二寸及白/蓝/红背景）。
"""

__version__ = "0.2.0"
__author__ = "fengjinchao"

# 导入主要模块和函数
from .server import main

__all__ = [
    "main",
]
