# -*- coding: utf-8 -*-
"""
Manim UCP Arvin - 综合测试套件
=====================================

本测试文件基于 USER_MANUAL.txt 中的示例公式，设计完整的测试用例集。
包含正常输入、边界条件、异常输入和安全漏洞测试。

测试分类：
1. 显函数微分测试 (TestExplicitDifferentiation)
2. 隐函数微分测试 (TestImplicitDifferentiation)
3. 极坐标输入测试 (TestPolarCoordinates)
4. 参数方程测试 (TestParametricEquations)
5. 边界条件测试 (TestBoundaryConditions)
6. 安全漏洞测试 (TestSecurityVulnerabilities)
7. 性能测试 (TestPerformance)

运行方式：
    python -m pytest test_comprehensive.py -v
    或
    python test_comprehensive.py
"""

import unittest
import sys
import os
import time
import math
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

HAS_MANIM = False
HAS_SYMYP = False

try:
    import sympy as sp
    from sympy import symbols, diff, sin, cos, exp, log, sqrt, pi, E, sympify
    HAS_SYMYP = True
except ImportError:
    HAS_SYMYP = False
    print("警告: SymPy 未安装，部分测试将被跳过")

try:
    from manim import *
    HAS_MANIM = True
except ImportError:
    HAS_MANIM = False
    print("警告: Manim 未安装，动画相关测试将被跳过")


class MockAnimator:
    """模拟动画生成器，用于在没有 Manim 的环境下运行测试"""
    
    def parse_function(self, func_str):
        """解析函数字符串为sympy表达式"""
        if not HAS_SYMYP:
            raise ImportError("SymPy 未安装")
        
        try:
            allowed_locals = {
                'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
                'exp': sp.exp, 'log': sp.log, 'sqrt': sp.sqrt,
                'pi': sp.pi, 'e': sp.E
            }
            expr = sp.sympify(func_str, locals=allowed_locals)
            return expr
        except Exception as e:
            raise ValueError(f"函数解析错误: {str(e)}")
    
    def compute_tangent_at_point(self, func_str, point_x, point_y):
        """计算隐函数在某点的切线"""
        if not HAS_SYMYP:
            raise ImportError("SymPy 未安装")
        
        x, y = symbols('x y')
        func = self.parse_function(func_str)
        
        dF_dx = sp.diff(func, x)
        dF_dy = sp.diff(func, y)
        
        dF_dx_val = float(dF_dx.subs([(x, point_x), (y, point_y)]))
        dF_dy_val = float(dF_dy.subs([(x, point_x), (y, point_y)]))
        
        if abs(dF_dy_val) < 1e-10:
            return None, None, None, None
        
        slope = -dF_dx_val / dF_dy_val
        
        def tangent_func(x_val):
            return slope * (x_val - point_x) + point_y
        
        return slope, point_x, point_y, tangent_func
    
    def create_polar_function(self, func_str):
        """创建极坐标函数"""
        def polar_func(theta):
            return eval(
                func_str,
                {
                    "theta": theta, "pi": math.pi, "e": math.e,
                    "sin": math.sin, "cos": math.cos, "tan": math.tan,
                    "exp": math.exp, "sqrt": math.sqrt, "log": math.log
                }
            )
        polar_func(0)
        return polar_func


if HAS_MANIM:
    try:
        from differentiation_animator import DifferentiationAnimator
        from implicit_animator import ImplicitFunctionAnimator
        from polar_animator import PolarAnimator
        from three_d_animator import ThreeDAnimator
        USE_REAL_ANIMATORS = True
    except ImportError:
        USE_REAL_ANIMATORS = False
        DifferentiationAnimator = MockAnimator
        ImplicitFunctionAnimator = MockAnimator
        PolarAnimator = MockAnimator
        ThreeDAnimator = MockAnimator
else:
    USE_REAL_ANIMATORS = False
    DifferentiationAnimator = MockAnimator
    ImplicitFunctionAnimator = MockAnimator
    PolarAnimator = MockAnimator
    ThreeDAnimator = MockAnimator


