#!/bin/bash

# FortyTwo Token Monitor Telegram Bot 部署脚本

echo "🤖 FortyTwo Token Monitor Telegram Bot 部署脚本"
echo "================================================"

# 检查是否提供了Bot Token
if [ -z "$1" ]; then
    echo "❌ 请提供Telegram Bot Token"
    echo "使用方法: ./deploy_bot.sh YOUR_BOT_TOKEN"
    echo ""
    echo "获取Bot Token步骤："
    echo "1. 在Telegram中搜索 @BotFather"
    echo "2. 发送 /newbot 命令"
    echo "3. 按照提示设置机器人名称和用户名"
    echo "4. 复制获得的Bot Token"
    exit 1
fi

BOT_TOKEN=$1
PROJECT_DIR="/root/42bot"

echo "📁 创建项目目录..."
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

echo "📥 检查项目文件..."
if [ ! -f "fortytwo_telegram_bot.py" ]; then
    echo "❌ 找不到 fortytwo_telegram_bot.py 文件"
    echo "请确保以下文件已上传到服务器："
    echo "- fortytwo_telegram_bot.py"
    echo "- requirements.txt"
    echo "- run_telegram_bot.py"
    exit 1
fi

echo "🐍 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "📦 安装Python3..."
    apt update
    apt install -y python3 python3-pip python3-venv
fi

echo "🐍 创建虚拟环境..."
python3 -m venv .venv

echo "📦 安装依赖..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败"
    exit 1
fi

echo "🔧 配置环境变量..."
echo "export TELEGRAM_BOT_TOKEN=\"$BOT_TOKEN\"" >> ~/.bashrc
export TELEGRAM_BOT_TOKEN="$BOT_TOKEN"

echo "🧪 测试机器人..."
echo "正在测试机器人连接..."
python3 -c "
import os
from telegram import Bot
try:
    bot = Bot(token='$BOT_TOKEN')
    me = bot.get_me()
    print(f'✅ 机器人连接成功: @{me.username}')
except Exception as e:
    print(f'❌ 机器人连接失败: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ 机器人测试失败，请检查Token是否正确"
    exit 1
fi

echo ""
echo "🚀 选择运行方式："
echo "1. 直接运行（前台运行，按Ctrl+C停止）"
echo "2. 后台运行（推荐，使用nohup）"
echo "3. 使用screen（推荐开发调试）"
echo "4. 使用systemd服务（推荐生产环境）"
echo ""
read -p "请选择运行方式 (1-4): " choice

case $choice in
    1)
        echo "🚀 直接运行机器人..."
        echo "按 Ctrl+C 停止机器人"
        python3 fortytwo_telegram_bot.py
        ;;
    2)
        echo "🚀 后台运行机器人..."
        nohup python3 fortytwo_telegram_bot.py > bot.log 2>&1 &
        echo "✅ 机器人已在后台启动"
        echo "📊 查看日志: tail -f bot.log"
        echo "🛑 停止机器人: pkill -f fortytwo_telegram_bot.py"
        ;;
    3)
        echo "🚀 使用screen运行机器人..."
        if ! command -v screen &> /dev/null; then
            echo "📦 安装screen..."
            apt install -y screen
        fi
        screen -dmS fortytwo-bot bash -c "cd $PROJECT_DIR && source .venv/bin/activate && python3 fortytwo_telegram_bot.py"
        echo "✅ 机器人已在screen中启动"
        echo "📊 查看screen会话: screen -ls"
        echo "🔗 连接screen: screen -r fortytwo-bot"
        echo "🛑 停止机器人: screen -S fortytwo-bot -X quit"
        ;;
    4)
        echo "🚀 配置systemd服务..."
        cat > /etc/systemd/system/fortytwo-bot.service << EOF
[Unit]
Description=FortyTwo Token Monitor Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_DIR
Environment=TELEGRAM_BOT_TOKEN=$BOT_TOKEN
ExecStart=$PROJECT_DIR/.venv/bin/python fortytwo_telegram_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
        
        systemctl daemon-reload
        systemctl enable fortytwo-bot
        systemctl start fortytwo-bot
        
        echo "✅ systemd服务已配置并启动"
        echo "📊 查看服务状态: systemctl status fortytwo-bot"
        echo "📋 查看日志: journalctl -u fortytwo-bot -f"
        echo "🛑 停止服务: systemctl stop fortytwo-bot"
        echo "🔄 重启服务: systemctl restart fortytwo-bot"
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "✅ 部署完成！"
echo ""
echo "📝 使用说明:"
echo "1. 在Telegram中搜索你的机器人"
echo "2. 发送 /start 开始使用"
echo "3. 使用 /help 查看所有命令"
echo "4. 使用 /check 查询代币余额"
echo ""
echo "🔍 故障排除:"
echo "- 查看README.md获取详细说明"
echo "- 检查日志文件查看错误信息"
echo "- 确认Bot Token正确且网络连接正常" 