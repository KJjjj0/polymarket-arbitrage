#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
市场模拟器 - 生成测试数据
用于测试 Frank-Wolfe 套利算法
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from config import Config


logger = logging.getLogger("polymarket-arb")


class MarketSimulator:
    """
    市场模拟器 - 生成预测市场模拟数据
    """

    def __init__(self, config: Optional[Config] = None):
        """
        初始化市场模拟器

        Args:
            config: 配置对象
        """
        self.config = config or Config()
        self.markets = []
        self.price_history = []

    def generate_markets(
        self,
        num_markets: int = 10,
        num_related_groups: int = 3,
        seed: Optional[int] = 42
    ) -> List[Dict[str, Any]]:
        """
        生成模拟市场

        Args:
            num_markets: 市场数量
            num_related_groups: 相关市场组数量（用于套利）
            seed: 随机种子

        Returns:
            市场列表
        """
        if seed is not None:
            np.random.seed(seed)

        self.markets = []

        # 生成相关市场组（同一事件的不同市场，用于套利）
        for group_id in range(num_related_groups):
            # 每个组 2-4 个市场（YES/NO 对）
            markets_in_group = np.random.randint(2, 5)

            for i in range(markets_in_group):
                # 生成真实概率（0.1 到 0.9 之间）
                true_prob = np.random.uniform(0.1, 0.9)

                # 市场价格围绕真实概率波动（模拟市场效率差异）
                # 有些市场更接近真实概率，有些有较大偏差
                efficiency = np.random.uniform(0.8, 1.0)
                market_price = true_prob * efficiency + np.random.uniform(-0.05, 0.05)
                market_price = np.clip(market_price, 0.05, 0.95)

                # YES 和 NO 价格
                price_yes = market_price
                price_no = 1.0 - market_price

                # 市场深度（流动性）
                depth = np.random.uniform(1000, 50000)

                # 波动性
                volatility = np.random.uniform(0.01, 0.05)

                market = {
                    'market_id': f'group_{group_id}_market_{i}',
                    'group_id': group_id,
                    'event': f'Event_{group_id}',
                    'description': f'Related market {i} for event {group_id}',
                    'price_yes': price_yes,
                    'price_no': price_no,
                    'true_probability': true_prob,
                    'depth': depth,
                    'volatility': volatility,
                    'created_at': datetime.now().isoformat()
                }

                self.markets.append(market)

        logger.info(f"生成了 {len(self.markets)} 个模拟市场 ({num_related_groups} 组)")

        return self.markets

    def simulate_price_movement(
        self,
        market_id: str,
        steps: int = 100,
        seed: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        模拟市场价格走势（几何布朗运动）

        Args:
            market_id: 市场 ID
            steps: 模拟步数
            seed: 随机种子

        Returns:
            价格历史
        """
        if seed is not None:
            np.random.seed(seed)

        # 找到市场
        market = None
        for m in self.markets:
            if m['market_id'] == market_id:
                market = m
                break

        if market is None:
            logger.warning(f"市场 {market_id} 不存在")
            return []

        # 参数
        initial_price = market['price_yes']
        drift = 0  # 无漂移（有效市场假设）
        volatility = market['volatility']
        dt = 1  # 每天一步

        # 模拟价格路径
        prices = [initial_price]
        for _ in range(steps):
            # 几何布朗运动
            shock = np.random.normal(0, 1)
            new_price = prices[-1] * np.exp(
                (drift - 0.5 * volatility**2) * dt + volatility * np.sqrt(dt) * shock
            )
            new_price = np.clip(new_price, 0.01, 0.99)
            prices.append(new_price)

        # 记录历史
        history = []
        for i, price in enumerate(prices):
            history.append({
                'step': i,
                'price_yes': price,
                'price_no': 1 - price,
                'timestamp': (datetime.now() + timedelta(minutes=i)).isoformat()
            })

        return history

    def find_arbitrage_opportunities(
        self,
        min_profit_rate: float = 0.01,
        fee_rate: float = 0.01
    ) -> List[Dict[str, Any]]:
        """
        寻找套利机会

        Args:
            min_profit_rate: 最小利润率阈值
            fee_rate: 交易手续费率

        Returns:
            套利机会列表
        """
        opportunities = []

        # 按组分类市场
        groups = {}
        for market in self.markets:
            group_id = market['group_id']
            if group_id not in groups:
                groups[group_id] = []
            groups[group_id].append(market)

        # 检查每个组
        for group_id, group_markets in groups.items():
            if len(group_markets) < 2:
                continue

            # 找到最佳 YES 和 NO 价格
            best_yes_price = max(m['price_yes'] for m in group_markets)
            best_no_price = max(m['price_no'] for m in group_markets)

            # 计算总成本
            total_cost = best_yes_price + best_no_price

            # 考虑手续费
            total_cost_with_fee = total_cost * (1 + fee_rate * 2)

            if total_cost_with_fee < 1.0:
                # 存在套利机会
                profit_per_share = 1.0 - total_cost_with_fee
                profit_rate = profit_per_share / total_cost_with_fee

                if profit_rate >= min_profit_rate:
                    opportunity = {
                        'group_id': group_id,
                        'event': group_markets[0]['event'],
                        'best_yes_price': best_yes_price,
                        'best_no_price': best_no_price,
                        'total_cost': total_cost,
                        'profit_per_share': profit_per_share,
                        'profit_rate': profit_rate,
                        'max_trade': min(m['depth'] for m in group_markets),
                        'timestamp': datetime.now().isoformat()
                    }
                    opportunities.append(opportunity)

        logger.info(f"发现 {len(opportunities)} 个套利机会")

        return opportunities

    def get_market_state(self) -> Dict[str, Any]:
        """
        获取当前市场状态

        Returns:
            市场状态字典
        """
        # 按组统计
        groups = {}
        for market in self.markets:
            group_id = market['group_id']
            if group_id not in groups:
                groups[group_id] = {
                    'markets': [],
                    'avg_price': 0,
                    'total_depth': 0
                }
            groups[group_id]['markets'].append(market['market_id'])
            groups[group_id]['avg_price'] += market['price_yes']
            groups[group_id]['total_depth'] += market['depth']

        # 计算平均值
        for group_id in groups:
            n = len(groups[group_id]['markets'])
            groups[group_id]['avg_price'] /= n

        return {
            'total_markets': len(self.markets),
            'total_groups': len(groups),
            'groups': groups,
            'timestamp': datetime.now().isoformat()
        }

    def simulate_order_book(
        self,
        market_id: str,
        levels: int = 10
    ) -> Dict[str, Any]:
        """
        模拟订单簿

        Args:
            market_id: 市场 ID
            levels: 订单簿深度

        Returns:
            订单簿数据
        """
        # 找到市场
        market = None
        for m in self.markets:
            if m['market_id'] == market_id:
                market = m
                break

        if market is None:
            return {}

        mid_price = market['price_yes']
        spread = 0.02  # 2% 买卖价差

        # 生成买方报价
        bids = []
        for i in range(levels):
            price = mid_price - spread / 2 - i * 0.005
            quantity = np.random.uniform(100, 1000)
            bids.append({
                'price': max(price, 0.01),
                'quantity': quantity
            })

        # 生成卖方报价
        asks = []
        for i in range(levels):
            price = mid_price + spread / 2 + i * 0.005
            quantity = np.random.uniform(100, 1000)
            asks.append({
                'price': min(price, 0.99),
                'quantity': quantity
            })

        return {
            'market_id': market_id,
            'mid_price': mid_price,
            'bids': bids,
            'asks': asks,
            'spread': spread,
            'timestamp': datetime.now().isoformat()
        }

    def export_data(self, filepath: str) -> None:
        """
        导出市场数据到 CSV

        Args:
            filepath: 保存路径
        """
        df = pd.DataFrame(self.markets)
        df.to_csv(filepath, index=False)
        logger.info(f"市场数据已导出到 {filepath}")


def generate_test_scenario(scenario_type: str = "arbitrage") -> Dict[str, Any]:
    """
    生成测试场景

    Args:
        scenario_type: 场景类型 ('arbitrage', 'no_arbitrage', 'volatile')

    Returns:
        测试场景字典
    """
    simulator = MarketSimulator()

    if scenario_type == "arbitrage":
        # 高效套利场景：有明显的套利机会
        np.random.seed(42)
        markets = []
        for group_id in range(3):
            # 组内价格差异大，创造套利机会
            for i in range(2):
                price = np.random.uniform(0.3, 0.7)
                # YES 价格
                markets.append({
                    'market_id': f'group_{group_id}_yes_{i}',
                    'group_id': group_id,
                    'price_yes': price + np.random.uniform(0, 0.1),
                    'price_no': 1 - (price + np.random.uniform(0, 0.1)),
                    'depth': 10000
                })
                # NO 价格
                markets.append({
                    'market_id': f'group_{group_id}_no_{i}',
                    'group_id': group_id,
                    'price_yes': 1 - price + np.random.uniform(0, 0.1),
                    'price_no': price - np.random.uniform(0, 0.1),
                    'depth': 10000
                })

    elif scenario_type == "no_arbitrage":
        # 无套利场景：价格接近有效
        np.random.seed(123)
        markets = []
        for group_id in range(3):
            true_prob = np.random.uniform(0.3, 0.7)
            for i in range(2):
                market_price = true_prob + np.random.uniform(-0.02, 0.02)
                markets.append({
                    'market_id': f'group_{group_id}_market_{i}',
                    'group_id': group_id,
                    'price_yes': np.clip(market_price, 0.05, 0.95),
                    'price_no': 1 - np.clip(market_price, 0.05, 0.95),
                    'depth': 10000
                })

    elif scenario_type == "volatile":
        # 高波动场景
        np.random.seed(456)
        markets = []
        for group_id in range(5):
            true_prob = np.random.uniform(0.2, 0.8)
            for i in range(3):
                market_price = true_prob + np.random.uniform(-0.2, 0.2)
                markets.append({
                    'market_id': f'group_{group_id}_market_{i}',
                    'group_id': group_id,
                    'price_yes': np.clip(market_price, 0.05, 0.95),
                    'price_no': 1 - np.clip(market_price, 0.05, 0.95),
                    'depth': np.random.uniform(1000, 20000),
                    'volatility': np.random.uniform(0.05, 0.15)
                })

    return {
        'scenario_type': scenario_type,
        'markets': markets,
        'num_markets': len(markets),
        'num_groups': len(set(m['group_id'] for m in markets))
    }


if __name__ == "__main__":
    # 测试市场模拟器
    print("=== 测试市场模拟器 ===")

    # 创建模拟器
    simulator = MarketSimulator()

    # 生成市场
    markets = simulator.generate_markets(num_markets=20, num_related_groups=5)
    print(f"生成了 {len(markets)} 个市场")

    # 查找套利机会
    opportunities = simulator.find_arbitrage_opportunities(min_profit_rate=0.005)
    print(f"\n发现 {len(opportunities)} 个套利机会:")

    for opp in opportunities[:3]:
        print(f"  事件 {opp['group_id']}: 利润率={opp['profit_rate']*100:.2f}%, "
              f"最大交易=${opp['max_trade']:.2f}")

    # 测试不同场景
    print("\n=== 测试不同场景 ===")

    for scenario in ['arbitrage', 'no_arbitrage', 'volatile']:
        scenario_data = generate_test_scenario(scenario)
        print(f"\n场景: {scenario}")
        print(f"  市场数: {scenario_data['num_markets']}")
        print(f"  组数: {scenario_data['num_groups']}")