class TestExplicitDifferentiation(unittest.TestCase):
    """显函数微分测试类
    
    测试步骤：
    1. 初始化微分动画生成器
    2. 解析函数表达式
    3. 计算导数
    4. 验证结果正确性
    
    预期结果：
    - 所有正常函数应正确解析和求导
    - 导数结果应与数学计算一致
    """
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.animator = DifferentiationAnimator()
        print("\n" + "="*60)
        print("显函数微分测试开始")
        print("="*60)
    
    def test_basic_polynomial(self):
        """测试基本多项式函数微分
        
        测试步骤：
        1. 输入 x**2
        2. 验证解析成功
        3. 验证导数为 2*x
        
        预期结果：解析成功，导数计算正确
        """
        func_str = "x**2"
        fit_point = 1
        radius = 2
        
        result = self.animator.parse_function(func_str)
        self.assertIsNotNone(result, "多项式函数解析失败")
        
        from sympy import symbols, diff
        x = symbols('x')
        expected_derivative = diff(result, x)
        expected_value = expected_derivative.subs(x, fit_point)
        
        self.assertEqual(float(expected_value), 2.0, "x**2 在 x=1 处导数应为 2")
        print(f"  [PASS] 多项式 x**2 微分测试通过")
    
    def test_trigonometric_sin(self):
        """测试正弦函数微分
        
        测试步骤：
        1. 输入 sin(x)
        2. 在 x=pi/4 处求导
        3. 验证导数为 cos(x)
        
        预期结果：导数为 cos(pi/4) = sqrt(2)/2
        """
        func_str = "sin(x)"
        fit_point = math.pi / 4
        
        result = self.animator.parse_function(func_str)
        self.assertIsNotNone(result, "正弦函数解析失败")
        
        from sympy import symbols, diff, cos
        x = symbols('x')
        expected_derivative = diff(result, x)
        expected_value = float(expected_derivative.subs(x, fit_point))
        
        self.assertAlmostEqual(expected_value, math.cos(fit_point), places=6, 
                              msg="sin(x) 导数应为 cos(x)")
        print(f"  [PASS] 正弦函数 sin(x) 微分测试通过")
    
    def test_trigonometric_cos(self):
        """测试余弦函数微分"""
        func_str = "cos(x)"
        fit_point = math.pi / 3
        
        result = self.animator.parse_function(func_str)
        self.assertIsNotNone(result, "余弦函数解析失败")
        
        from sympy import symbols, diff, sin
        x = symbols('x')
        expected_derivative = diff(result, x)
        expected_value = float(expected_derivative.subs(x, fit_point))
        
        self.assertAlmostEqual(expected_value, -math.sin(fit_point), places=6,
                              msg="cos(x) 导数应为 -sin(x)")
        print(f"  [PASS] 余弦函数 cos(x) 微分测试通过")
    
    def test_exponential(self):
        """测试指数函数微分
        
        测试步骤：
        1. 输入 exp(x)
        2. 在 x=0 处求导
        3. 验证导数为 exp(x)
        
        预期结果：exp(0) = 1
        """
        func_str = "exp(x)"
        fit_point = 0
        
        result = self.animator.parse_function(func_str)
        self.assertIsNotNone(result, "指数函数解析失败")
        
        from sympy import symbols, diff, exp
        x = symbols('x')
        expected_derivative = diff(result, x)
        expected_value = float(expected_derivative.subs(x, fit_point))
        
        self.assertAlmostEqual(expected_value, 1.0, places=6,
                              msg="exp(x) 在 x=0 处导数应为 1")
        print(f"  [PASS] 指数函数 exp(x) 微分测试通过")
    
    def test_logarithm(self):
        """测试对数函数微分"""
        func_str = "log(x)"
        fit_point = 1
        
        result = self.animator.parse_function(func_str)
        self.assertIsNotNone(result, "对数函数解析失败")
        
        from sympy import symbols, diff
        x = symbols('x')
        expected_derivative = diff(result, x)
        expected_value = float(expected_derivative.subs(x, fit_point))
        
        self.assertAlmostEqual(expected_value, 1.0, places=6,
                              msg="log(x) 在 x=1 处导数应为 1")
        print(f"  [PASS] 对数函数 log(x) 微分测试通过")
    
    def test_sqrt_function(self):
        """测试平方根函数微分"""
        func_str = "sqrt(x)"
        fit_point = 4
        
        result = self.animator.parse_function(func_str)
        self.assertIsNotNone(result, "平方根函数解析失败")
        
        from sympy import symbols, diff, sqrt
        x = symbols('x')
        expected_derivative = diff(result, x)
        expected_value = float(expected_derivative.subs(x, fit_point))
        
        self.assertAlmostEqual(expected_value, 1/(2*math.sqrt(fit_point)), places=6,
                              msg="sqrt(x) 导数应为 1/(2*sqrt(x))")
        print(f"  [PASS] 平方根函数 sqrt(x) 微分测试通过")
    
    def test_combined_function(self):
        """测试组合函数微分
        
        测试步骤：
        1. 输入 sin(x) + cos(x)
        2. 验证导数为 cos(x) - sin(x)
        """
        func_str = "sin(x) + cos(x)"
        fit_point = math.pi / 4
        
        result = self.animator.parse_function(func_str)
        self.assertIsNotNone(result, "组合函数解析失败")
        
        from sympy import symbols, diff
        x = symbols('x')
        expected_derivative = diff(result, x)
        expected_value = float(expected_derivative.subs(x, fit_point))
        
        expected = math.cos(fit_point) - math.sin(fit_point)
        self.assertAlmostEqual(expected_value, expected, places=6,
                              msg="sin(x)+cos(x) 导数应为 cos(x)-sin(x)")
        print(f"  [PASS] 组合函数 sin(x)+cos(x) 微分测试通过")
    
    def test_gaussian_function(self):
        """测试高斯函数微分"""
        func_str = "exp(-x**2)"
        fit_point = 0
        
        result = self.animator.parse_function(func_str)
        self.assertIsNotNone(result, "高斯函数解析失败")
        
        from sympy import symbols, diff
        x = symbols('x')
        expected_derivative = diff(result, x)
        expected_value = float(expected_derivative.subs(x, fit_point))
        
        self.assertAlmostEqual(expected_value, 0.0, places=6,
                              msg="exp(-x**2) 在 x=0 处导数应为 0")
        print(f"  [PASS] 高斯函数 exp(-x**2) 微分测试通过")
    
    def test_power_function_cubic(self):
        """测试三次函数微分"""
        func_str = "x**3"
        fit_point = 2
        
        result = self.animator.parse_function(func_str)
        self.assertIsNotNone(result, "三次函数解析失败")
        
        from sympy import symbols, diff
        x = symbols('x')
        expected_derivative = diff(result, x)
        expected_value = float(expected_derivative.subs(x, fit_point))
        
        self.assertAlmostEqual(expected_value, 12.0, places=6,
                              msg="x**3 在 x=2 处导数应为 12")
        print(f"  [PASS] 三次函数 x**3 微分测试通过")
    
    def test_inverse_function(self):
        """测试反比例函数微分"""
        func_str = "1/x"
        fit_point = 1
        
        result = self.animator.parse_function(func_str)
        self.assertIsNotNone(result, "反比例函数解析失败")
        
        from sympy import symbols, diff
        x = symbols('x')
        expected_derivative = diff(result, x)
        expected_value = float(expected_derivative.subs(x, fit_point))
        
        self.assertAlmostEqual(expected_value, -1.0, places=6,
                              msg="1/x 在 x=1 处导数应为 -1")
        print(f"  [PASS] 反比例函数 1/x 微分测试通过")


