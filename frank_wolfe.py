#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Frank-Wolfe 算法实现 - 套利优化
用于在预测市场中寻找最优套利路径
"""

import numpy as np
from typing import Tuple, List, Dict, Any, Callable, Optional
import logging
from config import Config
from bregman_projection import bregman_projection


logger = logging.getLogger("polymarket-arb")


def frank_wolfe(
    objective_func: Callable[[np.ndarray], float],
    gradient_func: Callable[[np.ndarray], np.ndarray],
    linear_optimization: Callable[[np.ndarray], Tuple[np.ndarray, np.ndarray]],
    initial_x: Optional[np.ndarray] = None,
    constraints: Optional[Dict[str, Any]] = None,
    config: Optional[Config] = None
) -> Dict[str, Any]:
    """
    Frank-Wolfe 条件梯度算法

    Args:
        objective_func: 目标函数 f(x)
        gradient_func: 梯度函数 ∇f(x)
        linear_optimization: 线性优化函数，返回最优搜索方向
        initial_x: 初始点（如果为 None，自动初始化）
        constraints: 约束条件字典
        config: 配置对象

    Returns:
        包含解、目标函数值、迭代历史等的字典
    """
    if config is None:
        config = Config()

    # 获取维度
    if constraints and 'dimension' in constraints:
        dimension = constraints['dimension']
    elif initial_x is not None:
        dimension = len(initial_x)
    else:
        raise ValueError("必须提供 dimension 或 initial_x")

    # 初始化解
    if initial_x is None:
        x = np.zeros(dimension)
        logger.info(f"Frank-Wolfe: 初始化 x 为零向量 (维度={dimension})")
    else:
        x = initial_x.copy()
        logger.info(f"Frank-Wolfe: 使用给定的初始点 (维度={dimension})")

    # 记录历史
    history = {
        'objective_values': [],
        'x_values': [],
        'gap_values': [],
        'iterations': 0
    }

    # 初始目标函数值
    obj_value = objective_func(x)
    history['objective_values'].append(obj_value)
    history['x_values'].append(x.copy())

    logger.info(f"Frank-Wolfe: 开始迭代 (最大={config.MAX_ITERATIONS})")
    logger.info(f"Frank-Wolfe: 初始目标值 = {obj_value:.6f}")

    # 开始迭代
    for iteration in range(config.MAX_ITERATIONS):
        # 计算梯度
        gradient = gradient_func(x)

        # 线性优化：找到使梯度下降方向最优的点
        # 最小化 gradientᵀ(y - x) 等价于 最小化 gradientᵀy
        # 因为 gradientᵀx 是常数
        y, _ = linear_optimization(gradient)

        # 计算方向
        direction = y - x

        # 计算对偶间隙（收敛指标）
        duality_gap = np.dot(gradient, direction)
        history['gap_values'].append(duality_gap)

        # 检查收敛
        if abs(duality_gap) < config.CONVERGENCE_THRESHOLD and iteration >= config.MIN_ITERATIONS:
            logger.info(f"Frank-Wolfe: 收敛! 迭代={iteration+1}, 间隙={duality_gap:.6e}")
            break

        # 计算步长（线搜索或固定步长）
        step_size = compute_step_size(
            x, direction, objective_func, gradient, iteration, config
        )

        # 更新解
        x_new = x + step_size * direction

        # Bregman Projection（如果有约束）
        if constraints:
            x_new = bregman_projection(
                x_new, x, constraints, config
            )

        # 计算新目标函数值
        obj_value_new = objective_func(x_new)

        # 如果目标函数改善，接受更新
        if obj_value_new < obj_value or iteration == 0:
            x = x_new
            obj_value = obj_value_new
            logger.debug(f"Iter {iteration+1}: obj={obj_value:.6f}, gap={duality_gap:.6f}, step={step_size:.6f}")
        else:
            # 如果没有改善，减小步长重试
            logger.debug(f"Iter {iteration+1}: 目标函数未改善，减小步长")
            step_size *= config.STEP_DECAY
            if step_size < 1e-10:
                logger.warning(f"Iter {iteration+1}: 步长过小，停止迭代")
                break

        # 记录历史
        history['objective_values'].append(obj_value)
        history['x_values'].append(x.copy())
        history['iterations'] = iteration + 1

    # 最终结果
    logger.info(f"Frank-Wolfe: 完成! 最终目标值 = {obj_value:.6f}, 迭代次数 = {history['iterations']}")

    result = {
        'x': x,
        'objective_value': obj_value,
        'history': history,
        'converged': abs(history['gap_values'][-1]) < config.CONVERGENCE_THRESHOLD if history['gap_values'] else False
    }

    return result


def compute_step_size(
    x: np.ndarray,
    direction: np.ndarray,
    objective_func: Callable[[np.ndarray], float],
    gradient: np.ndarray,
    iteration: int,
    config: Config,
    max_line_search: int = 10
) -> float:
    """
    计算最优步长

    Args:
        x: 当前点
        direction: 搜索方向
        objective_func: 目标函数
        gradient: 梯度
        iteration: 当前迭代次数
        config: 配置对象
        max_line_search: 最大线搜索次数

    Returns:
        步长
    """
    # 方法 1: 递减步长 2/(k+2)
    step_size = 2.0 / (iteration + 2)

    # 方法 2: 线搜索（如果目标函数可计算）
    try:
        # 简单的 Armijo 线搜索
        alpha = 1.0
        beta = 0.5  # 衰减因子
        c = 0.1  # 充分下降常数

        f_current = objective_func(x)
        grad_dot_d = np.dot(gradient, direction)

        for _ in range(max_line_search):
            x_new = x + alpha * direction
            f_new = objective_func(x_new)

            # Armijo 条件: f(x + αd) ≤ f(x) + cα∇f(x)ᵀd
            if f_new <= f_current + c * alpha * grad_dot_d:
                return alpha

            alpha *= beta

        # 如果线搜索失败，使用递减步长
        return 2.0 / (iteration + 2)

    except Exception as e:
        logger.debug(f"线搜索失败，使用递减步长: {e}")
        return 2.0 / (iteration + 2)


def arbitrage_objective(
    x: np.ndarray,
    prices: np.ndarray,
    transaction_costs: np.ndarray,
    risk_aversion: float = 1.0
) -> float:
    """
    套利目标函数：最小化负收益 + 风险惩罚

    Args:
        x: 交易向量（正数=买入，负数=卖出）
        prices: 价格向量
        transaction_costs: 交易成本向量
        risk_aversion: 风险厌恶系数

    Returns:
        目标函数值
    """
    # 预期收益
    expected_return = np.sum(x * (1.0 - prices) - transaction_costs)

    # 风险惩罚（持仓的方差）
    risk = risk_aversion * np.var(x)

    # 最小化负收益 + 风险
    objective = -expected_return + risk

    return objective


def arbitrage_gradient(
    x: np.ndarray,
    prices: np.ndarray,
    transaction_costs: np.ndarray,
    risk_aversion: float = 1.0
) -> np.ndarray:
    """
    套利目标函数的梯度

    Args:
        x: 交易向量
        prices: 价格向量
        transaction_costs: 交易成本向量
        risk_aversion: 风险厌恶系数

    Returns:
        梯度向量
    """
    # ∇(-expected_return) = -(1 - prices - transaction_costs)
    # ∇(risk) = 2 * risk_aversion * (x - mean(x))
    # 实际上风险 = risk_aversion * (sum(x^2) / n - (sum(x)/n)^2)
    # ∇risk = 2 * risk_aversion * (x/n - mean(x)/n) = 2 * risk_aversion * (x - mean(x)) / n

    n = len(x)
    mean_x = np.mean(x)

    gradient = -(1.0 - prices - transaction_costs) + 2 * risk_aversion * (x - mean_x) / n

    return gradient


def arbitrage_linear_optimization(
    gradient: np.ndarray,
    price_sum_constraint: float = 1.0,
    max_position: float = 1.0,
    min_position: float = -1.0
) -> Tuple[np.ndarray, np.ndarray]:
    """
    套利问题的线性优化（最陡下降方向）

    最小化: gradientᵀ * y
    约束:
        - sum(y) = price_sum_constraint (YES + NO = $1.00)
        - min_position ≤ y ≤ max_position

    Args:
        gradient: 梯度向量
        price_sum_constraint: 价格和约束
        max_position: 最大持仓
        min_position: 最小持仓

    Returns:
        (最优方向, 约束向量)
    """
    n = len(gradient)

    # 问题简化：找到梯度最小的元素，把所有权重给它
    # 但要满足 sum(y) = price_sum_constraint

    # 方法：将所有权重放在梯度最小的元素上
    min_idx = np.argmin(gradient)
    y = np.zeros(n)
    y[min_idx] = price_sum_constraint

    # 确保满足边界约束
    if y[min_idx] > max_position:
        y[min_idx] = max_position
        # 分配剩余给梯度次小的
        remaining = price_sum_constraint - max_position
        idx_sorted = np.argsort(gradient)
        for idx in idx_sorted[1:]:  # 跳过已经分配的
            if remaining <= 0:
                break
            y[idx] = min(remaining, max_position)
            remaining -= y[idx]

    return y, np.array([price_sum_constraint])


class ArbitrageOptimizer:
    """
    套利优化器 - 封装 Frank-Wolfe 算法
    """

    def __init__(self, config: Optional[Config] = None):
        """
        初始化优化器

        Args:
            config: 配置对象
        """
        self.config = config or Config()
        self.logger = logging.getLogger("polymarket-arb")

    def optimize(
        self,
        markets: List[Dict[str, Any]],
        capital: float = 10000,
        risk_aversion: float = 1.0
    ) -> Dict[str, Any]:
        """
        优化套利交易

        Args:
            markets: 市场列表
            capital: 可用资金
            risk_aversion: 风险厌恶系数

        Returns:
            优化结果
        """
        self.logger.info(f"开始优化套利交易 (市场数={len(markets)}, 资金=${capital})")

        # 构建价格向量
        prices = np.array([m['price'] for m in markets])
        transaction_costs = np.array([
            m['price'] * self.config.TRADING_FEE for m in markets
        ])

        # 定义目标函数和梯度
        objective_func = lambda x: arbitrage_objective(
            x, prices, transaction_costs, risk_aversion
        )

        gradient_func = lambda x: arbitrage_gradient(
            x, prices, transaction_costs, risk_aversion
        )

        # 定义线性优化（考虑预算约束）
        def linear_optimization(gradient):
            # 预算约束: sum(|x|) * max_price <= capital
            max_price = np.max(prices)
            max_abs_position = capital / (max_price * len(prices))

            return arbitrage_linear_optimization(
                gradient,
                price_sum_constraint=1.0,
                max_position=max_abs_position,
                min_position=-max_abs_position
            )

        # 约束
        constraints = {
            'dimension': len(markets),
            'capital': capital,
            'max_position_ratio': self.config.MAX_POSITION_RATIO
        }

        # 运行 Frank-Wolfe
        result = frank_wolfe(
            objective_func,
            gradient_func,
            linear_optimization,
            constraints=constraints,
            config=self.config
        )

        # 计算实际交易
        optimal_trades = result['x']

        # 计算预期利润
        expected_profit = -result['objective_value'] * capital

        # 构建结果
        optimization_result = {
            'trades': optimal_trades,
            'expected_profit': expected_profit,
            'profit_rate': expected_profit / capital,
            'converged': result['converged'],
            'iterations': result['history']['iterations'],
            'objective_values': result['history']['objective_values'],
            'gap_values': result['history']['gap_values']
        }

        self.logger.info(f"优化完成: 预期利润=${expected_profit:.2f}, 利润率={optimization_result['profit_rate']*100:.2f}%")

        return optimization_result


if __name__ == "__main__":
    # 测试 Frank-Wolfe 算法
    print("=== 测试 Frank-Wolfe 算法 ===")

    # 模拟市场数据
    markets = [
        {'market_id': 'market_a_yes', 'price': 0.52},
        {'market_id': 'market_a_no', 'price': 0.47},
        {'market_id': 'market_b_yes', 'price': 0.56},
        {'market_id': 'market_b_no', 'price': 0.43}
    ]

    # 创建优化器
    optimizer = ArbitrageOptimizer()

    # 运行优化
    result = optimizer.optimize(markets, capital=10000)

    print(f"\n优化结果:")
    print(f"预期利润: ${result['expected_profit']:.2f}")
    print(f"利润率: {result['profit_rate']*100:.2f}%")
    print(f"收敛: {'是' if result['converged'] else '否'}")
    print(f"迭代次数: {result['iterations']}")

    print(f"\n最优交易:")
    for i, trade in enumerate(result['trades']):
        print(f"  {markets[i]['market_id']}: ${trade:.2f}")
