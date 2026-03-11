#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polymarket 套利算法包
基于 Frank-Wolfe 算法的预测市场套利工具
"""

__version__ = "1.0.0"
__author__ = "Polymarket Arbitrage Bot"

# 导出主要类和函数
from .config import Config, get_config
from .utils import (
    setup_logging,
    calculate_expected_return,
    calculate_arbitrage_opportunity,
    normalize_probability_vector,
    check_market_feasibility,
    calculate_sharpe_ratio,
    calculate_max_drawdown,
    save_results,
    load_results
)
from .frank_wolfe import (
    frank_wolfe,
    compute_step_size,
    arbitrage_objective,
    arbitrage_gradient,
    arbitrage_linear_optimization,
    ArbitrageOptimizer
)
from .bregman_projection import (
    bregman_divergence,
    bregman_gradient,
    bregman_hessian_inverse,
    bregman_projection,
    simplex_projection,
    l1_ball_projection,
    box_constraint_projection,
    ConstraintManager
)
from .market_simulator import (
    MarketSimulator,
    generate_test_scenario
)
from .backtester import (
    Backtester,
    walk_forward_backtest
)
from .polymarket_api import (
    PolymarketAPI,
    ArbitrageScanner
)

__all__ = [
    # 配置
    'Config',
    'get_config',
    
    # 工具函数
    'setup_logging',
    'calculate_expected_return',
    'calculate_arbitrage_opportunity',
    'normalize_probability_vector',
    'check_market_feasibility',
    'calculate_sharpe_ratio',
    'calculate_max_drawdown',
    'save_results',
    'load_results',
    
    # Frank-Wolfe
    'frank_wolfe',
    'compute_step_size',
    'arbitrage_objective',
    'arbitrage_gradient',
    'arbitrage_linear_optimization',
    'ArbitrageOptimizer',
    
    # Bregman Projection
    'bregman_divergence',
    'bregman_gradient',
    'bregman_hessian_inverse',
    'bregman_projection',
    'simplex_projection',
    'l1_ball_projection',
    'box_constraint_projection',
    'ConstraintManager',
    
    # 市场模拟器
    'MarketSimulator',
    'generate_test_scenario',
    
    # 回测引擎
    'Backtester',
    'walk_forward_backtest',
    
    # Polymarket API
    'PolymarketAPI',
    'ArbitrageScanner'
]
