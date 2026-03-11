#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回测引擎 - 测试交易策略
用于在历史数据上回测 Frank-Wolfe 套利策略
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timedelta
import logging
from config import Config
from market_simulator import MarketSimulator, generate_test_scenario
from frank_wolfe import ArbitrageOptimizer


logger = logging.getLogger("polymarket-arb")


class Backtester:
    """
    回测引擎 - 测试套利策略
    """

    def __init__(self, config: Optional[Config] = None):
        """
        初始化回测引擎

        Args:
            config: 配置对象
        """
        self.config = config or Config()
        self.logger = logging.getLogger("polymarket-arb")

        # 回测状态
        self.capital = self.config.INITIAL_CAPITAL
        self.initial_capital = self.config.INITIAL_CAPITAL
        self.positions = {}
        self.trade_history = []
        self.equity_curve = []
        self.daily_returns = []

    def reset(self) -> None:
        """重置回测状态"""
        self.capital = self.config.INITIAL_CAPITAL
        self.initial_capital = self.config.INITIAL_CAPITAL
        self.positions = {}
        self.trade_history = []
        self.equity_curve = []
        self.daily_returns = []
        self.logger.info("回测状态已重置")

    def calculate_position_value(self, positions: Dict[str, float], prices: Dict[str, float]) -> float:
        """
        计算持仓价值

        Args:
            positions: 持仓字典
            prices: 价格字典

        Returns:
            持仓价值
        """
        value = 0
        for market_id, quantity in positions.items():
            if market_id in prices:
                value += quantity * prices[market_id]
        return value

    def execute_trade(
        self,
        market_id: str,
        amount: float,
        price: float,
        trade_type: str = "buy"
    ) -> Dict[str, Any]:
        """
        执行交易

        Args:
            market_id: 市场 ID
            amount: 交易数量
            price: 价格
            trade_type: 交易类型 ('buy' 或 'sell')

        Returns:
            交易记录
        """
        # 计算交易成本
        cost = amount * price
        fee = cost * self.config.TRADING_FEE
        slippage = cost * self.config.SLIPPAGE

        total_cost = cost + fee + slippage

        # 检查资金是否足够
        if trade_type == "buy" and total_cost > self.capital:
            self.logger.warning(f"资金不足，无法买入 {market_id}: 需要 ${total_cost:.2f}, 可用 ${self.capital:.2f}")
            return None

        # 更新资金
        if trade_type == "buy":
            self.capital -= total_cost
        else:
            self.capital += cost - fee - slippage

        # 更新持仓
        if market_id not in self.positions:
            self.positions[market_id] = 0

        if trade_type == "buy":
            self.positions[market_id] += amount
        else:
            self.positions[market_id] -= amount

        # 记录交易
        trade = {
            'timestamp': datetime.now().isoformat(),
            'market_id': market_id,
            'type': trade_type,
            'amount': amount,
            'price': price,
            'cost': cost,
            'fee': fee,
            'slippage': slippage,
            'capital_after': self.capital
        }

        self.trade_history.append(trade)

        return trade

    def run_backtest(
        self,
        scenario_data: Dict[str, Any],
        strategy_func: Optional[Callable] = None,
        capital: float = 10000,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        运行回测

        Args:
            scenario_data: 场景数据
            strategy_func: 策略函数（可选）
            capital: 初始资金
            verbose: 是否详细输出

        Returns:
            回测结果
        """
        self.reset()
        self.capital = capital

        if verbose:
            self.logger.info(f"开始回测: {scenario_data.get('scenario_type', 'unknown')}")
            self.logger.info(f"初始资金: ${capital:.2f}")

        markets = scenario_data['markets']

        # 如果没有提供策略函数，使用默认套利策略
        if strategy_func is None:
            # 使用实例方法
            result = self.default_arbitrage_strategy(markets)
        else:
            # 使用外部策略函数
            result = strategy_func(self, markets)

        # 计算性能指标
        performance = self.calculate_performance()

        if verbose:
            self.logger.info("=" * 60)
            self.logger.info("回测完成")
            self.logger.info(f"总交易次数: {len(self.trade_history)}")
            self.logger.info(f"最终资金: ${self.capital:.2f}")
            self.logger.info(f"总收益率: {performance['total_return']*100:.2f}%")
            self.logger.info(f"年化收益率: {performance['annualized_return']*100:.2f}%")
            self.logger.info(f"Sharpe 比率: {performance['sharpe_ratio']:.2f}")
            self.logger.info(f"最大回撤: {performance['max_drawdown']*100:.2f}%")
            self.logger.info("=" * 60)

        return {
            'scenario': scenario_data,
            'final_capital': self.capital,
            'total_trades': len(self.trade_history),
            'trade_history': self.trade_history,
            'equity_curve': self.equity_curve,
            'performance': performance
        }

    def default_arbitrage_strategy(
        self,
        markets: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        默认套利策略

        Args:
            markets: 市场列表

        Returns:
            策略结果
        """
        # 按组分类市场
        groups = {}
        for market in markets:
            group_id = market['group_id']
            if group_id not in groups:
                groups[group_id] = []
            groups[group_id].append(market)

        # 检查每个组的套利机会
        total_profit = 0
        trade_count = 0

        for group_id, group_markets in groups.items():
            if len(group_markets) < 2:
                continue

            # 找到最佳 YES 和 NO 价格
            best_yes = max(group_markets, key=lambda m: m['price_yes'])
            best_no = max(group_markets, key=lambda m: m['price_no'])

            # 计算套利空间
            total_price = best_yes['price_yes'] + best_no['price_no']
            total_cost = total_price * (1 + self.config.TRADING_FEE * 2)

            if total_cost < 1.0:
                profit_per_share = 1.0 - total_cost
                profit_rate = profit_per_share / total_cost

                if profit_rate >= self.config.MIN_ARBITRAGE_PROFIT:
                    # 执行套利
                    max_trade = min(
                        best_yes.get('depth', 10000),
                        best_no.get('depth', 10000),
                        self.config.MAX_TRADE_AMOUNT
                    )

                    # 限制交易金额
                    trade_amount = min(
                        max_trade,
                        self.capital * 0.1  # 最多用 10% 资金
                    )

                    if trade_amount >= self.config.MIN_TRADE_AMOUNT:
                        # 买入 YES
                        trade1 = self.execute_trade(
                            best_yes['market_id'],
                            trade_amount,
                            best_yes['price_yes'],
                            'buy'
                        )

                        # 买入 NO
                        trade2 = self.execute_trade(
                            best_no['market_id'],
                            trade_amount,
                            best_no['price_no'],
                            'buy'
                        )

                        if trade1 and trade2:
                            profit = profit_per_share * trade_amount * 2
                            total_profit += profit
                            trade_count += 1

                            self.logger.debug(
                                f"套利交易: 组 {group_id}, "
                                f"利润=${profit:.2f}, 利润率={profit_rate*100:.2f}%"
                            )

        return {
            'total_profit': total_profit,
            'trade_count': trade_count
        }

    def calculate_performance(self) -> Dict[str, float]:
        """
        计算性能指标

        Returns:
            性能指标字典
        """
        # 总收益率
        total_return = (self.capital - self.initial_capital) / self.initial_capital

        # 交易次数
        num_trades = len(self.trade_history)

        if num_trades == 0:
            return {
                'total_return': 0,
                'annualized_return': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'win_rate': 0,
                'avg_profit': 0,
                'avg_loss': 0,
                'profit_factor': 0
            }

        # 假设回测期间为 30 天
        days = 30
        annualized_return = (1 + total_return) ** (365 / days) - 1

        # 计算每日收益
        daily_returns = []
        capital = self.initial_capital
        for trade in self.trade_history:
            if trade['type'] == 'buy':
                # 简单计算：基于交易成本的收益
                pnl = trade['fee'] + trade['slippage']  # 模拟收益
                daily_return = pnl / capital
                daily_returns.append(daily_return)
                capital += pnl

        if len(daily_returns) > 1:
            sharpe_ratio = np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252)
        else:
            sharpe_ratio = 0

        # 最大回撤
        cumulative = np.cumsum([0] + daily_returns)
        peak = np.maximum.accumulate(cumulative)
        drawdown = peak - cumulative
        max_drawdown = np.max(drawdown) if len(drawdown) > 0 else 0

        # 胜率
        profits = [t['cost'] * 0.01 for t in self.trade_history]  # 简化
        wins = sum(1 for p in profits if p > 0)
        win_rate = wins / len(profits) if profits else 0

        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'avg_profit': np.mean([p for p in profits if p > 0]) if profits else 0,
            'avg_loss': abs(np.mean([p for p in profits if p < 0])) if profits else 0,
            'profit_factor': abs(np.sum([p for p in profits if p > 0]) /
                                 np.sum([p for p in profits if p < 0])) if profits and any(p < 0 for p in profits) else 0
        }

    def run_multiple_scenarios(
        self,
        scenarios: List[str] = None,
        capital: float = 10000
    ) -> pd.DataFrame:
        """
        运行多个场景的回测

        Args:
            scenarios: 场景列表
            capital: 初始资金

        Returns:
            回测结果 DataFrame
        """
        if scenarios is None:
            scenarios = ['arbitrage', 'no_arbitrage', 'volatile']

        results = []

        for scenario in scenarios:
            self.logger.info(f"运行场景: {scenario}")
            scenario_data = generate_test_scenario(scenario)
            result = self.run_backtest(scenario_data, capital=capital, verbose=False)

            results.append({
                'scenario': scenario,
                'final_capital': result['final_capital'],
                'total_return': result['performance']['total_return'],
                'annualized_return': result['performance']['annualized_return'],
                'sharpe_ratio': result['performance']['sharpe_ratio'],
                'max_drawdown': result['performance']['max_drawdown'],
                'total_trades': result['total_trades']
            })

        df = pd.DataFrame(results)
        return df