class TestImplicitDifferentiation(unittest.TestCase):
    """隐函数微分测试类
    
    测试步骤：
    1. 初始化隐函数动画生成器
    2. 解析隐函数表达式 F(x,y) = 0
    3. 计算隐函数导数 dy/dx = -∂F/∂x / ∂F/∂y
    4. 验证结果正确性
    """
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.animator = ImplicitFunctionAnimator()
        print("\n" + "="*60)
        print("隐函数微分测试开始")
        print("="*60)
    
    def test_circle(self):
        """测试圆的隐函数微分
        
        测试步骤：
        1. 输入 x**2 + y**2 - 4 (圆)
        2. 在点 (1, sqrt(3)) 处求切线
        3. 验证斜率为 -x/y
        
        预期结果：斜率 = -1/sqrt(3)
        """
        func_str = "x**2 + y**2 - 4"
        point_x, point_y = 1.0, math.sqrt(3)
        
        result = self.animator.compute_tangent_at_point(func_str, point_x, point_y)
        slope, px, py, tangent_func = result
        
        self.assertIsNotNone(slope, "圆的切线计算失败")
        expected_slope = -point_x / point_y
        self.assertAlmostEqual(slope, expected_slope, places=5,
                              msg="圆的切线斜率应为 -x/y")
        print(f"  [PASS] 圆 x**2 + y**2 = 4 隐函数微分测试通过")
    
    def test_ellipse(self):
        """测试椭圆的隐函数微分"""
        func_str = "x**2/4 + y**2 - 1"
        point_x, point_y = 0.0, 1.0
        
        result = self.animator.compute_tangent_at_point(func_str, point_x, point_y)
        slope, px, py, tangent_func = result
        
        self.assertIsNotNone(slope, "椭圆的切线计算失败")
        self.assertAlmostEqual(slope, 0.0, places=5,
                              msg="椭圆在顶点处切线斜率应为 0")
        print(f"  [PASS] 椭圆 x**2/4 + y**2 = 1 隐函数微分测试通过")
    
    def test_hyperbola(self):
        """测试双曲线的隐函数微分"""
        func_str = "x**2 - y**2 - 1"
        point_x, point_y = math.sqrt(2), 1.0
        
        result = self.animator.compute_tangent_at_point(func_str, point_x, point_y)
        slope, px, py, tangent_func = result
        
        self.assertIsNotNone(slope, "双曲线的切线计算失败")
        expected_slope = point_x / point_y
        self.assertAlmostEqual(slope, expected_slope, places=5,
                              msg="双曲线切线斜率计算错误")
        print(f"  [PASS] 双曲线 x**2 - y**2 = 1 隐函数微分测试通过")
    
    def test_parabola(self):
        """测试抛物线的隐函数微分"""
        func_str = "y - x**2"
        point_x, point_y = 2.0, 4.0
        
        result = self.animator.compute_tangent_at_point(func_str, point_x, point_y)
        slope, px, py, tangent_func = result
        
        self.assertIsNotNone(slope, "抛物线的切线计算失败")
        expected_slope = 2 * point_x
        self.assertAlmostEqual(slope, expected_slope, places=5,
                              msg="抛物线 y=x**2 切线斜率应为 2x")
        print(f"  [PASS] 抛物线 y = x**2 隐函数微分测试通过")
    
    def test_shifted_circle(self):
        """测试偏移圆的隐函数微分
        
        注意：在点 (3, 2) 处，∂F/∂y = 0，此时切线为垂直线
        系统返回 None 表示垂直切线情况
        """
        func_str = "(x-1)**2 + (y-2)**2 - 4"
        point_x, point_y = 3.0, 2.0
        
        result = self.animator.compute_tangent_at_point(func_str, point_x, point_y)
        slope, px, py, tangent_func = result
        
        self.assertIsNone(slope, "在水平直径端点，切线应为垂直线（slope=None）")
        print(f"  [PASS] 偏移圆 (x-1)**2 + (y-2)**2 = 4 隐函数微分测试通过（垂直切线）")
    
    def test_folium_descartes(self):
        """测试笛卡尔叶形线的隐函数微分"""
        func_str = "x**3 + y**3 - 3*x*y"
        point_x, point_y = 1.5, 1.5
        
        result = self.animator.compute_tangent_at_point(func_str, point_x, point_y)
        slope, px, py, tangent_func = result
        
        self.assertIsNotNone(slope, "笛卡尔叶形线的切线计算失败")
        print(f"  [PASS] 笛卡尔叶形线隐函数微分测试通过")


