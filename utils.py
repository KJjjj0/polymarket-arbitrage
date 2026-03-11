#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数 - Frank-Wolfe 套利算法
包含常用的辅助函数
"""

import numpy as np
import logging
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime
import json


def setup_logging(log_level: str = "INFO", verbose: bool = True) -> logging.Logger:
    """
    设置日志记录器

    Args:
        log_level: 日志级别
        verbose: 是否详细输出

    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger("polymarket-arb")
    logger.setLevel(getattr(logging, log_level.upper()))

    # 控制台输出
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO if not verbose else logging.DEBUG)

    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger


def calculate_expected_return(
    price_yes: float,
    price_no: float,
    bet_on_yes: bool,
    payout: float = 1.0
) -> float:
    """
    计算预期收益率

    Args:
        price_yes: YES 的价格
        price_no: NO 的价格
        bet_on_yes: 是否押注 YES
        payout: 到期支付金额（通常为 $1.00）

    Returns:
        预期收益率
    """
    # 检查价格合理性
    if price_yes <= 0 or price_no <= 0:
        raise ValueError("价格必须大于 0")

    if price_yes + price_no > payout + 0.01:
        logger = logging.getLogger("polymarket-arb")
        logger.warning(f"价格异常: YES={price_yes:.4f}, NO={price_no:.4f}, SUM={price_yes+price_no:.4f}")

    # 计算隐含概率
    prob_yes = price_yes / (price_yes + price_no)
    prob_no = price_no / (price_yes + price_no)

    if bet_on_yes:
        # 押注 YES：如果发生，收益 = (payout / price_yes) - 1
        win_return = (payout / price_yes) - 1
        loss_return = -1  # 输了损失全部
        expected_return = prob_yes * win_return + prob_no * loss_return
    else:
        # 押注 NO：如果失败，收益 = (payout / price_no) - 1
        win_return = (payout / price_no) - 1
        loss_return = -1
        expected_return = prob_no * win_return + prob_yes * loss_return

    return expected_return


def calculate_arbitrage_opportunity(
    markets: List[Dict[str, Any]],
    market_id: str,
    fee_rate: float = 0.01
) -> Optional[Dict[str, Any]]:
    """
    计算套利机会

    Args:
        markets: 市场列表，每个市场包含价格和深度信息
        market_id: 要检查的市场 ID
        fee_rate: 交易手续费率

    Returns:
        套利机会信息（如果有），否则 None
    """
    logger = logging.getLogger("polymarket-arb")

    # 筛选相关市场
    related_markets = [m for m in markets if m['market_id'] == market_id]

    if len(related_markets) < 2:
        return None

    # 找到 YES 和 NO 的最佳价格
    best_yes_price = max([m['price_yes'] for m in related_markets if 'price_yes' in m])
    best_no_price = max([m['price_no'] for m in related_markets if 'price_no' in m])

    # 检查套利空间
    total_price = best_yes_price + best_no_price

    # 考虑手续费
    total_price_with_fee = total_price * (1 + fee_rate * 2)  # 买入卖出各一次

    if total_price_with_fee < 1.0:
        # 存在套利机会
        profit_per_share = 1.0 - total_price_with_fee
        profit_rate = profit_per_share / total_price_with_fee

        # 计算最大可交易金额（受限于市场深度）
        yes_market = min(related_markets, key=lambda m: m.get('depth_yes', 0))
        no_market = min(related_markets, key=lambda m: m.get('depth_no', 0))
        max_yes_trade = yes_market.get('depth_yes', 0)
        max_no_trade = no_market.get('depth_no', 0)
        max_trade = min(max_yes_trade, max_no_trade)

        opportunity = {
            'market_id': market_id,
            'best_yes_price': best_yes_price,
            'best_no_price': best_no_price,
            'total_price': total_price,
            'profit_per_share': profit_per_share,
            'profit_rate': profit_rate,
            'max_trade': max_trade,
            'timestamp': datetime.now().isoformat()
        }

        logger.info(f"发现套利机会: {market_id}, 利润率: {profit_rate*100:.2f}%")
        return opportunity

    return None


def normalize_probability_vector(p: np.ndarray) -> np.ndarray:
    """
    归一化概率向量

    Args:
        p: 概率向量

    Returns:
        归一化后的概率向量
    """
    p_normalized = p / np.sum(p)
    return p_normalized