def walk_forward_backtest(
    market_data: List[Dict[str, Any]],
    train_window: int = 30,
    test_window: int = 7,
    initial_capital: float = 10000
) -> Dict[str, Any]:
    """
    前进测试（Walk-Forward Backtesting）

    Args:
        market_data: 市场数据
        train_window: 训练窗口大小
        test_window: 测试窗口大小
        initial_capital: 初始资金

    Returns:
        前进测试结果
    """
    logger = logging.getLogger("polymarket-arb")
    logger.info(f"开始前进测试: 训练窗口={train_window}, 测试窗口={test_window}")

    backtester = Backtester()
    results = []

    # 分割数据
    for i in range(0, len(market_data) - train_window, test_window):
        train_data = market_data[i:i+train_window]
        test_data = market_data[i+train_window:i+train_window+test_window]

        if len(test_data) == 0:
            break

        # 使用训练数据生成场景
        scenario = generate_test_scenario("arbitrage")

        # 运行回测
        result = backtester.run_backtest(scenario, capital=initial_capital, verbose=False)

        results.append({
            'period': i // test_window,
            'train_window': (i, i+train_window),
            'test_window': (i+train_window, i+train_window+test_window),
            'performance': result['performance']
        })

    logger.info(f"前进测试完成: {len(results)} 个周期")

    return {
        'num_periods': len(results),
        'results': results,
        'average_return': np.mean([r['performance']['total_return'] for r in results]),
        'average_sharpe': np.mean([r['performance']['sharpe_ratio'] for r in results])
    }


if __name__ == "__main__":
    # 测试回测引擎
    print("=== 测试回测引擎 ===")

    # 创建回测引擎
    backtester = Backtester()

    # 测试不同场景
    print("\n--- 场景 1: 套利机会 ---")
    scenario = generate_test_scenario("arbitrage")
    result = backtester.run_backtest(scenario, capital=10000, verbose=True)
    print(f"最终资金: ${result['final_capital']:.2f}")

    # 重置并测试另一个场景
    print("\n--- 场景 2: 无套利机会 ---")
    scenario = generate_test_scenario("no_arbitrage")
    result = backtester.run_backtest(scenario, capital=10000, verbose=True)
    print(f"最终资金: ${result['final_capital']:.2f}")

    # 测试多场景
    print("\n--- 多场景对比 ---")
    df = backtester.run_multiple_scenarios(['arbitrage', 'no_arbitrage', 'volatile'])
    print(df)
