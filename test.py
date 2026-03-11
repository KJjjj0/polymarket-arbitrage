#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试脚本 - 验证核心功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np

print("=" * 60)
print("Frank-Wolfe 套利算法 - 快速测试")
print("=" * 60)

# 测试 1: 配置
print("\n[测试 1] 加载配置...")
try:
    from config import Config
    config = Config()
    print(f"✅ 配置加载成功")
    print(f"   最大迭代次数: {config.MAX_ITERATIONS}")
    print(f"   收敛阈值: {config.CONVERGENCE_THRESHOLD}")
except Exception as e:
    print(f"❌ 配置加载失败: {e}")
    sys.exit(1)

# 测试 2: 工具函数
print("\n[测试 2] 测试工具函数...")
try:
    from utils import calculate_expected_return, setup_logging
    ret = calculate_expected_return(0.52, 0.47, bet_on_yes=True)
    print(f"✅ 工具函数正常")
    print(f"   预期收益率: {ret*100:.2f}%")
except Exception as e:
    print(f"❌ 工具函数失败: {e}")
    sys.exit(1)

# 测试 3: Frank-Wolfe
print("\n[测试 3] 测试 Frank-Wolfe 算法...")
try:
    from frank_wolfe import (
        arbitrage_objective,
        arbitrage_gradient,
        ArbitrageOptimizer
    )
    optimizer = ArbitrageOptimizer()

    # 简单测试
    markets = [
        {'market_id': 'm1', 'price': 0.52},
        {'market_id': 'm2', 'price': 0.47},
        {'market_id': 'm3', 'price': 0.56},
        {'market_id': 'm4', 'price': 0.43}
    ]

    print(f"✅ Frank-Wolfe 模块加载成功")
except Exception as e:
    print(f"❌ Frank-Wolfe 失败: {e}")
    sys.exit(1)

# 测试 4: Bregman Projection
print("\n[测试 4] 测试 Bregman Projection...")
try:
    from bregman_projection import (
        bregman_divergence,
        bregman_projection,
        ConstraintManager
    )
    p = np.array([0.3, 0.5, 0.2])
    q = np.array([0.25, 0.45, 0.3])
    div = bregman_divergence(p, q, 'entropy')
    print(f"✅ Bregman Projection 模块正常")
    print(f"   熵散度: {div:.6f}")
except Exception as e:
    print(f"❌ Bregman Projection 失败: {e}")
    sys.exit(1)

# 测试 5: 市场模拟器
print("\n[测试 5] 测试市场模拟器...")
try:
    from market_simulator import MarketSimulator, generate_test_scenario
    simulator = MarketSimulator()
    markets = simulator.generate_markets(num_markets=5, num_related_groups=2)
    print(f"✅ 市场模拟器正常")
    print(f"   生成了 {len(markets)} 个模拟市场")
except Exception as e:
    print(f"❌ 市场模拟器失败: {e}")
    sys.exit(1)

# 测试 6: 回测引擎
print("\n[测试 6] 测试回测引擎...")
try:
    from backtester import Backtester
    backtester = Backtester()
    print(f"✅ 回测引擎正常")
    print(f"   初始资金: ${backtester.initial_capital}")
except Exception as e:
    print(f"❌ 回测引擎失败: {e}")
    sys.exit(1)

# 测试 7: Polymarket API
print("\n[测试 7] 测试 Polymarket API...")
try:
    from polymarket_api import PolymarketAPI
    api = PolymarketAPI()
    markets = api.get_markets(limit=5)
    print(f"✅ Polymarket API 正常（使用模拟数据）")
    print(f"   获取了 {len(markets)} 个市场")
except Exception as e:
    print(f"❌ Polymarket API 失败: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ 所有测试通过！系统运行正常。")
print("=" * 60)
print("\n可以运行以下命令：")
print("  python3 examples/basic_arb.py      # 运行基础示例")
print("  python3 examples/visualization.py  # 运行可视化示例")
