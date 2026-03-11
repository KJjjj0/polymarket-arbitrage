#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础套利示例 - Frank-Wolfe 算法演示
展示如何使用 Frank-Wolfe 优化器进行套利
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import numpy as np
import logging
from config import Config
from frank_wolfe import ArbitrageOptimizer, frank_wolfe, arbitrage_objective, arbitrage_gradient, arbitrage_linear_optimization
from market_simulator import MarketSimulator, generate_test_scenario
from backtester import Backtester
from utils import setup_logging


def example_1_basic_arbitrage():
    """
    示例 1: 基础套利优化
    演示如何使用 Frank-Wolfe 算法优化套利交易
    """
    print("=" * 60)
    print("示例 1: 基础套利优化")
    print("=" * 60)

    # 设置日志
    logger = setup_logging("INFO", verbose=False)

    # 创建配置
    config = Config()

    # 创建模拟市场数据
    markets = [
        {'market_id': 'trump_yes_1', 'price': 0.52, 'depth': 10000},
        {'market_id': 'trump_no_1', 'price': 0.47, 'depth': 10000},
        {'market_id': 'trump_yes_2', 'price': 0.56, 'depth': 8000},
        {'market_id': 'trump_no_2', 'price': 0.43, 'depth': 8000},
    ]

    print(f"\n市场数据:")
    for m in markets:
        print(f"  {m['market_id']}: 价格=${m['price']:.4f}, 深度=${m['depth']:.0f}")

    # 创建优化器
    optimizer = ArbitrageOptimizer(config)

    # 运行优化
    print("\n运行 Frank-Wolfe 优化...")
    result = optimizer.optimize(markets, capital=10000)

    # 显示结果
    print(f"\n优化结果:")
    print(f"  预期利润: ${result['expected_profit']:.2f}")
    print(f"  利润率: {result['profit_rate']*100:.2f}%")
    print(f"  收敛: {'是' if result['converged'] else '否'}")
    print(f"  迭代次数: {result['iterations']}")

    print(f"\n最优交易:")
    for i, trade in enumerate(result['trades']):
        if abs(trade) > 0.01:
            print(f"  {markets[i]['market_id']}: ${trade:.2f}")

    return result


def example_2_market_simulation():
    """
    示例 2: 市场模拟和套利机会检测
    """
    print("\n" + "=" * 60)
    print("示例 2: 市场模拟和套利机会检测")
    print("=" * 60)

    # 创建模拟器
    simulator = MarketSimulator()

    # 生成测试市场
    print("\n生成模拟市场...")
    markets = simulator.generate_markets(num_markets=20, num_related_groups=5)

    print(f"生成了 {len(markets)} 个市场")

    # 查找套利机会
    print("\n查找套利机会...")
    opportunities = simulator.find_arbitrage_opportunities(
        min_profit_rate=0.005,  # 0.5% 最低利润率
        fee_rate=0.01  # 1% 手续费
    )

    if opportunities:
        print(f"\n发现 {len(opportunities)} 个套利机会:")
        for opp in opportunities:
            print(f"  事件 {opp['group_id']}:")
            print(f"    最佳 YES 价格: ${opp['best_yes_price']:.4f}")
            print(f"    最佳 NO 价格: ${opp['best_no_price']:.4f}")
            print(f"    总成本: ${opp['total_cost']:.4f}")
            print(f"    利润率: {opp['profit_rate']*100:.2f}%")
            print(f"    最大交易: ${opp['max_trade']:.2f}")
    else:
        print("未发现套利机会")

    return opportunities


def example_3_backtest():
    """
    示例 3: 回测策略
    """
    print("\n" + "=" * 60)
    print("示例 3: 回测策略")
    print("=" * 60)

    # 创建回测引擎
    backtester = Backtester()

    # 使用不同场景进行回测
    scenarios = ['arbitrage', 'no_arbitrage', 'volatile']

    results = []

    for scenario in scenarios:
        print(f"\n--- 场景: {scenario} ---")

        # 生成场景数据
        scenario_data = generate_test_scenario(scenario)

        # 运行回测
        result = backtester.run_backtest(
            scenario_data,
            capital=10000,
            verbose=False
        )

        # 显示结果
        print(f"  交易次数: {result['total_trades']}")
        print(f"  最终资金: ${result['final_capital']:.2f}")
        print(f"  总收益率: {result['performance']['total_return']*100:.2f}%")
        print(f"  Sharpe 比率: {result['performance']['sharpe_ratio']:.2f}")

        results.append(result)

    return results


