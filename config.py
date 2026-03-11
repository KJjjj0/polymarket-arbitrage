#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件 - Frank-Wolfe 套利算法
包含所有可调参数和常量
"""

class Config:
    """配置类"""

    # ==================== 算法参数 ====================
    # Frank-Wolfe 最大迭代次数
    MAX_ITERATIONS = 150

    # Frank-Wolfe 最小迭代次数
    MIN_ITERATIONS = 50

    # 收敛阈值（解的变化小于此值时停止）
    CONVERGENCE_THRESHOLD = 1e-6

    # 初始步长
    INITIAL_STEP_SIZE = 1.0

    # 步长衰减率（如果目标函数不改善）
    STEP_DECAY = 0.9

    # ==================== 套利参数 ====================
    # 最小套利利润率（百分比）
    MIN_ARBITRAGE_PROFIT = 0.02  # 2%

    # 交易手续费率（百分比）
    TRADING_FEE = 0.01  # 1%

    # 最大交易金额（单次）
    MAX_TRADE_AMOUNT = 10000  # USDC

    # 最小交易金额（单次）
    MIN_TRADE_AMOUNT = 10  # USDC

    # 最大持仓比例（占资金）
    MAX_POSITION_RATIO = 0.3  # 30%

    # ==================== 市场参数 ====================
    # YES + NO 的理论价格（不变量）
    YES_NO_SUM = 1.0  # $1.00

    # 价格容差（考虑滑点）
    PRICE_TOLERANCE = 0.005  # 0.5%

    # 最小市场深度
    MIN_MARKET_DEPTH = 1000  # USDC

    # ==================== 风险控制 ====================
    # 最大同时持仓数
    MAX_POSITIONS = 10

    # 单个市场最大持仓比例
    MAX_MARKET_POSITION_RATIO = 0.2  # 20%

    # 置信度阈值（只执行高置信度交易）
    MIN_CONFIDENCE = 0.7  # 70%

    # ==================== API 参数 ====================
    # Polymarket API 基础 URL
    POLYMARKET_API_BASE = "https://api.polymarket.com"

    # API 请求超时（秒）
    API_TIMEOUT = 30

    # 数据刷新间隔（秒）
    DATA_REFRESH_INTERVAL = 5

    # ==================== 日志和调试 ====================
    # 日志级别：DEBUG, INFO, WARNING, ERROR
    LOG_LEVEL = "INFO"

    # 是否保存详细日志
    VERBOSE_LOGGING = True

    # 是否保存中间结果
    SAVE_INTERMEDIATE_RESULTS = True

    # ==================== 回测参数 ====================
    # 回测开始日期
    BACKTEST_START_DATE = "2025-01-01"

    # 回测结束日期
    BACKTEST_END_DATE = "2026-03-01"

    # 初始资金
    INITIAL_CAPITAL = 10000  # USDC

    # 交易滑点（模拟）
    SLIPPAGE = 0.001  # 0.1%

    # ==================== 可视化参数 ====================
    # 图表大小
    FIGURE_SIZE = (12, 8)

    # 字体大小
    FONT_SIZE = 10

    # 是否保存图表
    SAVE_PLOTS = True

    # 图表保存路径
    PLOT_SAVE_PATH = "./plots/"

    # ==================== Bregman Projection 参数 ====================
    # Bregman divergence 类型：'entropy', 'norm2'
    BREGMAN_TYPE = 'entropy'

    # Bregman Projection 最大迭代次数
    BREGMAN_MAX_ITER = 100

    # Bregman Projection 收敛阈值
    BREGMAN_CONVERGENCE_THRESHOLD = 1e-8

    # ==================== 优化器参数 ====================
    # 线性规划求解器：'scipy', 'custom'
    LINEAR_SOLVER = 'scipy'

    # 线性规划容差
    LINEAR_SOLVER_TOLERANCE = 1e-6


# 创建全局配置实例
config = Config()


def get_config():
    """获取配置实例"""
    return config


if __name__ == "__main__":
    # 打印当前配置
    print("=== Frank-Wolfe 套利算法配置 ===")
    print(f"最大迭代次数: {config.MAX_ITERATIONS}")
    print(f"最小套利利润率: {config.MIN_ARBITRAGE_PROFIT * 100}%")
    print(f"交易手续费率: {config.TRADING_FEE * 100}%")
    print(f"最大交易金额: ${config.MAX_TRADE_AMOUNT}")
    print(f"收敛阈值: {config.CONVERGENCE_THRESHOLD}")
