#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化示例 - 结果可视化
用于展示回测结果和算法收敛过程
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import matplotlib.pyplot as plt
from matplotlib import rcParams
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

# 设置中文字体
rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'SimHei']
rcParams['axes.unicode_minus'] = False

from config import Config
from frank_wolfe import ArbitrageOptimizer
from market_simulator import MarketSimulator, generate_test_scenario
from backtester import Backtester


logger = logging.getLogger("polymarket-arb")


def plot_equity_curve(
    equity_curve: List[float],
    save_path: Optional[str] = None,
    title: str = "Equity Curve"
) -> None:
    """
    绘制权益曲线

    Args:
        equity_curve: 权益历史
        save_path: 保存路径
        title: 标题
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(equity_curve, linewidth=2, color='#2196F3')
    ax.fill_between(range(len(equity_curve)), equity_curve, alpha=0.3, color='#2196F3')

    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('Trade', fontsize=12)
    ax.set_ylabel('Capital ($)', fontsize=12)
    ax.grid(True, alpha=0.3)

    # 添加起始和结束标注
    if equity_curve:
        ax.axhline(y=equity_curve[0], color='green', linestyle='--', alpha=0.5, label='Initial Capital')
        ax.axhline(y=equity_curve[-1], color='red', linestyle='--', alpha=0.5, label='Final Capital')
        ax.legend()

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        logger.info(f"权益曲线已保存到: {save_path}")
    else:
        plt.show()

    plt.close()


def plot_convergence(
    objective_values: List[float],
    gap_values: List[float],
    save_path: Optional[str] = None,
    title: str = "Algorithm Convergence"
) -> None:
    """
    绘制算法收敛过程

    Args:
        objective_values: 目标函数值历史
        gap_values: 对偶间隙历史
        save_path: 保存路径
        title: 标题
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # 目标函数值
    iterations = range(len(objective_values))
    ax1.plot(iterations, objective_values, linewidth=2, color='#4CAF50', marker='o', markersize=3)
    ax1.set_title('Objective Function Value', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Iteration', fontsize=10)
    ax1.set_ylabel('Objective Value', fontsize=10)
    ax1.grid(True, alpha=0.3)

    # 对偶间隙
    if gap_values:
        ax2.plot(range(len(gap_values)), gap_values, linewidth=2, color='#FF9800', marker='s', markersize=3)
        ax2.set_title('Duality Gap', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Iteration', fontsize=10)
        ax2.set_ylabel('Gap', fontsize=10)
        ax2.set_yscale('log')
        ax2.grid(True, alpha=0.3)

    plt.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        logger.info(f"收敛曲线已保存到: {save_path}")
    else:
        plt.show()

    plt.close()


def plot_trade_distribution(
    trades: List[Dict[str, Any]],
    save_path: Optional[str] = None,
    title: str = "Trade Distribution"
) -> None:
    """
    绘制交易分布

    Args:
        trades: 交易历史
        save_path: 保存路径
        title: 标题
    """
    if not trades:
        logger.warning("没有交易数据可供可视化")
        return

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 1. 交易金额分布
    amounts = [t['amount'] for t in trades]
    axes[0, 0].hist(amounts, bins=20, color='#2196F3', alpha=0.7, edgecolor='black')
    axes[0, 0].set_title('Trade Amount Distribution', fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel('Amount ($)', fontsize=10)
    axes[0, 0].set_ylabel('Frequency', fontsize=10)
    axes[0, 0].grid(True, alpha=0.3)

    # 2. 交易费用分布
    fees = [t['fee'] for t in trades]
    axes[0, 1].hist(fees, bins=20, color='#FF5722', alpha=0.7, edgecolor='black')
    axes[0, 1].set_title('Fee Distribution', fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel('Fee ($)', fontsize=10)
    axes[0, 1].set_ylabel('Frequency', fontsize=10)
    axes[0, 1].grid(True, alpha=0.3)

    # 3. 资金变化
    capital_after = [t['capital_after'] for t in trades]
    axes[1, 0].plot(capital_after, linewidth=2, color='#4CAF50')
    axes[1, 0].set_title('Capital Over Trades', fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel('Trade #', fontsize=10)
    axes[1, 0].set_ylabel('Capital ($)', fontsize=10)
    axes[1, 0].grid(True, alpha=0.3)

    # 4. 买入 vs 卖出
    buy_count = sum(1 for t in trades if t['type'] == 'buy')
    sell_count = sum(1 for t in trades if t['type'] == 'sell')
    axes[1, 1].pie([buy_count, sell_count], labels=['Buy', 'Sell'],
                   autopct='%1.1f%%', colors=['#4CAF50', '#F44336'],
                   explode=(0.05, 0), startangle=90)
    axes[1, 1].set_title('Buy vs Sell', fontsize=12, fontweight='bold')

    plt.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        logger.info(f"交易分布已保存到: {save_path}")
    else:
        plt.show()

    plt.close()


def plot_performance_comparison(
    scenario_results: Dict[str, Dict[str, float]],
    save_path: Optional[str] = None,
    title: str = "Performance Comparison"
) -> None:
    """
    绘制场景性能对比

    Args:
        scenario_results: 场景结果字典
        save_path: 保存路径
        title: 标题
    """
    scenarios = list(scenario_results.keys())
    returns = [scenario_results[s]['total_return'] * 100 for s in scenarios]
    sharpes = [scenario_results[s]['sharpe_ratio'] for s in scenarios]
    max_drawdowns = [scenario_results[s]['max_drawdown'] * 100 for s in scenarios]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # 收益率
    colors = ['#4CAF50' if r > 0 else '#F44336' for r in returns]
    axes[0].bar(scenarios, returns, color=colors, alpha=0.8, edgecolor='black')
    axes[0].set_title('Total Return (%)', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Return (%)', fontsize=10)
    axes[0].grid(True, alpha=0.3, axis='y')
    axes[0].tick_params(axis='x', rotation=45)

    # Sharpe 比率
    colors = ['#4CAF50' if s > 0 else '#F44336' for s in sharpes]
    axes[1].bar(scenarios, sharpes, color=colors, alpha=0.8, edgecolor='black')
    axes[1].set_title('Sharpe Ratio', fontsize=12, fontweight='bold')
    axes[1].set_ylabel('Sharpe', fontsize=10)
    axes[1].grid(True, alpha=0.3, axis='y')
    axes[1].tick_params(axis='x', rotation=45)

    # 最大回撤
    colors = ['#FF9800' for _ in max_drawdowns]
    axes[2].bar(scenarios, max_drawdowns, color=colors, alpha=0.8, edgecolor='black')
    axes[2].set_title('Max Drawdown (%)', fontsize=12, fontweight='bold')
    axes[2].set_ylabel('Drawdown (%)', fontsize=10)
    axes[2].grid(True, alpha=0.3, axis='y')
    axes[2].tick_params(axis='x', rotation=45)

    plt.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        logger.info(f"性能对比已保存到: {save_path}")
    else:
        plt.show()

    plt.close()


def plot_arbitrage_opportunities(
    opportunities: List[Dict[str, Any]],
    save_path: Optional[str] = None,
    title: str = "Arbitrage Opportunities"
) -> None:
    """
    绘制套利机会

    Args:
        opportunities: 套利机会列表
        save_path: 保存路径
        title: 标题
    """
    if not opportunities:
        logger.warning("没有套利机会可供可视化")
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # 利润率分布
    profit_rates = [opp['profit_rate'] * 100 for opp in opportunities]
    ax1.hist(profit_rates, bins=15, color='#9C27B0', alpha=0.7, edgecolor='black')
    ax1.set_title('Profit Rate Distribution', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Profit Rate (%)', fontsize=10)
    ax1.set_ylabel('Frequency', fontsize=10)
    ax1.grid(True, alpha=0.3)

    # 最大交易金额
    max_trades = [opp['max_trade'] for opp in opportunities]
    ax2.bar(range(len(opportunities)), max_trades, color='#00BCD4', alpha=0.7, edgecolor='black')
    ax2.set_title('Max Trade Amount by Opportunity', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Opportunity #', fontsize=10)
    ax2.set_ylabel('Max Trade ($)', fontsize=10)
    ax2.grid(True, alpha=0.3, axis='y')

    plt.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        logger.info(f"套利机会图已保存到: {save_path}")
    else:
        plt.show()

    plt.close()


def run_visualization_examples():
    """
    运行可视化示例
    """
    print("=" * 60)
    print("可视化示例")
    print("=" * 60)

    # 创建输出目录
    output_dir = "./plots"
    os.makedirs(output_dir, exist_ok=True)

    # 示例 1: 收敛曲线
    print("\n--- 示例 1: 收敛曲线 ---")
    optimizer = ArbitrageOptimizer()
    markets = [
        {'market_id': 'm1', 'price': 0.52},
        {'market_id': 'm2', 'price': 0.47},
        {'market_id': 'm3', 'price': 0.56},
        {'market_id': 'm4', 'price': 0.43}
    ]
    result = optimizer.optimize(markets, capital=10000)

    plot_convergence(
        result['objective_values'],
        result['gap_values'],
        save_path=f"{output_dir}/convergence.png",
        title="Frank-Wolfe Convergence"
    )

    # 示例 2: 回测结果可视化
    print("\n--- 示例 2: 回测结果可视化 ---")
    backtester = Backtester()
    scenario = generate_test_scenario("arbitrage")
    backtest_result = backtester.run_backtest(scenario, capital=10000, verbose=False)

    if backtest_result['trade_history']:
        plot_trade_distribution(
            backtest_result['trade_history'],
            save_path=f"{output_dir}/trades.png"
        )

    # 示例 3: 场景对比
    print("\n--- 示例 3: 场景对比 ---")
    scenario_results = {}
    for scenario_name in ['arbitrage', 'no_arbitrage', 'volatile']:
        scenario_data = generate_test_scenario(scenario_name)
        result = backtester.run_backtest(scenario_data, capital=10000, verbose=False)
        scenario_results[scenario_name] = result['performance']

    plot_performance_comparison(
        scenario_results,
        save_path=f"{output_dir}/comparison.png"
    )

    # 示例 4: 套利机会
    print("\n--- 示例 4: 套利机会可视化 ---")
    simulator = MarketSimulator()
    simulator.generate_markets(num_markets=20, num_related_groups=5)
    opportunities = simulator.find_arbitrage_opportunities(min_profit_rate=0.005)

    if opportunities:
        plot_arbitrage_opportunities(
            opportunities,
            save_path=f"{output_dir}/opportunities.png"
        )

    print(f"\n所有图表已保存到: {output_dir}/")


if __name__ == "__main__":
    # 运行可视化示例
    run_visualization_examples()