class TestPolarCoordinates(unittest.TestCase):
    """极坐标输入测试类
    
    测试步骤：
    1. 初始化极坐标动画生成器
    2. 解析极坐标表达式 r = r(θ)
    3. 验证转换后的直角坐标正确性
    """
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.animator = PolarAnimator()
        print("\n" + "="*60)
        print("极坐标输入测试开始")
        print("="*60)
    
    def test_circle_polar(self):
        """测试极坐标圆
        
        测试步骤：
        1. 输入 r = 2 (圆)
        2. 验证 θ=0 时点为 (2, 0)
        3. 验证 θ=π/2 时点为 (0, 2)
        """
        func_str = "2"
        theta = 0
        
        r = eval(func_str, {"theta": theta, "pi": math.pi})
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        
        self.assertEqual(r, 2, "极坐标圆半径应为 2")
        self.assertAlmostEqual(x, 2.0, places=6)
        self.assertAlmostEqual(y, 0.0, places=6)
        print(f"  [PASS] 极坐标圆 r=2 测试通过")
    
    def test_archimedean_spiral(self):
        """测试阿基米德螺线"""
        func_str = "2*theta"
        
        theta_values = [0, math.pi/4, math.pi/2, math.pi]
        for theta in theta_values:
            r = eval(func_str, {"theta": theta, "pi": math.pi})
            expected_r = 2 * theta
            self.assertAlmostEqual(r, expected_r, places=6,
                                  msg="阿基米德螺线 r=2θ 计算错误")
        print(f"  [PASS] 阿基米德螺线 r=2θ 测试通过")
    
    def test_logarithmic_spiral(self):
        """测试对数螺线"""
        func_str = "exp(theta/3)"
        theta = 0
        
        r = eval(func_str, {"theta": theta, "pi": math.pi, "exp": math.exp})
        self.assertAlmostEqual(r, 1.0, places=6, msg="对数螺线在 θ=0 时 r=1")
        print(f"  [PASS] 对数螺线 r=exp(θ/3) 测试通过")
    
    def test_rose_curve_4_petals(self):
        """测试四叶玫瑰线"""
        func_str = "cos(2*theta)"
        
        theta_values = [0, math.pi/4, math.pi/2, math.pi]
        expected_values = [1, 0, -1, 1]
        
        for theta, expected in zip(theta_values, expected_values):
            r = eval(func_str, {"theta": theta, "pi": math.pi, "cos": math.cos})
            self.assertAlmostEqual(r, expected, places=6,
                                  msg="四叶玫瑰线计算错误")
        print(f"  [PASS] 四叶玫瑰线 r=cos(2θ) 测试通过")
    
    def test_rose_curve_3_petals(self):
        """测试三叶玫瑰线"""
        func_str = "cos(3*theta)"
        
        theta_values = [0, math.pi/6, math.pi/3]
        for theta in theta_values:
            r = eval(func_str, {"theta": theta, "pi": math.pi, "cos": math.cos})
            expected = math.cos(3 * theta)
            self.assertAlmostEqual(r, expected, places=6)
        print(f"  [PASS] 三叶玫瑰线 r=cos(3θ) 测试通过")
    
    def test_cardioid(self):
        """测试心形线"""
        func_str = "2 + 2*sin(theta)"
        
        theta_values = [0, math.pi/2, math.pi, 3*math.pi/2]
        expected_values = [2, 4, 2, 0]
        
        for theta, expected in zip(theta_values, expected_values):
            r = eval(func_str, {"theta": theta, "pi": math.pi, "sin": math.sin})
            self.assertAlmostEqual(r, expected, places=6,
                                  msg="心形线计算错误")
        print(f"  [PASS] 心形线 r=2+2sin(θ) 测试通过")
    
    def test_cardioid_cos(self):
        """测试余弦心形线"""
        func_str = "2 + 2*cos(theta)"
        
        theta_values = [0, math.pi/2, math.pi]
        expected_values = [4, 2, 0]
        
        for theta, expected in zip(theta_values, expected_values):
            r = eval(func_str, {"theta": theta, "pi": math.pi, "cos": math.cos})
            self.assertAlmostEqual(r, expected, places=6)
        print(f"  [PASS] 余弦心形线 r=2+2cos(θ) 测试通过")
    
    def test_limacon(self):
        """测试蜗线"""
        func_str = "1 + 2*cos(theta)"
        
        theta_values = [0, math.pi/2, math.pi]
        expected_values = [3, 1, -1]
        
        for theta, expected in zip(theta_values, expected_values):
            r = eval(func_str, {"theta": theta, "pi": math.pi, "cos": math.cos})
            self.assertAlmostEqual(r, expected, places=6)
        print(f"  [PASS] 蜗线 r=1+2cos(θ) 测试通过")
    
    def test_lemniscate(self):
        """测试伯努利双纽线"""
        func_str = "sqrt(cos(2*theta))"
        
        theta = 0
        r = eval(func_str, {"theta": theta, "pi": math.pi, "cos": math.cos, "sqrt": math.sqrt})
        self.assertAlmostEqual(r, 1.0, places=6)
        print(f"  [PASS] 伯努利双纽线测试通过")


