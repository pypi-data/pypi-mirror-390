"""
定制的、快速的启用基础层

 * 通常用于【分层架构】、【洋葱架构】
 * 提供的层：
    > LPrint： 输出层、日志层


"""
from .lprint import LPrint

# 依赖库
from .lp_impl import *

__all__ = ['LPrint']

