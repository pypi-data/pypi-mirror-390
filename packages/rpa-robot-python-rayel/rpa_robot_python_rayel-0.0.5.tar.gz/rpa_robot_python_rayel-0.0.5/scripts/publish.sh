#!/bin/bash

# 确保脚本在错误时退出
set -e

# 清理旧的构建文件
rm -rf dist/ build/ *.egg-info/

# 构建包
uv pip install build
python -m build

# 检查构建是否成功
if [ ! -d "dist" ]; then
    echo "构建失败：dist 目录不存在"
    exit 1
fi

# 上传到 PyPI
echo "正在上传到 PyPI..."
uv pip install twine
python -m twine upload dist/*

echo "发布完成！" 