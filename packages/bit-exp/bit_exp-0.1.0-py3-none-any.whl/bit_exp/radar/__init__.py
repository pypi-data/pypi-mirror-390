"""
bit_exp.radar - 雷达信号处理模块

提供雷达数据处理的各种功能，包括：
- bin2mat: 二进制数据转换为MATLAB格式
- RDimaging: 距离-多普勒成像
- ATimaging: 角度-时间成像
- processing: 批处理和流程管理
"""

from .bin2mat import run as bin2mat
from .RDimaging import run as rdimaging
from .ATimaging import run as atimaging
from .processing import process_data, process_folder

__all__ = [
    'bin2mat',
    'rdimaging',
    'atimaging',
    'process_data',
    'process_folder',
]
