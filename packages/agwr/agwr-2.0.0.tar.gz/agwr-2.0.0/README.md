# AGWR - 各向异性地理加权回归模型 (VGWR)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/agwr.svg)](https://badge.fury.io/py/agwr)

一个用于实现各向异性地理加权回归(Variably Geographically Weighted Regression, VGWR)的Python包。该包基于研究论文中的数学理论，提供了稳定、高效的VGWR模型实现。

## 功能特点

- **各向异性核函数**: 支持方向性距离计算和各向异性带宽参数
- **CA算法**: 使用条件数算法选择代表性位置点
- **模型拟合**: 使用最大似然估计和L-BFGS-B优化算法
- **空间变系数**: 支持部分变量具有空间变化的系数
- **模型诊断**: 提供AIC、R²、残差分析等诊断工具
- **易于使用**: 简洁的API设计，类似scikit-learn的使用方式

## 安装

### 从PyPI安装（推荐）

```bash
pip install agwr
```

### 从源码安装

```bash
git clone https://github.com/agwr-team/agwr.git
cd agwr
pip install -e .
```

## 依赖要求

- Python >= 3.8
- numpy >= 1.20.0
- pandas >= 1.3.0
- scipy >= 1.7.0

## 快速开始

### 基本用法

```python
import numpy as np
from agwr import VGWR

# 准备数据
n = 100
u = np.random.rand(n) * 10  # 经度坐标
v = np.random.rand(n) * 10   # 纬度坐标

# 生成示例数据
z1 = np.random.randn(n)
z2 = np.random.randn(n)
z3 = np.random.randn(n)
z4 = np.random.randn(n)
z5 = np.random.randn(n)
z6 = np.random.randn(n)

# 生成因变量（示例）
y = (1.0 + 0.5*z1 + 0.3*z2 + 0.2*z3 + 
     0.1*z4 + 0.15*z5 + 0.25*z6 + 
     np.random.randn(n) * 0.1)

# 创建并拟合模型
model = VGWR(m=20, max_iter=100)
model.fit(y, z1, z2, z3, z4, z5, z6, u, v)

# 查看结果
model.summary()

# 获取局部系数
coefficients = model.get_local_coefficients()
print(f"beta2 平均值: {np.mean(coefficients['beta2']):.4f}")
print(f"beta4 平均值: {np.mean(coefficients['beta4']):.4f}")
print(f"beta6 平均值: {np.mean(coefficients['beta6']):.4f}")
```

### 预测新数据

```python
# 准备新数据
n_new = 50
u_new = np.random.rand(n_new) * 10
v_new = np.random.rand(n_new) * 10
z1_new = np.random.randn(n_new)
z2_new = np.random.randn(n_new)
z3_new = np.random.randn(n_new)
z4_new = np.random.randn(n_new)
z5_new = np.random.randn(n_new)
z6_new = np.random.randn(n_new)

# 进行预测
y_pred = model.predict(z1_new, z2_new, z3_new, z4_new, 
                       z5_new, z6_new, u_new, v_new)
print(f"预测值范围: [{y_pred.min():.4f}, {y_pred.max():.4f}]")
```

### 可视化空间变系数

```python
from agwr import plot_spatial_coefficients

# 绘制 beta2 的空间分布
plot_spatial_coefficients(model, u, v, variable_name='beta2')

# 绘制 beta4 的空间分布
plot_spatial_coefficients(model, u, v, variable_name='beta4')

# 绘制 beta6 的空间分布
plot_spatial_coefficients(model, u, v, variable_name='beta6')
```

## 模型理论

VGWR模型基于以下数学公式：

### 各向异性核函数

```
R(h, θ) = exp(-Σ(h²/θ))
```

其中：
- `h` 是方向性距离向量 `[h_u, h_v]`
- `θ` 是各向异性带宽向量 `[θ_u, θ_v]`

### 空间变系数表示

模型使用重构参数化方法来表示空间变化的系数：

```
β(x) = ∑ᵢ γᵢ bᵢ(x)
```

其中 `bᵢ(x)` 是基函数，`γᵢ` 是节点系数。

### 模型形式

VGWR模型的形式为：

```
y = β₀ + β₁z₁ + β₂(u,v)z₂ + β₃z₃ + β₄(u,v)z₄ + β₅z₅ + β₆(u,v)z₆ + ε
```

其中：
- `β₀`, `β₁`, `β₃`, `β₅` 是全局常数系数
- `β₂(u,v)`, `β₄(u,v)`, `β₆(u,v)` 是空间变化的系数

### 负对数似然函数

```
L = (n/2) log(2πσ²) + RSS/(2σ²)
```

其中 `RSS` 是残差平方和。

## API参考

### VGWR类

#### 初始化参数

- `m` (int): 代表点数量，默认为20
- `max_iter` (int): 优化最大迭代次数，默认为100
- `random_state` (int, optional): 随机种子

#### 主要方法

- `fit(y, z1, z2, z3, z4, z5, z6, u, v, initial_theta=None, verbose=True)`: 拟合模型
- `predict(z1_new, z2_new, z3_new, z4_new, z5_new, z6_new, u_new, v_new)`: 进行预测
- `summary()`: 打印模型摘要
- `get_local_coefficients()`: 获取所有位置的局部系数

#### 属性

- `sig`: 误差标准差
- `theta2`, `theta4`, `theta6`: 各向异性带宽参数
- `beta0`, `beta1`, `beta3`, `beta5`: 全局系数
- `betv2`, `betv4`, `betv6`: 空间变系数
- `AIC`: Akaike信息准则
- `R_squared`: 决定系数
- `fitted_values`: 拟合值
- `residuals`: 残差

### 工具函数

- `RV(theta, h)`: 计算各向异性核函数值
- `CA_algorithm(x, m, max_iter)`: 使用条件数算法选择代表点
- `plot_spatial_coefficients(model, u, v, variable_name)`: 绘制空间变系数的分布图

## 测试

运行测试套件：

```bash
cd agwr_package
python -m pytest tests/
```

或者运行单个测试：

```bash
python tests/test_model.py
```

## 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 引用

如果您在研究中使用了AGWR包，请引用相关论文：

```bibtex
@article{agwr2024,
  title={各向异性地理加权回归模型研究},
  author={AGWR开发团队},
  journal={空间统计学报},
  year={2024}
}
```

## 联系方式

- 项目主页: https://github.com/agwr-team/agwr
- 问题反馈: https://github.com/agwr-team/agwr/issues
- 邮箱: agwr@example.com

## 更新日志

### v2.0.0 (2024-01-01)
- 重构为VGWR模型实现
- 实现各向异性核函数
- 支持空间变系数估计
- 提供CA算法选择代表点
- 包含完整的测试套件

### v1.0.0 (2024-01-01)
- 初始版本发布
- 实现基本的AGWR模型
- 支持各向异性核函数
- 提供坐标投影功能
- 包含完整的测试套件
