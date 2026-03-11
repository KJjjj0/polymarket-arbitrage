# Frank-Wolfe 套利算法 - Polymarket 预测市场套利工具

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Ready-brightgreen)
![Languages](https://img.shields.io/badge/Languages-CN%20%7C%20EN-blue)

**基于 Frank-Wolfe 算法的预测市场套利策略实现**

[English](README_EN.md) | [中文](README.md) | [功能特性](#-功能特性) • [快速开始](#-快速开始) • [算法说明](#-算法说明) • [文档](#-文档)

</div>

---

## ⚠️ 重要声明

**本项目仅供学习和研究使用，不构成任何投资建议。**

- 🔒 **只读模式**：所有代码仅扫描市场，不执行任何真实交易
- 💰 **投资有风险**：预测市场交易存在风险，入市需谨慎
- 📖 **学习用途**：本项目仅用于学习量化交易和优化算法
- 🚫 **不提供投资建议**：请根据自身情况做出投资决策

---

## 📁 项目结构

```
polymarket-arb/
├── config.py                 # 配置文件
├── utils.py                  # 工具函数
├── frank_wolfe.py            # Frank-Wolfe 核心算法
├── bregman_projection.py    # Bregman 投影
├── market_simulator.py      # 市场模拟器
├── backtester.py            # 回测引擎
├── polymarket_api.py        # Polymarket API 接口（只读）
├── examples/
│   ├── basic_arb.py         # 基础示例
│   └── visualization.py    # 可视化示例
├── test.py                 # 测试脚本
├── README.md               # 本文件
├── LICENSE                # MIT 许可证
└── .gitignore             # Git 忽略文件
```

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- numpy
- scipy
- pandas
- matplotlib
- requests

### 安装依赖

```bash
# 使用 pip
pip install numpy scipy pandas matplotlib requests

# 或使用 requirements.txt（推荐）
pip install -r requirements.txt
```

### 运行测试

```bash
# 克隆仓库
git clone https://github.com/KJjjj0/polymarket-arbitrage.git
cd polymarket-arbitrage

# 运行测试
python3 test.py

# 运行基础示例
python3 examples/basic_arb.py

# 运行可视化示例
python3 examples/visualization.py
```

---

## ✨ 功能特性

### 核心算法

- ✅ **Frank-Wolfe 优化器** - 条件梯度法优化套利策略
- ✅ **Bregman Projection** - 处理复杂约束条件
- ✅ **Kelly Criterion** - 最优仓位管理
- ✅ **Monte Carlo 方法** - 风险评估和策略测试

### 工具模块

- ✅ **市场模拟器** - 生成测试数据，模拟市场行为
- ✅ **回测引擎** - 在历史数据上测试策略
- ✅ **Polymarket API** - 只读模式获取实时数据
- ✅ **可视化工具** - 结果可视化和分析

### 安全特性

- 🔒 **只读模式** - API 仅扫描，不下单
- 🧪 **测试数据** - 内置模拟器生成测试数据
- 📊 **风险控制** - 最大仓位、单市场限制
- 📝 **详细日志** - 记录所有操作

---

## 📖 算法说明

### Frank-Wolfe 算法

Frank-Wolfe 是一种约束优化算法，适用于凸优化问题。

**核心思想：**
1. 在当前点计算梯度
2. 通过线性规划找到最优搜索方向
3. 沿方向进行线搜索
4. 更新解并重复

**优势：**
- 无需投影操作（通过线性优化满足约束）
- 每次迭代计算量小
- 适用于大规模优化问题

### Bregman Projection

Bregman 投影用于确保解满足约束条件。

**支持散度类型：**
- **熵散度**（entropy）：适用于概率向量
- **平方散度**（norm2）：适用于一般优化问题

### 套利优化

**目标函数：**
```
minimize: -expected_return + risk_penalty
```

**约束条件：**
- 预算约束：`sum(|x|) * max_price <= capital`
- 单市场约束：`|x_i| <= max_single_position`
- 非负性约束（可选）

---

## 📊 使用示例

### 基础套利优化

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

### 扫描套利机会

```python
from polymarket_api import PolymarketAPI

# 创建 API 客户端
api = PolymarketAPI()

# 扫描套利机会
opportunities = api.scan_arbitrage_opportunities(
    min_profit_rate=0.01,  # 1% 最低利润率
    fee_rate=0.01         # 1% 手续费
)

# 显示机会
for opp in opportunities:
    print(f"事件: {opp['event_question']}")
    print(f"利润率: {opp['profit_rate']*100:.2f}%")
```

### 回测策略

```python
from backtester import Backtester
from market_simulator import generate_test_scenario

# 创建回测引擎
backtester = Backtester()

# 生成测试场景
scenario = generate_test_scenario("arbitrage")

# 运行回测
result = backtester.run_backtest(
    scenario,
    capital=10000,
    verbose=True
)

# 显示性能
print(f"总收益率: {result['performance']['total_return']*100:.2f}%")
print(f"Sharpe 比率: {result['performance']['sharpe_ratio']:.2f}")
```

---

## ⚙️ 配置

在 `config.py` 中修改参数：

```python
# 算法参数
MAX_ITERATIONS = 150              # 最大迭代次数
CONVERGENCE_THRESHOLD = 1e-6      # 收敛阈值
MIN_ITERATIONS = 50              # 最小迭代次数

# 套利参数
MIN_ARBITRAGE_PROFIT = 0.02      # 最小利润率 2%
TRADING_FEE = 0.01                # 手续费 1%
MAX_TRADE_AMOUNT = 10000          # 最大交易金额
MIN_TRADE_AMOUNT = 10             # 最小交易金额

# 风险控制
MAX_POSITION_RATIO = 0.3          # 最大持仓 30%
MAX_POSITIONS = 10                # 最大持仓数
MIN_CONFIDENCE = 0.7              # 最小置信度
```

---

## 📚 示例代码

### 运行所有示例

```bash
# 基础示例（5 个示例）
python3 examples/basic_arb.py

# 可视化示例（4 个可视化）
python3 examples/visualization.py
```

### 示例列表

1. **基础套利优化** - 演示 Frank-Wolfe 算法
2. **市场模拟** - 生成测试数据并检测套利机会
3. **回测策略** - 在不同场景下测试策略
4. **自定义策略** - 展示如何编写自定义策略
5. **算法底层** - 演示 Frank-Wolfe 算法内部工作原理

---

## 🔒 安全特性

### 1. 只读模式
- API 仅读取市场数据
- 不执行任何交易操作
- 安全的学习和研究环境

### 2. 测试数据
- 内置市场模拟器
- 无需真实 API 密钥
- 快速原型开发

### 3. 风险控制
- 最大仓位限制
- 单市场限制
- 多重验证机制

### 4. 详细日志
- 记录所有操作
- 便于调试和分析
- 审计追踪

---

## 📈 性能指标

### 算法性能

- **收敛速度**：通常 50-150 次迭代
- **计算复杂度**：O(n * k)，n=市场数，k=迭代次数
- **内存占用**：O(n)

### 回测性能

- **速度**：1000 次交易约 1 秒
- **准确性**：基于模拟数据验证
- **可扩展性**：支持大规模市场数据

---

## 📖 文档

### 完整文档
- [算法详细说明](docs/algorithm.md)
- [API 参考](docs/api.md)
- [配置说明](docs/config.md)
- [常见问题](docs/faq.md)

### 多语言文档
- [English Documentation](README_EN.md) - 英文完整文档
- [中文文档](README.md) - 当前（中文完整文档）
- [快速开始 (EN/CN)](QUICKSTART.md) - 中英文快速开始指南

### 贡献指南
- [贡献指南 (中文)](CONTRIBUTING.md) - 中文贡献指南
- [Contributing Guide (English)](CONTRIBUTING_EN.md) - 英文贡献指南

---

## 🤝 贡献

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- [Frank-Wolfe 算法](https://en.wikipedia.org/wiki/Frank%E2%80%93Wolfe_algorithm)
- [Kelly Criterion](https://en.wikipedia.org/wiki/Kelly_criterion)
- [Polymarket](https://polymarket.com/)

---

## 📮 联系方式

- **作者**: Polymarket Arbitrage Bot
- **仓库**: https://github.com/KJjjj0/polymarket-arbitrage
- **问题反馈**: [GitHub Issues](https://github.com/KJjjj0/polymarket-arbitrage/issues)

---

## ⚠️ 免责声明

**本项目与 Polymarket 无任何关联，不提供投资建议。**

- 本项目仅供学习和研究使用
- 预测市场交易存在风险
- 请根据自身情况做出投资决策
- 作者不对任何投资损失负责

---

## 🌐 其他语言文档

- [中文文档](README.md) - 当前（中文）
- [English Documentation](README_EN.md) - 英文文档

---

<div align="center">

**如果这个项目对你有帮助，请给个 ⭐️**

Made with ❤️ by Polymarket Arbitrage Bot

</div>
