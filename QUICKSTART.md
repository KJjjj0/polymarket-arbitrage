# Quick Start Guide / 快速开始指南

<div align="center">

**English / 中文**

[English](#english) | [中文](#中文)

</div>

---

## English / 英文

### Installation / 安装

```bash
# Clone the repository
git clone https://github.com/KJjjj0/polymarket-arbitrage.git
cd polymarket-arbitrage

# Install dependencies
pip install -r requirements.txt
```

### Run Examples / 运行示例

```bash
# Run tests
python3 test.py

# Run basic examples
python3 examples/basic_arb.py

# Run visualization examples
python3 examples/visualization.py
```

### Basic Usage / 基础使用

```python
from frank_wolfe import ArbitrageOptimizer

# Create optimizer
optimizer = ArbitrageOptimizer()

# Market data
markets = [
    {'market_id': 'trump_yes', 'price': 0.52, 'depth': 10000},
    {'market_id': 'trump_no', 'price': 0.47, 'depth': 10000},
]

# Run optimization
result = optimizer.optimize(markets, capital=10000)

print(f"Expected profit: ${result['expected_profit']:.2f}")
print(f"Profit rate: {result['profit_rate']*100:.2f}%")
```

---

## 中文 / 中文

### 安装

```bash
# 克隆仓库
git clone https://github.com/KJjjj0/polymarket-arbitrage.git
cd polymarket-arbitrage

# 安装依赖
pip install -r requirements.txt
```

### 运行示例

```bash
# 运行测试
python3 test.py

# 运行基础示例
python3 examples/basic_arb.py

# 运行可视化示例
python3 examples/visualization.py
```

### 基础使用

```python
from frank_wolfe import ArbitrageOptimizer

# 创建优化器
optimizer = ArbitrageOptimizer()

# 市场数据
markets = [
    {'market_id': 'trump_yes', 'price': 0.52, 'depth': 10000},
    {'market_id': 'trump_no', 'price': 0.47, 'depth': 10000},
]

# 运行优化
result = optimizer.optimize(markets, capital=10000)

print(f"预期利润: ${result['expected_profit']:.2f}")
print(f"利润率: {result['profit_rate']*100:.2f}%")
```

---

## Documentation / 文档

- [English README](README_EN.md) - 英文完整文档
- [Chinese README](README.md) - 中文完整文档
- [Contributing Guide (EN)](CONTRIBUTING_EN.md) - 英文贡献指南
- [Contributing Guide (CN)](CONTRIBUTING.md) - 中文贡献指南

---

## Support / 支持

- [GitHub Issues](https://github.com/KJjjj0/polymarket-arbitrage/issues)
- [GitHub Discussions](https://github.com/KJjjj0/polymarket-arbitrage/discussions)

---

<div align="center">

Made with ❤️ by Polymarket Arbitrage Bot

</div>