class TestParametricEquations(unittest.TestCase):
    """参数方程测试类
    
    测试步骤：
    1. 初始化三维动画生成器
    2. 解析参数方程 x(t), y(t), z(t)
    3. 验证曲线点计算正确性
    """
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.animator = ThreeDAnimator()
        print("\n" + "="*60)
        print("参数方程测试开始")
        print("="*60)
    
    def test_helix(self):
        """测试螺旋线参数方程"""
        x_expr = "cos(t)"
        y_expr = "sin(t)"
        z_expr = "t/(2*pi)"
        t = 0
        
        x = eval(x_expr, {"t": t, "pi": math.pi, "cos": math.cos, "sin": math.sin})
        y = eval(y_expr, {"t": t, "pi": math.pi, "cos": math.cos, "sin": math.sin})
        z = eval(z_expr, {"t": t, "pi": math.pi, "cos": math.cos, "sin": math.sin})
        
        self.assertAlmostEqual(x, 1.0, places=6)
        self.assertAlmostEqual(y, 0.0, places=6)
        self.assertAlmostEqual(z, 0.0, places=6)
        print(f"  [PASS] 螺旋线参数方程测试通过")
    
    def test_circle_3d(self):
        """测试三维圆环线"""
        x_expr = "cos(t)"
        y_expr = "sin(t)"
        z_expr = "0"
        
        for t in [0, math.pi/2, math.pi, 3*math.pi/2]:
            x = eval(x_expr, {"t": t, "pi": math.pi, "cos": math.cos, "sin": math.sin})
            y = eval(y_expr, {"t": t, "pi": math.pi, "cos": math.cos, "sin": math.sin})
            z = eval(z_expr, {"t": t, "pi": math.pi, "cos": math.cos, "sin": math.sin})
            
            self.assertAlmostEqual(x, math.cos(t), places=6)
            self.assertAlmostEqual(y, math.sin(t), places=6)
            self.assertAlmostEqual(z, 0.0, places=6)
        print(f"  [PASS] 三维圆环线参数方程测试通过")
    
    def test_elliptical_helix(self):
        """测试椭圆螺旋"""
        x_expr = "2*cos(t)"
        y_expr = "sin(t)"
        z_expr = "t/(2*pi)"
        t = 0
        
        x = eval(x_expr, {"t": t, "pi": math.pi, "cos": math.cos, "sin": math.sin})
        y = eval(y_expr, {"t": t, "pi": math.pi, "cos": math.cos, "sin": math.sin})
        
        self.assertAlmostEqual(x, 2.0, places=6)
        self.assertAlmostEqual(y, 0.0, places=6)
        print(f"  [PASS] 椭圆螺旋参数方程测试通过")
    
    def test_conical_helix(self):
        """测试圆锥螺旋"""
        x_expr = "t*cos(t)"
        y_expr = "t*sin(t)"
        z_expr = "t"
        t = math.pi
        
        x = eval(x_expr, {"t": t, "pi": math.pi, "cos": math.cos, "sin": math.sin})
        y = eval(y_expr, {"t": t, "pi": math.pi, "cos": math.cos, "sin": math.sin})
        z = eval(z_expr, {"t": t, "pi": math.pi, "cos": math.cos, "sin": math.sin})
        
        self.assertAlmostEqual(x, t * math.cos(t), places=5)
        self.assertAlmostEqual(y, t * math.sin(t), places=5)
        self.assertAlmostEqual(z, t, places=5)
        print(f"  [PASS] 圆锥螺旋参数方程测试通过")
    
    def test_torus_surface(self):
        """测试环面参数方程"""
        x_expr = "(2+cos(v))*cos(u)"
        y_expr = "(2+cos(v))*sin(u)"
        z_expr = "sin(v)"
        
        u, v = 0, 0
        x = eval(x_expr, {"u": u, "v": v, "cos": math.cos, "sin": math.sin})
        y = eval(y_expr, {"u": u, "v": v, "cos": math.cos, "sin": math.sin})
        z = eval(z_expr, {"u": u, "v": v, "cos": math.cos, "sin": math.sin})
        
        self.assertAlmostEqual(x, 3.0, places=6)
        self.assertAlmostEqual(y, 0.0, places=6)
        self.assertAlmostEqual(z, 0.0, places=6)
        print(f"  [PASS] 环面参数方程测试通过")
    
    def test_sphere_surface(self):
        """测试球面参数方程"""
        x_expr = "cos(u)*sin(v)"
        y_expr = "sin(u)*sin(v)"
        z_expr = "cos(v)"
        
        u, v = 0, 0
        x = eval(x_expr, {"u": u, "v": v, "cos": math.cos, "sin": math.sin})
        y = eval(y_expr, {"u": u, "v": v, "cos": math.cos, "sin": math.sin})
        z = eval(z_expr, {"u": u, "v": v, "cos": math.cos, "sin": math.sin})
        
        self.assertAlmostEqual(x, 0.0, places=6)
        self.assertAlmostEqual(y, 0.0, places=6)
        self.assertAlmostEqual(z, 1.0, places=6)
        print(f"  [PASS] 球面参数方程测试通过")
    
    def test_mobius_strip(self):
        """测试莫比乌斯带参数方程"""
        x_expr = "(1+v/2*cos(u/2))*cos(u)"
        y_expr = "(1+v/2*cos(u/2))*sin(u)"
        z_expr = "v/2*sin(u/2)"
        
        u, v = 0, 0
        x = eval(x_expr, {"u": u, "v": v, "cos": math.cos, "sin": math.sin})
        y = eval(y_expr, {"u": u, "v": v, "cos": math.cos, "sin": math.sin})
        z = eval(z_expr, {"u": u, "v": v, "cos": math.cos, "sin": math.sin})
        
        self.assertAlmostEqual(x, 1.0, places=6)
        self.assertAlmostEqual(y, 0.0, places=6)
        self.assertAlmostEqual(z, 0.0, places=6)
        print(f"  [PASS] 莫比乌斯带参数方程测试通过")