def example_4_custom_strategy():
    """
    示例 4: 自定义策略
    展示如何编写自定义交易策略
    """
    print("\n" + "=" * 60)
    print("示例 4: 自定义策略")
    print("=" * 60)

    # 定义自定义策略
    def my_strategy(backtester, markets):
        """
        我的自定义套利策略

        Args:
            backtester: 回测引擎实例
            markets: 市场列表

        Returns:
            策略结果
        """
        print("  执行自定义策略...")

        # 按组分类
        groups = {}
        for m in markets:
            gid = m['group_id']
            if gid not in groups:
                groups[gid] = []
            groups[gid].append(m)

        total_profit = 0
        trade_count = 0

        # 遍历每个组
        for gid, gmarkets in groups.items():
            if len(gmarkets) < 2:
                continue

            # 找最佳 YES 和 NO
            best_yes = max(gmarkets, key=lambda x: x['price_yes'])
            best_no = max(gmarkets, key=lambda x: x['price_no'])

            # 计算成本
            total = best_yes['price_yes'] + best_no['price_no']
            cost = total * 1.02  # 考虑手续费

            if cost < 1.0:
                profit = (1.0 - cost) * backtester.capital * 0.05
                if profit > 0:
                    total_profit += profit
                    trade_count += 1
                    print(f"    交易: 组 {gid}, 利润 ${profit:.2f}")

        return {
            'total_profit': total_profit,
            'trade_count': trade_count
        }

    # 创建回测引擎
    backtester = Backtester()

    # 生成场景
    scenario = generate_test_scenario("arbitrage")

    # 运行回测
    print("\n运行自定义策略...")
    result = backtester.run_backtest(
        scenario,
        strategy_func=my_strategy,
        capital=10000,
        verbose=False
    )

    print(f"\n自定义策略结果:")
    print(f"  交易次数: {result['total_trades']}")
    print(f"  最终资金: ${result['final_capital']:.2f}")

    return result


def example_5_frank_wolfe_algorithm():
    """
    示例 5: Frank-Wolfe 算法底层演示
    展示算法内部工作原理
    """
    print("\n" + "=" * 60)
    print("示例 5: Frank-Wolfe 算法底层演示")
    print("=" * 60)

    # 设置问题参数
    n = 4  # 4 个市场
    prices = np.array([0.52, 0.47, 0.56, 0.43])
    transaction_costs = prices * 0.01

    print(f"\n市场数量: {n}")
    print(f"价格: {prices}")
    print(f"交易成本: {transaction_costs}")

    # 定义目标函数
    objective_func = lambda x: arbitrage_objective(x, prices, transaction_costs)
    gradient_func = lambda x: arbitrage_gradient(x, prices, transaction_costs)
    linear_optimization = lambda g: arbitrage_linear_optimization(g, 1.0, 0.3, -0.3)

    # 运行 Frank-Wolfe
    print("\n运行 Frank-Wolfe 算法...")
    result = frank_wolfe(
        objective_func,
        gradient_func,
        linear_optimization,
        initial_x=np.zeros(n),
        config=Config()
    )

    # 显示结果
    print(f"\n优化结果:")
    print(f"  最优解: {result['x']}")
    print(f"  目标函数值: {result['objective_value']:.6f}")
    print(f"  收敛: {'是' if result['converged'] else '否'}")
    print(f"  迭代次数: {result['history']['iterations']}")

    # 显示迭代历史
    print(f"\n迭代历史:")
    for i, obj in enumerate(result['history']['objective_values'][:10]):
        gap = result['history']['gap_values'][i] if i < len(result['history']['gap_values']) else 0
        print(f"  迭代 {i}: 目标值 = {obj:.6f}, 间隙 = {gap:.6f}")

    return result


def run_all_examples():
    """
    运行所有示例
    """
    print("\n" + "=" * 60)
    print("Frank-Wolfe 套利算法 - 完整示例")
    print("=" * 60)

    # 运行所有示例
    example_1_basic_arbitrage()
    example_2_market_simulation()
    example_3_backtest()
    example_4_custom_strategy()
    example_5_frank_wolfe_algorithm()

    print("\n" + "=" * 60)
    print("所有示例完成！")
    print("=" * 60)


if __name__ == "__main__":
    # 运行所有示例
    run_all_examples()
