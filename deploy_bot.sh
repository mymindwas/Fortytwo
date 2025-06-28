#!/bin/bash

# FortyTwo Token Monitor Telegram Bot 部署脚本

echo "🤖 FortyTwo Token Monitor Telegram Bot 部署脚本"
echo "================================================"

# 检查是否提供了Bot Token
if [ -z "$1" ]; then
    echo "❌ 请提供Telegram Bot Token"
    echo "使用方法: ./deploy_bot.sh YOUR_BOT_TOKEN"
    exit 1
fi

BOT_TOKEN=$1
PROJECT_DIR="/root/fortytwo-bot"

echo "📁 创建项目目录..."
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

echo "📥 复制项目文件..."
# 这里需要手动复制文件到服务器

echo "🐍 创建虚拟环境..."
python3 -m venv .venv

echo "📦 安装依赖..."
source .venv/bin/activate
pip install web3 requests python-telegram-bot

echo "🔧 配置服务文件..."
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

echo "🚀 启动服务..."
systemctl daemon-reload
systemctl enable fortytwo-bot
systemctl start fortytwo-bot

echo "✅ 部署完成！"
echo "📊 检查服务状态:"
systemctl status fortytwo-bot

echo ""
echo "📝 使用说明:"
echo "1. 在Telegram中搜索你的机器人"
echo "2. 发送 /start 开始使用"
echo "3. 使用 /help 查看所有命令"
echo ""
echo "🔍 查看日志: journalctl -u fortytwo-bot -f"
echo "🛑 停止服务: systemctl stop fortytwo-bot"
echo "🔄 重启服务: systemctl restart fortytwo-bot" 