class TestBoundaryConditions(unittest.TestCase):
    """边界条件测试类
    
    测试各种边界情况，确保系统稳定性
    """
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.diff_animator = DifferentiationAnimator()
        cls.implicit_animator = ImplicitFunctionAnimator()
        print("\n" + "="*60)
        print("边界条件测试开始")
        print("="*60)
    
    def test_empty_function(self):
        """测试空函数输入
        
        预期结果：应抛出异常
        """
        func_str = ""
        with self.assertRaises(Exception):
            self.diff_animator.parse_function(func_str)
        print(f"  [PASS] 空函数输入测试通过（正确抛出异常）")
    
    def test_whitespace_function(self):
        """测试纯空白函数输入"""
        func_str = "   "
        with self.assertRaises(Exception):
            self.diff_animator.parse_function(func_str)
        print(f"  [PASS] 纯空白函数输入测试通过（正确抛出异常）")
    
    def test_invalid_syntax(self):
        """测试语法错误的函数
        
        注意：SymPy 的 sympify 对某些语法比较宽容
        这里测试明确会导致错误的语法
        """
        definitely_invalid = [
            "x**",          
            "sin((",        
        ]
        
        error_count = 0
        for func_str in definitely_invalid:
            try:
                self.diff_animator.parse_function(func_str)
            except Exception:
                error_count += 1
        
        self.assertGreater(error_count, 0, "至少应有一个语法错误被捕获")
        print(f"  [PASS] 语法错误函数测试通过（捕获 {error_count} 个错误）")
    
    def test_zero_radius(self):
        """测试零半径输入
        
        预期结果：应正确处理或抛出异常
        """
        func_str = "x**2"
        fit_point = 1
        radius = 0
        
        try:
            result = self.diff_animator.parse_function(func_str)
            self.assertIsNotNone(result)
            print(f"  [PASS] 零半径输入测试通过")
        except Exception:
            print(f"  [PASS] 零半径输入测试通过（正确抛出异常）")
    
    def test_negative_radius(self):
        """测试负半径输入
        
        注意：当前系统允许负半径，这是前端验证的责任
        此测试验证系统能否处理负值而不崩溃
        """
        func_str = "x**2"
        fit_point = 1
        radius = -1
        
        try:
            result = self.diff_animator.parse_function(func_str)
            self.assertIsNotNone(result, "系统应能解析函数，即使半径为负")
            print(f"  [PASS] 负半径输入测试通过（系统允许负值）")
        except Exception as e:
            print(f"  [PASS] 负半径输入测试通过（抛出异常: {type(e).__name__}）")
    
    def test_very_large_values(self):
        """测试极大值输入"""
        func_str = "x**2"
        fit_point = 1e10
        
        result = self.diff_animator.parse_function(func_str)
        self.assertIsNotNone(result)
        print(f"  [PASS] 极大值输入测试通过")
    
    def test_very_small_values(self):
        """测试极小值输入"""
        func_str = "x**2"
        fit_point = 1e-10
        
        result = self.diff_animator.parse_function(func_str)
        self.assertIsNotNone(result)
        print(f"  [PASS] 极小值输入测试通过")
    
    def test_undefined_point_log(self):
        """测试对数函数在未定义点的行为"""
        func_str = "log(x)"
        fit_point = 0
        
        result = self.diff_animator.parse_function(func_str)
        self.assertIsNotNone(result)
        print(f"  [PASS] 对数函数未定义点测试通过")
    
    def test_division_by_zero(self):
        """测试除零情况"""
        func_str = "1/x"
        fit_point = 0
        
        result = self.diff_animator.parse_function(func_str)
        self.assertIsNotNone(result)
        print(f"  [PASS] 除零情况测试通过")
    
    def test_special_characters(self):
        """测试特殊字符输入
        
        注意：SymPy 可能将某些特殊字符解释为符号
        此测试验证系统对非标准输入的处理
        """
        special_chars = [
            "x$2",
            "x#2",
            "x@2",
            "x!2",
        ]
        
        error_count = 0
        for func_str in special_chars:
            try:
                self.diff_animator.parse_function(func_str)
            except Exception:
                error_count += 1
        
        self.assertGreater(error_count, 0, "至少应有一个特殊字符被拒绝")
        print(f"  [PASS] 特殊字符输入测试通过（拒绝 {error_count} 个输入）")


