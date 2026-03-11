# Frank-Wolfe 套利算法 - 安装说明

## 当前状态

✅ **代码已完成** - 所有 Python 代码都已写在 `/root/.openclaw/workspace/polymarket-arb/`

⚠️ **依赖安装中** - 正在通过 apt 安装系统包（python3-numpy, python3-matplotlib, python3-scipy）

## 位置

**项目路径：** `/root/.openclaw/workspace/polymarket-arb/`

**包含文件：**
- config.py - 配置文件
- utils.py - 工具函数
- frank_wolfe.py - Frank-Wolfe 核心算法
- bregman_projection.py - Bregman 投影
- market_simulator.py - 市场模拟器
- backtester.py - 回测引擎
- polymarket_api.py - Polymarket API（只读）
- __init__.py - 包初始化
- README.md - 使用文档
- install.sh - 安装脚本
- examples/
  - basic_arb.py - 基础示例
  - visualization.py - 可视化示例

## 运行方式

### 方式 1：在当前服务器运行（推荐）

```bash
cd /root/.openclaw/workspace/polymarket-arb

# 运行基础示例
python3 examples/basic_arb.py

# 运行可视化示例
python3 examples/visualization.py
```

### 方式 2：虚拟环境（如果系统包安装失败）

```bash
cd /root/.openclaw/workspace/polymarket-arb

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖（需要网络）
pip install numpy pandas matplotlib scipy requests

# 运行示例
python examples/basic_arb.py
```

### 方式 3：拷贝到本地

如果需要在你的电脑上运行：

1. **下载整个文件夹**
   - 路径：`/root/.openclaw/workspace/polymarket-arb/`
   - 可以使用 SCP 或 SFTP 下载

2. **在本地安装依赖**
   ```bash
   cd polymarket-arb
   pip install numpy pandas matplotlib scipy requests
   ```

3. **运行示例**
   ```bash
   python examples/basic_arb.py
   ```

## 测试

安装完成后，运行测试：

```bash
python3 config.py
```

应该看到：
```
=== Frank-Wolfe 套利算法配置 ===
最大迭代次数: 150
最小套利利润率: 2.0%
交易手续费率: 1.0%
最大交易金额: $10000
收敛阈值: 1e-06
```

## 常见问题

**Q: 代码在哪？**
A: `/root/.openclaw/workspace/polymarket-arb/`

**Q: 需要安装依赖吗？**
A: 是的，需要 numpy, pandas, matplotlib, scipy, requests

**Q: 可以在当前服务器运行吗？**
A: 可以，正在通过 apt 安装系统包

**Q: 需要拷贝到本地吗？**
A: 不一定，如果 apt 安装成功，可以直接在服务器上运行

## 下一步

等待系统包安装完成后：
1. 测试配置：`python3 config.py`
2. 运行示例：`python3 examples/basic_arb.py`
3. 查看结果和图表

---

**注意：** 当前服务器网络可能受限，如果 apt 安装失败，可以考虑使用本地 Python 环境或者拷贝到网络环境更好的电脑上运行。