def check_market_feasibility(
    current_position: np.ndarray,
    proposed_trade: np.ndarray,
    max_position_ratio: float = 0.3,
    total_capital: float = 10000
) -> bool:
    """
    检查交易是否可行

    Args:
        current_position: 当前持仓
        proposed_trade: 提议的交易
        max_position_ratio: 最大持仓比例
        total_capital: 总资金

    Returns:
        是否可行
    """
    # 计算新持仓
    new_position = current_position + proposed_trade

    # 检查资金限制
    total_exposure = np.sum(np.abs(new_position))
    if total_exposure > total_capital * max_position_ratio:
        return False

    # 检查单个市场持仓
    max_single_exposure = np.max(np.abs(new_position))
    if max_single_exposure > total_capital * 0.2:  # 单个市场最大 20%
        return False

    return True


def calculate_sharpe_ratio(
    returns: np.ndarray,
    risk_free_rate: float = 0.0
) -> float:
    """
    计算 Sharpe 比率

    Args:
        returns: 收益率序列
        risk_free_rate: 无风险利率

    Returns:
        Sharpe 比率
    """
    excess_returns = returns - risk_free_rate
    if np.std(excess_returns) == 0:
        return 0.0

    sharpe = np.mean(excess_returns) / np.std(excess_returns)
    return sharpe


def calculate_max_drawdown(
    cumulative_returns: np.ndarray
) -> float:
    """
    计算最大回撤

    Args:
        cumulative_returns: 累计收益率序列

    Returns:
        最大回撤
    """
    peak = np.maximum.accumulate(cumulative_returns)
    drawdown = (peak - cumulative_returns) / peak
    max_drawdown = np.max(drawdown)
    return max_drawdown


def save_results(
    results: Dict[str, Any],
    filepath: str
) -> None:
    """
    保存结果到 JSON 文件

    Args:
        results: 结果字典
        filepath: 保存路径
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


def load_results(filepath: str) -> Dict[str, Any]:
    """
    从 JSON 文件加载结果

    Args:
        filepath: 文件路径

    Returns:
        结果字典
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        results = json.load(f)
    return results


def print_trade_summary(
    trade: Dict[str, Any],
    logger: Optional[logging.Logger] = None
) -> None:
    """
    打印交易摘要

    Args:
        trade: 交易信息
        logger: 日志记录器
    """
    if logger is None:
        logger = logging.getLogger("polymarket-arb")

    logger.info("=" * 60)
    logger.info("交易摘要")
    logger.info("=" * 60)
    logger.info(f"市场 ID: {trade.get('market_id', 'N/A')}")
    logger.info(f"交易类型: {trade.get('trade_type', 'N/A')}")
    logger.info(f"交易金额: ${trade.get('amount', 0):.2f}")
    logger.info(f"预期利润: ${trade.get('expected_profit', 0):.2f}")
    logger.info(f"利润率: {trade.get('profit_rate', 0) * 100:.2f}%")
    logger.info(f"时间戳: {trade.get('timestamp', 'N/A')}")
    logger.info("=" * 60)


# 初始化全局日志记录器
logger = setup_logging()


if __name__ == "__main__":
    # 测试工具函数
    print("=== 测试工具函数 ===")

    # 测试预期收益计算
    expected_return = calculate_expected_return(0.52, 0.47, bet_on_yes=True)
    print(f"预期收益率（押 YES）: {expected_return*100:.2f}%")

    expected_return = calculate_expected_return(0.52, 0.47, bet_on_yes=False)
    print(f"预期收益率（押 NO）: {expected_return*100:.2f}%")

    # 测试套利机会计算
    markets = [
        {
            'market_id': 'trump-wins',
            'price_yes': 0.52,
            'price_no': 0.47,
            'depth_yes': 5000,
            'depth_no': 5000
        },
        {
            'market_id': 'trump-wins',
            'price_yes': 0.56,
            'price_no': 0.43,
            'depth_yes': 3000,
            'depth_no': 3000
        }
    ]

    opportunity = calculate_arbitrage_opportunity(markets, 'trump-wins')
    if opportunity:
        print(f"\n套利机会发现:")
        print(f"  YES 最佳价格: ${opportunity['best_yes_price']:.4f}")
        print(f"  NO 最佳价格: ${opportunity['best_no_price']:.4f}")
        print(f"  利润率: {opportunity['profit_rate']*100:.2f}%")
        print(f"  最大可交易: ${opportunity['max_trade']:.2f}")
