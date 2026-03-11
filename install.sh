#!/bin/bash
# 安装依赖脚本
# 创建虚拟环境并安装所需的 Python 包

cd "$(dirname "$0")"

echo "创建虚拟环境..."
python3 -m venv venv

echo "激活虚拟环境..."
source venv/bin/activate

echo "安装依赖包..."
pip install --upgrade pip
pip install numpy pandas matplotlib scipy requests

echo "依赖安装完成！"
echo ""
echo "使用方法："
echo "  source venv/bin/activate  # 激活虚拟环境"
echo "  python examples/basic_arb.py  # 运行基础示例"
echo "  python examples/visualization.py  # 运行可视化示例"
