"""
AGWR - 各向异性地理加权回归模型

一个用于实现各向异性地理加权回归(Variably Geographically Weighted Regression, VGWR)的Python包。
该包基于研究论文中的数学理论，提供了稳定、高效的VGWR模型实现。

主要功能:
- 各向异性核函数计算
- VGWR模型拟合和预测
- 空间变系数估计
- 模型诊断和评估

作者: AGWR开发团队
版本: 2.0.0
"""

from .vgwr import (
    VGWR,
    RV,
    CA_algorithm,
    RAV_function,
    rav_function,
    bv_function,
    vgwr_objective,
    plot_spatial_coefficients
)

__version__ = "2.0.0"
__author__ = "AGWR开发团队"

__all__ = [
    "VGWR",
    "RV",
    "CA_algorithm",
    "RAV_function",
    "rav_function",
    "bv_function",
    "vgwr_objective",
    "plot_spatial_coefficients"
]
