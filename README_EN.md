# Frank-Wolfe Arbitrage Algorithm - Polymarket Prediction Market Arbitrage Tool

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Ready-brightgreen)
![Languages](https://img.shields.io/badge/Languages-CN%20%7C%20EN-blue)

**Frank-Wolfe Arbitrage Algorithm - Polymarket Prediction Market Arbitrage Tool**

[English](README_EN.md) | [中文](README.md) | [Features](#-features) • [Quick Start](#-quick-start) • [Algorithm](#-algorithm) • [Documentation](#-documentation)

</div>

---

## ⚠️ Important Disclaimer

**This project is for learning and research purposes only and does not constitute any investment advice.**

- 🔒 **Read-Only Mode**: All code only scans markets, does not execute any real trades
- 💰 **Investment Risk**: Prediction market trading carries risks, enter with caution
- 📖 **Educational Purpose**: This project is only for learning quantitative trading and optimization algorithms
- 🚫 **No Investment Advice**: Please make investment decisions based on your own situation

---

## 📁 Project Structure

```
polymarket-arb/
├── config.py                 # Configuration file
├── utils.py                  # Utility functions
├── frank_wolfe.py            # Frank-Wolfe core algorithm
├── bregman_projection.py    # Bregman projection
├── market_simulator.py      # Market simulator
├── backtester.py            # Backtest engine
├── polymarket_api.py        # Polymarket API interface (read-only)
├── examples/
│   ├── basic_arb.py         # Basic examples
│   └── visualization.py    # Visualization examples
├── test.py                 # Test script
├── README.md               # Chinese documentation
├── README_EN.md            # English documentation
├── LICENSE                # MIT License
└── .gitignore             # Git ignore file
```

---

## 🚀 Quick Start

### Requirements

- Python 3.10+
- numpy
- scipy
- pandas
- matplotlib
- requests

### Installation

```bash
# Using pip
pip install numpy scipy pandas matplotlib requests

# Or using requirements.txt (recommended)
pip install -r requirements.txt
```

### Run Tests

```bash
# Clone repository
git clone https://github.com/KJjjj0/polymarket-arbitrage.git
cd polymarket-arbitrage

# Run tests
python3 test.py

# Run basic examples
python3 examples/basic_arb.py

# Run visualization examples
python3 examples/visualization.py
```

---

## ✨ Features

### Core Algorithms

- ✅ **Frank-Wolfe Optimizer** - Conditional gradient method for arbitrage strategy optimization
- ✅ **Bregman Projection** - Handle complex constraint conditions
- ✅ **Kelly Criterion** - Optimal position sizing
- ✅ **Monte Carlo Method** - Risk assessment and strategy testing

### Utility Modules

- ✅ **Market Simulator** - Generate test data, simulate market behavior
- ✅ **Backtest Engine** - Test strategies on historical data
- ✅ **Polymarket API** - Read-only mode for real-time data fetching
- ✅ **Visualization Tools** - Result visualization and analysis

### Security Features

- 🔒 **Read-Only Mode** - API only scans, no order execution
- 🧪 **Test Data** - Built-in simulator for test data generation
- 📊 **Risk Controls** - Maximum position, single market limits
- 📝 **Detailed Logging** - Record all operations

---

## 📖 Algorithm

### Frank-Wolfe Algorithm

Frank-Wolfe is a constraint optimization algorithm suitable for convex optimization problems.

**Core Idea:**
1. Compute gradient at current point
2. Find optimal search direction through linear programming
3. Perform line search along direction
4. Update solution and repeat

**Advantages:**
- No projection operations (constraints satisfied via linear optimization)
- Small computation per iteration
- Suitable for large-scale optimization problems

### Bregman Projection

Bregman projection ensures solution satisfies constraint conditions.

**Supported Divergence Types:**
- **Entropy Divergence**: Suitable for probability vectors
- **Norm-2 Divergence**: Suitable for general optimization problems

### Arbitrage Optimization

**Objective Function:**
```
minimize: -expected_return + risk_penalty
```

**Constraints:**
- Budget constraint: `sum(|x|) * max_price <= capital`
- Single market constraint: `|x_i| <= max_single_position`
- Non-negativity constraint (optional)

---

## 📊 Usage Examples

### Basic Arbitrage Optimization

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

### Scan Arbitrage Opportunities

```python
from polymarket_api import PolymarketAPI

# Create API client
api = PolymarketAPI()

# Scan arbitrage opportunities
opportunities = api.scan_arbitrage_opportunities(
    min_profit_rate=0.01,  # 1% minimum profit rate
    fee_rate=0.01         # 1% fee
)

# Display opportunities
for opp in opportunities:
    print(f"Event: {opp['event_question']}")
    print(f"Profit rate: {opp['profit_rate']*100:.2f}%")
```

### Backtest Strategy

```python
from backtester import Backtester
from market_simulator import generate_test_scenario

# Create backtest engine
backtester = Backtester()

# Generate test scenario
scenario = generate_test_scenario("arbitrage")

# Run backtest
result = backtester.run_backtest(
    scenario,
    capital=10000,
    verbose=True
)

# Display performance
print(f"Total return: {result['performance']['total_return']*100:.2f}%")
print(f"Sharpe ratio: {result['performance']['sharpe_ratio']:.2f}")
```

---

## ⚙️ Configuration

Modify parameters in `config.py`:

```python
# Algorithm parameters
MAX_ITERATIONS = 150              # Maximum iterations
CONVERGENCE_THRESHOLD = 1e-6      # Convergence threshold
MIN_ITERATIONS = 50              # Minimum iterations

# Arbitrage parameters
MIN_ARBITRAGE_PROFIT = 0.02      # Minimum profit rate 2%
TRADING_FEE = 0.01                # Fee 1%
MAX_TRADE_AMOUNT = 10000          # Maximum trade amount
MIN_TRADE_AMOUNT = 10             # Minimum trade amount

# Risk controls
MAX_POSITION_RATIO = 0.3          # Maximum position 30%
MAX_POSITIONS = 10                # Maximum number of positions
MIN_CONFIDENCE = 0.7              # Minimum confidence
```

---

## 📚 Example Code

### Run All Examples

```bash
# Basic examples (5 examples)
python3 examples/basic_arb.py

# Visualization examples (4 visualizations)
python3 examples/visualization.py
```

### Example List

1. **Basic Arbitrage Optimization** - Demonstrate Frank-Wolfe algorithm
2. **Market Simulation** - Generate test data and detect arbitrage opportunities
3. **Backtest Strategy** - Test strategies under different scenarios
4. **Custom Strategy** - Show how to write custom strategies
5. **Algorithm Internals** - Demonstrate internal workings of Frank-Wolfe algorithm

---

## 🔒 Security Features

### 1. Read-Only Mode
- API only reads market data
- No trade execution operations
- Safe learning and research environment

### 2. Test Data
- Built-in market simulator
- No real API key required
- Rapid prototyping

### 3. Risk Controls
- Maximum position limits
- Single market limits
- Multiple validation mechanisms

### 4. Detailed Logging
- Record all operations
- Facilitate debugging and analysis
- Audit trail

---

## 📈 Performance Metrics

### Algorithm Performance

- **Convergence Speed**: Typically 50-150 iterations
- **Computational Complexity**: O(n * k), n=number of markets, k=number of iterations
- **Memory Usage**: O(n)

### Backtest Performance

- **Speed**: ~1 second for 1000 trades
- **Accuracy**: Validated on simulated data
- **Scalability**: Supports large-scale market data

---

## 📖 Documentation

### Full Documentation
- [Algorithm Details](docs/algorithm.md)
- [API Reference](docs/api.md)
- [Configuration Guide](docs/config.md)
- [FAQ](docs/faq.md)

### Multi-Language Documentation
- [Chinese Documentation](README.md) - 完整中文文档
- [English Documentation](README_EN.md) - Current (Full English Documentation)
- [Quick Start (EN/CN)](QUICKSTART.md) - Bilingual Quick Start Guide

### Contributing Guide
- [Contributing Guide (English)](CONTRIBUTING_EN.md) - English contributing guide
- [贡献指南 (中文)](CONTRIBUTING.md) - Chinese contributing guide

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork this repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

- [Frank-Wolfe Algorithm](https://en.wikipedia.org/wiki/Frank%E2%80%93Wolfe_algorithm)
- [Kelly Criterion](https://en.wikipedia.org/wiki/Kelly_criterion)
- [Polymarket](https://polymarket.com/)

---

## 📮 Contact

- **Author**: Polymarket Arbitrage Bot
- **Repository**: https://github.com/KJjjj0/polymarket-arbitrage
- **Issues**: [GitHub Issues](https://github.com/KJjjj0/polymarket-arbitrage/issues)

---

## ⚠️ Disclaimer

**This project is not affiliated with Polymarket and does not provide investment advice.**

- This project is for learning and research purposes only
- Prediction market trading carries risks
- Please make investment decisions based on your own situation
- Author is not responsible for any investment losses

---

## 🌐 Documentation in Other Languages

- [中文文档](README.md) - Chinese Documentation
- [English Documentation](README_EN.md) - Current (English)

---

<div align="center">

**If this project helps you, please give it a ⭐️**

Made with ❤️ by Polymarket Arbitrage Bot

</div>
