#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bregman Projection 实现 - 约束处理
确保 Frank-Wolfe 的中间解满足所有约束条件
"""

import numpy as np
from typing import Dict, Any, Optional, Tuple
import logging
from scipy.optimize import minimize
from config import Config


logger = logging.getLogger("polymarket-arb")


def bregman_divergence(
    p: np.ndarray,
    q: np.ndarray,
    divergence_type: str = 'entropy'
) -> float:
    """
    计算 Bregman 散度

    Args:
        p: 第一个向量
        q: 第二个向量
        divergence_type: 散度类型 ('entropy', 'norm2')

    Returns:
        Bregman 散度值
    """
    # 添加小常数避免 log(0)
    epsilon = 1e-10
    p = np.maximum(p, epsilon)
    q = np.maximum(q, epsilon)

    if divergence_type == 'entropy':
        # 负熵散度: D(p||q) = sum(p * log(p/q) - p + q)
        divergence = np.sum(p * np.log(p / q) - p + q)
    elif divergence_type == 'norm2':
        # 平方散度: D(p||q) = ||p - q||^2
        divergence = np.sum((p - q) ** 2)
    else:
        raise ValueError(f"未知的散度类型: {divergence_type}")

    return divergence


def bregman_gradient(
    p: np.ndarray,
    divergence_type: str = 'entropy'
) -> np.ndarray:
    """
    计算 Bregman 散度的梯度

    Args:
        p: 向量
        divergence_type: 散度类型

    Returns:
        梯度向量
    """
    epsilon = 1e-10
    p = np.maximum(p, epsilon)

    if divergence_type == 'entropy':
        # ∇h(p) = log(p)
        gradient = np.log(p)
    elif divergence_type == 'norm2':
        # ∇h(p) = 2p
        gradient = 2 * p
    else:
        raise ValueError(f"未知的散度类型: {divergence_type}")

    return gradient


def bregman_hessian_inverse(
    p: np.ndarray,
    divergence_type: str = 'entropy'
) -> np.ndarray:
    """
    计算 Bregman 散度 Hessian 矩阵的逆

    Args:
        p: 向量
        divergence_type: 散度类型

    Returns:
        Hessian 逆矩阵
    """
    epsilon = 1e-10
    p = np.maximum(p, epsilon)

    if divergence_type == 'entropy':
        # Hessian = diag(1/p)
        # Hessian_inv = diag(p)
        hessian_inv = np.diag(p)
    elif divergence_type == 'norm2':
        # Hessian = 2I
        # Hessian_inv = (1/2)I
        hessian_inv = 0.5 * np.eye(len(p))
    else:
        raise ValueError(f"未知的散度类型: {divergence_type}")

    return hessian_inv


def bregman_projection(
    x: np.ndarray,
    x_reference: np.ndarray,
    constraints: Dict[str, Any],
    config: Config
) -> np.ndarray:
    """
    Bregman Projection - 将点投影到可行域

    最小化: D(x_proj || x)  (或者 D(x_proj || x_reference))
    约束: x_proj ∈ 可行域

    Args:
        x: 待投影的点（Frank-Wolfe 的候选解）
        x_reference: 参考点（通常是上一迭代点）
        constraints: 约束条件字典
        config: 配置对象

    Returns:
        投影后的点（满足所有约束）
    """
    n = len(x)
    divergence_type = config.BREGMAN_TYPE

    # 提取约束
    capital = constraints.get('capital', 10000)
    max_position_ratio = constraints.get('max_position_ratio', 0.3)
    max_single_position_ratio = constraints.get('max_single_position_ratio', 0.2)

    # 计算最大持仓
    max_position = capital * max_position_ratio
    max_single_position = capital * max_single_position_ratio

    logger.debug(f"Bregman Projection: 投影到可行域 (资本=${capital})")

    # 定义优化问题
    def objective(y):
        # 最小化 Bregman 散度
        return bregman_divergence(y, x, divergence_type)

    def constraint_sum(y):
        # 预算约束: sum(|y|) * max_price <= capital
        # 这里简化处理：约束绝对值之和
        return capital - np.sum(np.abs(y))

    def constraint_single(y):
        # 单个市场持仓约束
        return max_single_position - np.abs(y)

    # 约束字典
    cons = [
        {'type': 'ineq', 'fun': constraint_sum}
    ]

    # 添加单个市场约束
    for i in range(n):
        cons.append({
            'type': 'ineq',
            'fun': lambda y, i=i: constraint_single(y)[i]
        })

    # 边界
    bounds = [(-max_single_position, max_single_position) for _ in range(n)]

    # 初始猜测
    x0 = x_reference.copy()

    # 优化
    result = minimize(
        objective,
        x0,
        method='SLSQP',
        bounds=bounds,
        constraints=cons,
        options={
            'maxiter': config.BREGMAN_MAX_ITER,
            'ftol': config.BREGMAN_CONVERGENCE_THRESHOLD
        }
    )

    if result.success:
        logger.debug(f"Bregman Projection: 投影成功 (迭代={result.nit})")
        return result.x
    else:
        logger.warning(f"Bregman Projection: 未收敛，返回原点")
        # 如果投影失败，使用简单的截断方法
        x_proj = np.clip(x, -max_single_position, max_single_position)
        # 确保总持仓不超限
        if np.sum(np.abs(x_proj)) > max_position:
            scale = max_position / np.sum(np.abs(x_proj))
            x_proj *= scale
        return x_proj


def simplex_projection(
    x: np.ndarray,
    sum_constraint: float = 1.0
) -> np.ndarray:
    """
    简单多面体投影（欧几里得投影）

    将向量投影到 {x: sum(x) = sum_constraint, x >= 0}

    Args:
        x: 待投影的向量
        sum_constraint: 和约束

    Returns:
        投影后的向量
    """
    n = len(x)

    # 排序并寻找阈值
    u = np.sort(x)[::-1]

    # 寻找最大 rho 满足 sum_{i=1}^{rho} (u_i - theta) = sum_constraint
    # theta = (sum_{i=1}^{rho} u_i - sum_constraint) / rho

    cumsum = np.cumsum(u)
    rho = np.where(u - (cumsum - sum_constraint) / (np.arange(n) + 1) > 0)[0]

    if len(rho) == 0:
        # 所有元素都 <= 0
        theta = 0
    else:
        rho = rho[-1] + 1
        theta = (cumsum[rho - 1] - sum_constraint) / rho

    # 投影
    x_proj = np.maximum(x - theta, 0)

    return x_proj


def l1_ball_projection(
    x: np.ndarray,
    radius: float
) -> np.ndarray:
    """
    L1 球投影

    将向量投影到 {x: ||x||_1 <= radius}

    Args:
        x: 待投影的向量
        radius: L1 球半径

    Returns:
        投影后的向量
    """
    if np.sum(np.abs(x)) <= radius:
        return x

    # 对绝对值排序
    abs_x = np.abs(x)
    u = np.sort(abs_x)[::-1]

    # 寻找阈值
    cumsum = np.cumsum(u)
    rho = np.where(u * (np.arange(len(u)) + 1) - (cumsum - radius) > 0)[0]

    if len(rho) == 0:
        return np.zeros_like(x)

    rho = rho[-1] + 1
    threshold = (cumsum[rho - 1] - radius) / rho

    # 投影
    x_proj = np.sign(x) * np.maximum(abs_x - threshold, 0)

    return x_proj


def box_constraint_projection(
    x: np.ndarray,
    lower: np.ndarray,
    upper: np.ndarray
) -> np.ndarray:
    """
    盒子约束投影

    将向量投影到 {x: lower <= x <= upper}

    Args:
        x: 待投影的向量
        lower: 下界
        upper: 上界

    Returns:
        投影后的向量
    """
    x_proj = np.clip(x, lower, upper)
    return x_proj


class ConstraintManager:
    """
    约束管理器 - 处理各种约束类型
    """

    def __init__(self, config: Config):
        """
        初始化约束管理器

        Args:
            config: 配置对象
        """
        self.config = config
        self.logger = logging.getLogger("polymarket-arb")

    def project_to_constraints(
        self,
        x: np.ndarray,
        x_reference: np.ndarray,
        capital: float,
        markets: int
    ) -> np.ndarray:
        """
        投影到满足所有约束的可行域

        Args:
            x: 待投影的点
            x_reference: 参考点
            capital: 资本
            markets: 市场数量

        Returns:
            投影后的点
        """
        constraints = {
            'dimension': markets,
            'capital': capital,
            'max_position_ratio': self.config.MAX_POSITION_RATIO,
            'max_single_position_ratio': 0.2
        }

        # Bregman Projection
        x_proj = bregman_projection(x, x_reference, constraints, self.config)

        return x_proj

    def check_constraints(
        self,
        x: np.ndarray,
        capital: float
    ) -> bool:
        """
        检查向量是否满足所有约束

        Args:
            x: 向量
            capital: 资本

        Returns:
            是否满足约束
        """
        max_position = capital * self.config.MAX_POSITION_RATIO
        max_single_position = capital * 0.2

        # 检查总持仓
        if np.sum(np.abs(x)) > max_position:
            self.logger.warning(f"违反总持仓约束: {np.sum(np.abs(x))} > {max_position}")
            return False

        # 检查单个市场持仓
        if np.any(np.abs(x) > max_single_position):
            self.logger.warning(f"违反单市场持仓约束")
            return False

        return True


if __name__ == "__main__":
    # 测试 Bregman Projection
    print("=== 测试 Bregman Projection ===")

    from config import Config

    config = Config()

    # 测试 Bregman 散度
    p = np.array([0.3, 0.5, 0.2])
    q = np.array([0.25, 0.45, 0.3])

    div_entropy = bregman_divergence(p, q, 'entropy')
    div_norm2 = bregman_divergence(p, q, 'norm2')

    print(f"熵散度: {div_entropy:.6f}")
    print(f"平方散度: {div_norm2:.6f}")

    # 测试投影
    x = np.array([1000, 2000, 1500])
    x_reference = np.array([500, 1000, 750])

    constraints = {
        'dimension': 3,
        'capital': 10000,
        'max_position_ratio': 0.3,
        'max_single_position_ratio': 0.2
    }

    x_proj = bregman_projection(x, x_reference, constraints, config)

    print(f"\n投影前: {x}")
    print(f"投影后: {x_proj}")

    # 检查约束
    manager = ConstraintManager(config)
    satisfied = manager.check_constraints(x_proj, 10000)
    print(f"约束满足: {satisfied}")
