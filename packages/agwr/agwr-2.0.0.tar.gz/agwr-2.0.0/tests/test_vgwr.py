"""
VGWR模型测试
"""
import numpy as np
import sys
import os

# 添加包路径到sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agwr import VGWR


def test_vgwr_basic():
    """
    测试VGWR模型的基本功能
    """
    print("=" * 80)
    print("测试VGWR模型基本功能")
    print("=" * 80)
    
    # 1. 创建模拟数据
    print("\n1. 创建模拟数据...")
    np.random.seed(42)
    n = 50  # 观测数量
    
    # 创建模拟坐标
    u = np.random.rand(n) * 10  # 经度坐标
    v = np.random.rand(n) * 10   # 纬度坐标
    
    # 创建模拟变量
    z1 = np.random.randn(n)
    z2 = np.random.randn(n)
    z3 = np.random.randn(n)
    z4 = np.random.randn(n)
    z5 = np.random.randn(n)
    z6 = np.random.randn(n)
    
    # 创建因变量
    y = (1.0 + 0.5*z1 + 0.3*z2 + 0.2*z3 + 
         0.1*z4 + 0.15*z5 + 0.25*z6 + 
         np.random.randn(n) * 0.1)
    
    print(f"  观测数量: {n}")
    print(f"  坐标范围: u({u.min():.2f}, {u.max():.2f})")
    print(f"  坐标范围: v({v.min():.2f}, {v.max():.2f})")
    
    # 2. 创建并拟合模型
    print("\n2. 拟合VGWR模型...")
    model = VGWR(m=10, max_iter=50, random_state=42)
    
    try:
        model.fit(y, z1, z2, z3, z4, z5, z6, u, v, verbose=False)
        
        # 3. 验证结果
        print("\n3. 验证模型结果...")
        
        # 检查模型参数
        assert model.beta0 is not None, "beta0未计算"
        assert model.beta1 is not None, "beta1未计算"
        assert model.beta3 is not None, "beta3未计算"
        assert model.beta5 is not None, "beta5未计算"
        assert model.sig is not None, "sig未计算"
        print("  ✓ 全局参数已计算")
        
        # 检查空间变系数
        assert model.betv2 is not None, "betv2未计算"
        assert model.betv4 is not None, "betv4未计算"
        assert model.betv6 is not None, "betv6未计算"
        print("  ✓ 空间变系数已计算")
        
        # 检查模型评估指标
        assert model.AIC is not None, "AIC未计算"
        assert model.R_squared is not None, "R²未计算"
        assert model.fitted_values is not None, "拟合值未计算"
        assert model.residuals is not None, "残差未计算"
        print(f"  ✓ AIC: {model.AIC:.4f}")
        print(f"  ✓ R²: {model.R_squared:.6f}")
        
        # 4. 测试预测功能
        print("\n4. 测试预测功能...")
        n_new = 10
        u_new = np.random.rand(n_new) * 10
        v_new = np.random.rand(n_new) * 10
        z1_new = np.random.randn(n_new)
        z2_new = np.random.randn(n_new)
        z3_new = np.random.randn(n_new)
        z4_new = np.random.randn(n_new)
        z5_new = np.random.randn(n_new)
        z6_new = np.random.randn(n_new)
        
        y_pred = model.predict(z1_new, z2_new, z3_new, z4_new, 
                              z5_new, z6_new, u_new, v_new)
        assert len(y_pred) == n_new, "预测值数量不正确"
        print(f"  ✓ 预测完成，预测值范围: [{y_pred.min():.4f}, {y_pred.max():.4f}]")
        
        # 5. 测试获取局部系数
        print("\n5. 测试获取局部系数...")
        coeffs = model.get_local_coefficients()
        assert 'beta0' in coeffs, "缺少beta0"
        assert 'beta2' in coeffs, "缺少beta2"
        assert 'beta4' in coeffs, "缺少beta4"
        assert 'beta6' in coeffs, "缺少beta6"
        print(f"  ✓ 局部系数已获取")
        print(f"    beta2 平均值: {np.mean(coeffs['beta2']):.4f}")
        print(f"    beta4 平均值: {np.mean(coeffs['beta4']):.4f}")
        print(f"    beta6 平均值: {np.mean(coeffs['beta6']):.4f}")
        
        print("\n" + "=" * 80)
        print("✓ 所有测试通过！VGWR模型运行成功")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n✗ 模型测试失败: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "=" * 80)
        print("✗ 测试失败")
        print("=" * 80)
        return False


if __name__ == "__main__":
    test_vgwr_basic()

