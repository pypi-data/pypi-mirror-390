"""
各向异性地理加权回归 (VGWR) - Python实现
Variably Geographically Weighted Regression

这是从R代码(xtgccode.R 第356-477行)转换而来的完整实现
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.spatial.distance import pdist, squareform
import warnings
warnings.filterwarnings('ignore')


# ==============================================================================
# 核心函数：各向异性相关函数
# ==============================================================================

def RV(theta, h):
    """各向异性核函数 R(x) = exp(-Σ (h_j^2 / theta_j))"""
    RH = -np.sum((h**2) / theta)
    return np.exp(RH)

def CA_algorithm(x, m=20, max_iter=100):
    n = x.shape[0]
    C0 = n  # 初始值设为n
    t0 = None
    
    for k in range(max_iter):
        # 随机采样m个点
        t = np.random.choice(n, m, replace=False)
        U = x[t]
        
        # 计算所有点对之间的欧氏距离的倒数
        c_values = []
        for i in range(m-1):
            for j in range(i+1, m):
                # 计算欧氏距离
                dist = np.linalg.norm(U[i] - U[j])
                if dist > 0:
                    c_values.append(1.0 / dist)
        
        if len(c_values) > 0:
            CA = max(c_values)
            
            # 如果当前配置更好，则保存
            if CA <= C0:
                t0 = t.copy()
                C0 = CA
    
    # 如果没有找到合适的点，返回随机选择
    if t0 is None:
        t0 = np.random.choice(n, m, replace=False)
    
    return t0

def RAV_function(theta, ua, va, m):
    RAV = np.zeros((m, m))
    for i in range(m):
        for j in range(m):
            h = np.array([ua[i] - ua[j], va[i] - va[j]])
            RAV[i, j] = RV(theta, h)
    return RAV

def rav_function(theta, u, v, ua, va, m, n):
    rav = np.zeros((m, n))
    for i in range(m):
        for j in range(n):
            h = np.array([u[j] - ua[i], v[j] - va[i]])
            rav[i, j] = RV(theta, h)
    return rav

def bv_function(x, theta, ua, va, u, v, m0):
    m, n = len(m0), len(u)
    RAAV = RAV_function(theta, ua, va, m)
    rAV = rav_function(theta, u, v, ua, va, m, n)

    # 正确的 GAV 定义
    GAV = np.column_stack([np.ones(m), ua, va])
    RATV = np.linalg.inv(RAAV + 1e-6 * np.eye(m))
    GRAV = np.linalg.inv(GAV.T @ RATV @ GAV)
    PV = RATV @ GAV @ GRAV
    QV = (np.eye(m) - RATV @ GAV @ GRAV @ GAV.T) @ RATV

    bv = np.zeros((m, n))
    for i in range(n):
        g_i = np.array([1, u[i], v[i]])
        bv[:, i] = PV @ g_i + QV @ rAV[:, i]
    return bv

def vgwr_objective(par, y, z1, z2, z3, z4, z5, z6, x, m0, u, v, ua, va):
    sig = par[0]
    theta2 = par[1:3]
    theta4 = par[3:5]
    theta6 = par[5:7]
    beta0 = par[7]
    beta1 = par[8]
    beta3 = par[9]
    beta5 = par[10]
    
    m = len(m0)
    gama1 = par[11:11+m]
    gama2 = par[11+m:11+2*m]
    gama3 = par[11+2*m:11+3*m]
    
    # 使用各向异性函数计算b矩阵
    b2 = bv_function(x, theta2, ua, va, u, v, m0)
    b4 = bv_function(x, theta4, ua, va, u, v, m0)
    b6 = bv_function(x, theta6, ua, va, u, v, m0)
    
    n = len(y)
    
    # 计算空间变系数
    IGP2 = gama1 @ b2  # 结果是 (n,) 向量
    IGP4 = gama2 @ b4
    IGP6 = gama3 @ b6
    
    # 计算残差
    e = y - beta0 - beta1*z1 - IGP2*z2 - beta3*z3 - IGP4*z4 - beta5*z5 - IGP6*z6
    
    # 计算负对数似然
    ll = n/2 * np.log(2*np.pi*sig**2) + (0.5 * np.dot(e, e)) / (sig**2)
    
    return ll


# ==============================================================================
# VGWR模型类
# ==============================================================================

class VGWR:
    """
    各向异性地理加权回归模型类
    
    使用示例:
    >>> model = VGWR(m=20)
    >>> model.fit(y, z1, z2, z3, z4, z5, z6, u, v)
    >>> print(model.summary())
    """
    
    def __init__(self, m=20, max_iter=100, random_state=None):
        """
        初始化VGWR模型
        
        参数:
        m: 代表点数量
        max_iter: 优化最大迭代次数
        random_state: 随机种子
        """
        self.m = m
        self.max_iter = max_iter
        self.random_state = random_state
        
        # 模型参数（拟合后填充）
        self.sig = None
        self.theta2 = None
        self.theta4 = None
        self.theta6 = None
        self.beta0 = None
        self.beta1 = None
        self.beta3 = None
        self.beta5 = None
        self.gama_vgwr = None
        
        # 空间变系数
        self.betv2 = None
        self.betv4 = None
        self.betv6 = None
        
        # 模型评估指标
        self.residuals = None
        self.AIC = None
        self.R_squared = None
        self.fitted_values = None
        
        # 代表点
        self.m0 = None
        self.ua = None
        self.va = None
    
    def fit(self, y, z1, z2, z3, z4, z5, z6, u, v, 
            initial_theta=None, verbose=True):
        """
        拟合VGWR模型
        
        R代码对应:
        opt_vgwr<-optim(c(rep(1,11),t2,t4,t6),fnv,method ="L-BFGS-B" ,
                   control = list(maxit=100))
        
        参数:
        y: 因变量
        z1-z6: 自变量
        u, v: 空间坐标
        initial_theta: 初始参数（如果为None则使用默认值）
        verbose: 是否打印优化过程
        """
        if self.random_state is not None:
            np.random.seed(self.random_state)
        
        # 转换为numpy数组
        y = np.asarray(y)
        z1 = np.asarray(z1)
        z2 = np.asarray(z2)
        z3 = np.asarray(z3)
        z4 = np.asarray(z4)
        z5 = np.asarray(z5)
        z6 = np.asarray(z6)
        u = np.asarray(u)
        v = np.asarray(v)
        
        n = len(y)
        x = np.column_stack([u, v])
        
        # 使用CA算法选择代表点
        if verbose:
            print("正在选择代表性位置点...")
        self.m0 = CA_algorithm(x, m=self.m, max_iter=100)
        self.ua = u[self.m0]
        self.va = v[self.m0]
        
        if verbose:
            print(f"选择了 {len(self.m0)} 个代表点")
        
        # 设置初始参数
        if initial_theta is None:
            # 根据经纬度尺度估计合理带宽初值
            theta_init = np.array([np.var(u) ** 0.5, np.var(v) ** 0.5])
            initial_params = np.concatenate([
                [1.0],  # sig
                theta_init,  # theta2
                theta_init,  # theta4
                theta_init,  # theta6
                [1, 1, 1, 1],  # beta0, beta1, beta3, beta5
                np.ones(self.m), np.ones(self.m), np.ones(self.m)
            ])

        else:
            initial_params = initial_theta
        
        if verbose:
            print(f"参数总数: {len(initial_params)}")
            print("开始优化...")

        # 设置约束：所有参数必须为正（避免 theta 出现负值）
        bounds = [(1e-6, None)] * len(initial_params)

        # 执行优化（带约束）
        result = minimize(
            vgwr_objective,
            initial_params,
            args=(y, z1, z2, z3, z4, z5, z6, x, self.m0, u, v, self.ua, self.va),
            method='L-BFGS-B',
            bounds=bounds,
            options={'maxiter': self.max_iter, 'disp': verbose}
        )

        if verbose:
            print(f"优化完成。成功: {result.success}")
            print(f"迭代次数: {result.nit}")
            print(f"最终似然值: {result.fun:.4f}")
        
        # 提取参数
        self.sig = result.x[0]
        self.theta2 = result.x[1:3]
        self.theta4 = result.x[3:5]
        self.theta6 = result.x[5:7]
        self.beta0 = result.x[7]
        self.beta1 = result.x[8]
        self.beta3 = result.x[9]
        self.beta5 = result.x[10]
        self.gama_vgwr = result.x[11:]
        
        # 计算空间变系数
        B2 = bv_function(x, self.theta2, self.ua, self.va, u, v, self.m0)
        B4 = bv_function(x, self.theta4, self.ua, self.va, u, v, self.m0)
        B6 = bv_function(x, self.theta6, self.ua, self.va, u, v, self.m0)
        
        gama1 = self.gama_vgwr[0:self.m]
        gama2 = self.gama_vgwr[self.m:2*self.m]
        gama3 = self.gama_vgwr[2*self.m:3*self.m]
        
        self.betv2 = gama1 @ B2  # (n,) 向量
        self.betv4 = gama2 @ B4
        self.betv6 = gama3 @ B6
        
        # 计算拟合值和残差
        self.fitted_values = (self.beta0 + self.beta1*z1 + self.betv2*z2 + 
                             self.beta3*z3 + self.betv4*z4 + self.beta5*z5 + 
                             self.betv6*z6)
        self.residuals = y - self.fitted_values
        
        # 计算模型评估指标
        l_vgwr = n/2 * np.log(2*np.pi*self.sig**2) + \
                 (0.5 * np.dot(self.residuals, self.residuals)) / (self.sig**2)
        
        self.AIC = 2 * 71 - 2 * l_vgwr  # 71是参数个数
        
        # 计算R²
        rs = y - np.mean(y)
        rss = np.dot(rs, rs)
        self.R_squared = 1 - np.sum(self.residuals**2) / rss
        
        if verbose:
            print("\n模型拟合完成！")
        
        return self
    
    def predict(self, z1_new, z2_new, z3_new, z4_new, z5_new, z6_new, 
                u_new, v_new):
        """
        使用拟合的模型进行预测
        
        参数:
        z1_new - z6_new: 新数据的自变量
        u_new, v_new: 新数据的空间坐标
        
        返回:
        预测值
        """
        z1_new = np.asarray(z1_new)
        z2_new = np.asarray(z2_new)
        z3_new = np.asarray(z3_new)
        z4_new = np.asarray(z4_new)
        z5_new = np.asarray(z5_new)
        z6_new = np.asarray(z6_new)
        u_new = np.asarray(u_new)
        v_new = np.asarray(v_new)
        
        n_new = len(z1_new)
        x_new = np.column_stack([u_new, v_new])
        
        # 为新位置计算空间变系数
        B2_new = bv_function(x_new, self.theta2, self.ua, self.va, 
                            u_new, v_new, self.m0)
        B4_new = bv_function(x_new, self.theta4, self.ua, self.va, 
                            u_new, v_new, self.m0)
        B6_new = bv_function(x_new, self.theta6, self.ua, self.va, 
                            u_new, v_new, self.m0)
        
        gama1 = self.gama_vgwr[0:self.m]
        gama2 = self.gama_vgwr[self.m:2*self.m]
        gama3 = self.gama_vgwr[2*self.m:3*self.m]
        
        betv2_new = gama1 @ B2_new
        betv4_new = gama2 @ B4_new
        betv6_new = gama3 @ B6_new
        
        # 计算预测值
        y_pred = (self.beta0 + self.beta1*z1_new + betv2_new*z2_new + 
                 self.beta3*z3_new + betv4_new*z4_new + self.beta5*z5_new + 
                 betv6_new*z6_new)
        
        return y_pred
    
    def summary(self):
        """
        打印模型摘要
        
        R代码对应:
        print(opt_vgwr$par)
        mean(as.numeric(t(gama_vgwr[c(1:20)])%*%B2))
        ...
        """
        print("="*70)
        print("各向异性地理加权回归 (VGWR) 模型摘要")
        print("="*70)
        print()
        
        print("全局参数:")
        print(f"  截距 (beta0):           {self.beta0:10.6f}")
        print(f"  z1系数 (beta1):         {self.beta1:10.6f}")
        print(f"  z3系数 (beta3):         {self.beta3:10.6f}")
        print(f"  z5系数 (beta5):         {self.beta5:10.6f}")
        print(f"  标准差 (sigma):         {self.sig:10.6f}")
        print()
        
        print("各向异性带宽参数:")
        print(f"  theta2 (z2):            [{self.theta2[0]:8.6f}, {self.theta2[1]:8.6f}]")
        print(f"  theta4 (z4):            [{self.theta4[0]:8.6f}, {self.theta4[1]:8.6f}]")
        print(f"  theta6 (z6):            [{self.theta6[0]:8.6f}, {self.theta6[1]:8.6f}]")
        print()
        
        print("空间变系数统计 (z2, z4, z6):")
        print(f"  betv2 平均值:           {np.mean(self.betv2):10.6f}")
        print(f"  betv2 标准差:           {np.std(self.betv2):10.6f}")
        print(f"  betv2 范围:             [{np.min(self.betv2):8.4f}, {np.max(self.betv2):8.4f}]")
        print()
        print(f"  betv4 平均值:           {np.mean(self.betv4):10.6f}")
        print(f"  betv4 标准差:           {np.std(self.betv4):10.6f}")
        print(f"  betv4 范围:             [{np.min(self.betv4):8.4f}, {np.max(self.betv4):8.4f}]")
        print()
        print(f"  betv6 平均值:           {np.mean(self.betv6):10.6f}")
        print(f"  betv6 标准差:           {np.std(self.betv6):10.6f}")
        print(f"  betv6 范围:             [{np.min(self.betv6):8.4f}, {np.max(self.betv6):8.4f}]")
        print()
        
        print("模型评估:")
        print(f"  AIC:                    {self.AIC:10.4f}")
        print(f"  R²:                     {self.R_squared:10.6f}")
        print(f"  残差平方和:             {np.sum(self.residuals**2):10.4f}")
        print(f"  RMSE:                   {np.sqrt(np.mean(self.residuals**2)):10.6f}")
        print()
        
        print(f"代表点数量: {self.m}")
        print(f"参数总数: {11 + 3*self.m}")
        print("="*70)
    
    def get_local_coefficients(self):
        """
        获取所有位置的局部系数
        
        返回:
        包含所有局部系数的字典
        """
        return {
            'beta0': self.beta0,  # 全局常数
            'beta1': self.beta1,  # 全局常数
            'beta2': self.betv2,  # 空间变化
            'beta3': self.beta3,  # 全局常数
            'beta4': self.betv4,  # 空间变化
            'beta5': self.beta5,  # 全局常数
            'beta6': self.betv6   # 空间变化
        }


# ==============================================================================
# 辅助函数
# ==============================================================================

def plot_spatial_coefficients(model, u, v, variable_name='beta2', 
                              figsize=(10, 8)):
    """
    绘制空间变系数的分布图
    
    参数:
    model: 拟合好的VGWR模型
    u, v: 坐标
    variable_name: 要绘制的变量名 ('beta2', 'beta4', 或 'beta6')
    figsize: 图形大小
    """
    import matplotlib.pyplot as plt
    from matplotlib import cm
    
    coeffs = model.get_local_coefficients()
    
    if variable_name not in coeffs:
        raise ValueError(f"变量名必须是: {list(coeffs.keys())}")
    
    coef_values = coeffs[variable_name]
    
    # 如果是标量，则无法绘制空间分布
    if not hasattr(coef_values, '__len__'):
        print(f"{variable_name} 是全局常数，无空间变化")
        return
    
    plt.figure(figsize=figsize)
    scatter = plt.scatter(u, v, c=coef_values, cmap=cm.RdYlBu_r, 
                         s=100, edgecolors='black', linewidth=0.5)
    plt.colorbar(scatter, label=f'{variable_name}系数值')
    plt.xlabel('经度 (u)')
    plt.ylabel('纬度 (v)')
    plt.title(f'{variable_name} 的空间分布')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