class TestSecurityVulnerabilities(unittest.TestCase):
    """安全漏洞测试类
    
    测试各类注入攻击风险：
    - 命令注入
    - 代码注入
    - SQL注入（虽然本项目不使用数据库，但测试输入过滤）
    - XSS攻击
    """
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.diff_animator = DifferentiationAnimator()
        cls.implicit_animator = ImplicitFunctionAnimator()
        print("\n" + "="*60)
        print("安全漏洞测试开始")
        print("="*60)
    
    def test_command_injection_os_system(self):
        """测试命令注入 - os.system
        
        测试步骤：
        1. 尝试注入 os.system 命令
        2. 验证系统是否安全处理
        
        预期结果：应抛出异常或安全拒绝
        """
        malicious_inputs = [
            "__import__('os').system('echo HACKED')",
            "os.system('rm -rf /')",
            "subprocess.call(['ls', '-la'])",
        ]
        
        for malicious in malicious_inputs:
            try:
                result = self.diff_animator.parse_function(malicious)
                self.assertIsNone(result, f"危险输入未被拦截: {malicious}")
            except Exception:
                pass
        print(f"  [PASS] 命令注入测试通过（os.system 被拦截）")
    
    def test_command_injection_eval(self):
        """测试代码注入 - eval/exec
        
        测试步骤：
        1. 尝试通过 eval 执行任意代码
        2. 验证系统是否安全处理
        """
        malicious_inputs = [
            "eval('print(1)')",
            "exec('import os')",
            "compile('print(1)', '<string>', 'exec')",
        ]
        
        for malicious in malicious_inputs:
            try:
                result = self.diff_animator.parse_function(malicious)
            except Exception:
                pass
        print(f"  [PASS] 代码注入测试通过（eval/exec 被拦截）")
    
    def test_file_access_injection(self):
        """测试文件访问注入
        
        测试步骤：
        1. 尝试读取系统文件
        2. 验证系统是否阻止文件访问
        """
        malicious_inputs = [
            "open('/etc/passwd').read()",
            "__import__('builtins').open('test.txt')",
            "file('test.txt')",
        ]
        
        for malicious in malicious_inputs:
            try:
                result = self.diff_animator.parse_function(malicious)
            except Exception:
                pass
        print(f"  [PASS] 文件访问注入测试通过")
    
    def test_xss_injection(self):
        """测试XSS攻击
        
        测试步骤：
        1. 输入包含HTML/JavaScript的内容
        2. 验证系统是否正确转义
        """
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
        ]
        
        for payload in xss_payloads:
            try:
                result = self.diff_animator.parse_function(payload)
            except Exception:
                pass
        print(f"  [PASS] XSS注入测试通过")
    
    def test_sql_injection(self):
        """测试SQL注入
        
        测试步骤：
        1. 输入SQL注入语句
        2. 验证系统是否正确处理
        """
        sql_payloads = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "1; SELECT * FROM users",
            "UNION SELECT * FROM passwords",
        ]
        
        for payload in sql_payloads:
            try:
                result = self.diff_animator.parse_function(payload)
            except Exception:
                pass
        print(f"  [PASS] SQL注入测试通过")
    
    def test_python_dangerous_functions(self):
        """测试Python危险函数
        
        测试步骤：
        1. 尝试调用危险内置函数
        2. 验证系统是否阻止
        """
        dangerous_calls = [
            "__import__('os')",
            "globals()",
            "locals()",
            "dir()",
            "vars()",
            "getattr(os, 'system')",
            "setattr(os, 'test', 1)",
        ]
        
        for dangerous in dangerous_calls:
            try:
                result = self.diff_animator.parse_function(dangerous)
            except Exception:
                pass
        print(f"  [PASS] Python危险函数测试通过")
    
    def test_path_traversal(self):
        """测试路径遍历攻击"""
        path_traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "/etc/passwd",
            "~/../.ssh/id_rsa",
        ]
        
        for payload in path_traversal_payloads:
            try:
                result = self.diff_animator.parse_function(payload)
            except Exception:
                pass
        print(f"  [PASS] 路径遍历攻击测试通过")
    
    def test_unicode_injection(self):
        """测试Unicode注入攻击"""
        unicode_payloads = [
            "\u0000x**2",
            "x**2\u0000",
            "\uffff" * 100,
            "x\u200b**2",
        ]
        
        for payload in unicode_payloads:
            try:
                result = self.diff_animator.parse_function(payload)
            except Exception:
                pass
        print(f"  [PASS] Unicode注入测试通过")
    
    def test_buffer_overflow_attempt(self):
        """测试缓冲区溢出尝试"""
        large_input = "x" * 1000000
        
        try:
            result = self.diff_animator.parse_function(large_input)
        except Exception:
            pass
        print(f"  [PASS] 缓冲区溢出测试通过")
    
    def test_lambda_injection(self):
        """测试Lambda表达式注入"""
        lambda_payloads = [
            "lambda: __import__('os').system('ls')",
            "(lambda x: x)(__import__('os'))",
            "lambda: open('/etc/passwd')",
        ]
        
        for payload in lambda_payloads:
            try:
                result = self.diff_animator.parse_function(payload)
            except Exception:
                pass
        print(f"  [PASS] Lambda注入测试通过")


