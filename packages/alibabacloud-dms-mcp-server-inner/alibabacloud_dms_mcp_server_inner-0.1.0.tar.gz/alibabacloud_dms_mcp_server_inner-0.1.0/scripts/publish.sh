#!/bin/bash
# 发布脚本 - 用于将包发布到 PyPI

set -e  # 遇到错误立即退出

echo "🚀 开始发布 alibabacloud-dms-mcp-server-inner 到 PyPI"

# 检查是否在项目根目录
if [ ! -f "pyproject.toml" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 检查是否安装了必要的工具
if ! command -v uv &> /dev/null; then
    echo "❌ 错误: 未找到 uv，请先安装 uv"
    exit 1
fi

if ! command -v twine &> /dev/null; then
    echo "📦 安装 twine..."
    uv pip install twine
fi

# 读取当前版本
VERSION=$(grep -E '^version = ' pyproject.toml | sed -E 's/version = "([^"]+)"/\1/')
echo "📌 当前版本: $VERSION"

# 确认发布
read -p "确认发布版本 $VERSION 到 PyPI? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 已取消发布"
    exit 1
fi

# 清理旧的构建文件
echo "🧹 清理旧的构建文件..."
rm -rf dist/ build/ *.egg-info src/*.egg-info

# 构建包
echo "🔨 构建包..."
uv build

# 检查构建结果
if [ ! -d "dist" ] || [ -z "$(ls -A dist)" ]; then
    echo "❌ 错误: 构建失败，dist 目录为空"
    exit 1
fi

echo "✅ 构建成功，生成的文件:"
ls -lh dist/

# 验证包
echo "🔍 验证包..."
twine check dist/*

# 选择发布目标
echo ""
echo "选择发布目标:"
echo "1) TestPyPI (测试)"
echo "2) PyPI (正式)"
read -p "请选择 (1/2): " choice

case $choice in
    1)
        echo "📤 发布到 TestPyPI..."
        twine upload --repository testpypi dist/*
        echo "✅ 已发布到 TestPyPI"
        echo "💡 测试安装: uvx --index-url https://test.pypi.org/simple/ alibabacloud-dms-mcp-server-inner@$VERSION"
        ;;
    2)
        echo "📤 发布到 PyPI..."
        twine upload dist/*
        echo "✅ 已发布到 PyPI"
        echo "💡 测试安装: uvx alibabacloud-dms-mcp-server-inner@$VERSION"
        ;;
    *)
        echo "❌ 无效选择，已取消发布"
        exit 1
        ;;
esac

echo ""
echo "🎉 发布完成！"
echo "📦 包名: alibabacloud-dms-mcp-server-inner"
echo "🏷️  版本: $VERSION"
echo "🌐 查看: https://pypi.org/project/alibabacloud-dms-mcp-server-inner/"


