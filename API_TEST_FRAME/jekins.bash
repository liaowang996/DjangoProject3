#!/bin/bash
set -e

VENV_DIR="/var/jenkins_home/python_venv"

# 找到真正的项目根目录（包含 common 和 test_runner 的目录）
PROJECT_ROOT=$(find "$WORKSPACE" -type d -name "common" | head -n 1 | xargs dirname)

if [ -z "$PROJECT_ROOT" ]; then
    echo "错误：未找到包含 common 目录的项目根目录！"
    exit 1
fi

echo "项目根目录: $PROJECT_ROOT"


REPORT_ROOT="$WORKSPACE/API_TEST_FRAME/report"

if [ -d "$REPORT_ROOT" ]; then
    # 按修改时间排序（最新在前），跳过前5个，删除其余
    find "$REPORT_ROOT" -mindepth 1 -maxdepth 1 -type d | sort -r | tail -n +6 | while read -r dir; do
        echo "删除旧报告: $dir"
        rm -rf "$dir"
    done
else
    echo "报告根目录不存在: $REPORT_ROOT"
fi


# 创建/激活虚拟环境
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

# 查找 requirements.txt（先在工作区根目录，再在项目根目录）
REQUIREMENTS=""
if [ -f "$WORKSPACE/requirements.txt" ]; then
    REQUIREMENTS="$WORKSPACE/requirements.txt"
elif [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    REQUIREMENTS="$PROJECT_ROOT/requirements.txt"
fi
# 在安装依赖后添加修复命令
sed -i 's/collections.Mapping/collections.abc.Mapping/g' "$VENV_DIR/lib/python3.11/site-packages/paramunittest.py"
# 安装依赖
if [ -n "$REQUIREMENTS" ]; then
    echo "使用依赖文件: $REQUIREMENTS"
    HASH_FILE="$VENV_DIR/requirements.hash"
    CURRENT_HASH=$(md5sum "$REQUIREMENTS" | awk '{print $1}')
    if [ ! -f "$HASH_FILE" ] || [ "$(cat "$HASH_FILE")" != "$CURRENT_HASH" ]; then
        pip install --no-cache-dir -U pip
        pip install --no-cache-dir -r "$REQUIREMENTS"
        echo "$CURRENT_HASH" > "$HASH_FILE"
    else
        echo "requirements.txt 未变化，跳过依赖安装"
    fi
else
    echo "警告：未找到 requirements.txt，可能导致依赖缺失"
fi

# 查找并执行脚本
RUN_SCRIPT=$(find "$PROJECT_ROOT" -type f -name "run_case.py" | head -n 1)
if [ -n "$RUN_SCRIPT" ]; then
    echo "找到脚本: $RUN_SCRIPT"

    # 关键：将项目根目录添加到 Python 路径
    export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

    echo "开始执行测试..."
    python3 "$RUN_SCRIPT"
else
    echo "错误：未找到 run_case.py 文件！"
    exit 1
fi

deactivate