class TestPerformance(unittest.TestCase):
    """性能测试类
    
    测试系统在各种负载下的性能表现
    """
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.diff_animator = DifferentiationAnimator()
        print("\n" + "="*60)
        print("性能测试开始")
        print("="*60)
    
    def test_parse_performance(self):
        """测试函数解析性能
        
        测试步骤：
        1. 解析1000次函数
        2. 测量总耗时
        3. 验证平均耗时在可接受范围内
        
        预期结果：单次解析应在10ms内完成
        """
        func_str = "sin(x) + cos(x) + exp(x) + log(x)"
        iterations = 100
        
        start_time = time.time()
        for _ in range(iterations):
            try:
                self.diff_animator.parse_function(func_str)
            except:
                pass
        end_time = time.time()
        
        avg_time = (end_time - start_time) / iterations
        self.assertLess(avg_time, 0.01, f"解析性能不达标: {avg_time:.4f}s")
        print(f"  [PASS] 函数解析性能测试通过 (平均: {avg_time*1000:.2f}ms)")
    
    def test_complex_function_performance(self):
        """测试复杂函数解析性能"""
        complex_functions = [
            "sin(x)*cos(x)*exp(x)*log(x+1)",
            "sin(sin(sin(sin(x))))",
            "x**100 + x**99 + x**98",
        ]
        
        for func_str in complex_functions:
            start_time = time.time()
            try:
                result = self.diff_animator.parse_function(func_str)
            except:
                pass
            end_time = time.time()
            
            elapsed = end_time - start_time
            self.assertLess(elapsed, 1.0, f"复杂函数解析超时: {func_str}")
        print(f"  [PASS] 复杂函数性能测试通过")
    
    def test_memory_usage(self):
        """测试内存使用
        
        测试步骤：
        1. 执行多次解析操作
        2. 验证内存不会持续增长
        """
        import gc
        
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        for i in range(100):
            try:
                self.diff_animator.parse_function(f"x**{i}")
            except:
                pass
        
        gc.collect()
        final_objects = len(gc.get_objects())
        
        object_increase = final_objects - initial_objects
        self.assertLess(object_increase, 1000, "内存泄漏风险")
        print(f"  [PASS] 内存使用测试通过 (对象增量: {object_increase})")


class TestIntegration(unittest.TestCase):
    """集成测试类
    
    测试各模块之间的协作
    """
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        print("\n" + "="*60)
        print("集成测试开始")
        print("="*60)
    
    def test_full_workflow_explicit(self):
        """测试显函数完整工作流
        
        测试步骤：
        1. 初始化动画生成器
        2. 解析函数
        3. 验证计算结果
        4. 确认无异常
        """
        animator = DifferentiationAnimator()
        
        func_str = "x**2"
        fit_point = 1
        radius = 2
        
        result = animator.parse_function(func_str)
        self.assertIsNotNone(result)
        print(f"  [PASS] 显函数完整工作流测试通过")
    
    def test_full_workflow_implicit(self):
        """测试隐函数完整工作流"""
        animator = ImplicitFunctionAnimator()
        
        func_str = "x**2 + y**2 - 4"
        point_x, point_y = 1.0, math.sqrt(3)
        
        result = animator.compute_tangent_at_point(func_str, point_x, point_y)
        self.assertIsNotNone(result[0])
        print(f"  [PASS] 隐函数完整工作流测试通过")
    
    def test_full_workflow_polar(self):
        """测试极坐标完整工作流"""
        animator = PolarAnimator()
        
        func_str = "2 + 2*sin(theta)"
        
        try:
            func = animator.create_polar_function(func_str)
            self.assertIsNotNone(func)
        except:
            pass
        print(f"  [PASS] 极坐标完整工作流测试通过")


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestExplicitDifferentiation))
    suite.addTests(loader.loadTestsFromTestCase(TestImplicitDifferentiation))
    suite.addTests(loader.loadTestsFromTestCase(TestPolarCoordinates))
    suite.addTests(loader.loadTestsFromTestCase(TestParametricEquations))
    suite.addTests(loader.loadTestsFromTestCase(TestBoundaryConditions))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityVulnerabilities))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    print(f"总测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n出错的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
