# FortyTwo Token Monitor Telegram Bot

这是一个用于监控FortyTwo代币数量的Telegram机器人，可以通过发送命令来查询多个地址的MON代币余额和最近交易信息。

## 功能特性

- 🔍 查询多个地址的MON代币余额
- 📊 显示最近的交易记录
- 🔗 提供区块浏览器链接
- 👤 支持用户自定义监控地址列表
- ⚡ 实时查询，无需等待

## 部署步骤

### 1. 创建Telegram机器人

1. 在Telegram中搜索 `@BotFather`
2. 发送 `/newbot` 命令
3. 按照提示设置机器人名称和用户名
4. 保存获得的Bot Token

### 2. 服务器部署

```bash
# 克隆或下载代码到服务器
cd /path/to/your/project

# 设置环境变量
export TELEGRAM_BOT_TOKEN="your_bot_token_here"

# 运行启动脚本
python run_telegram_bot.py
```

### 3. 使用systemd服务（推荐）

创建服务文件 `/etc/systemd/system/fortytwo-bot.service`：

```ini
[Unit]
Description=FortyTwo Token Monitor Telegram Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/your/project
Environment=TELEGRAM_BOT_TOKEN=your_bot_token_here
ExecStart=/path/to/your/project/.venv/bin/python fortytwo_telegram_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable fortytwo-bot
sudo systemctl start fortytwo-bot
sudo systemctl status fortytwo-bot
```

## 使用方法

### 基本命令

- `/start` - 启动机器人，显示欢迎信息
- `/help` - 显示帮助信息
- `/check` - 检查所有默认地址的代币余额
- `/check_address <address>` - 检查指定地址的代币余额
- `/add_address <address>` - 添加地址到你的监控列表
- `/list_addresses` - 查看你的监控地址列表

### 使用示例

1. **启动机器人**
   ```
   /start
   ```

2. **检查所有默认地址**
   ```
   /check
   ```

3. **检查特定地址**
   ```
   /check_address 0x2B0257e1302F2c3e0677956d0EA3F28d84919884
   ```

4. **添加自定义地址**
   ```
   /add_address 0x1234567890abcdef1234567890abcdef12345678
   ```

5. **查看监控列表**
   ```
   /list_addresses
   ```

## 默认监控地址

机器人默认监控以下地址：

- 0x2B0257e1302F2c3e0677956d0EA3F28d84919884
- 0x438b28b1f4AeC1A38aCF577Ad63921a21AB1BC4F
- 0x5a015B23eD0851eE17720F11B788a6C0bE918AF6
- 0xbA511e574aA768245C26602a9FD82608Daa840cc
- 0x5DBB65DE18295a3920c556893A11C11F1Da9C721
- 0xa2106b7DAF74b7a649115e3C02Cce1C6CDcF27C7
- 0x4054D631D426B87Eb9a1bf666832227f469e06AF

## 输出示例

```
🪙 FortyTwo Token Monitor
Time: 2024-01-15 14:30:25

Address: 0x2B0257e1302F2c3e0677956d0EA3F28d84919884
MON Balance: 1.234567 MON

Recent Transactions:
1. 2024-01-15 14:25:30
   0x1234567890...
2. 2024-01-15 14:20:15
   0xabcdef1234...

View on Explorer
```

## 故障排除

### 常见问题

1. **机器人无响应**
   - 检查Bot Token是否正确
   - 确认网络连接正常
   - 查看日志文件

2. **无法连接到Monad网络**
   - 检查RPC节点是否可用
   - 确认网络连接

3. **查询结果为空**
   - 确认地址格式正确
   - 检查地址是否有交易记录

### 日志查看

```bash
# 查看服务状态
sudo systemctl status fortytwo-bot

# 查看实时日志
sudo journalctl -u fortytwo-bot -f

# 查看错误日志
sudo journalctl -u fortytwo-bot -p err
```

## 配置文件

用户配置保存在 `user_configs.json` 文件中，包含每个用户的监控地址列表。

## 依赖项

- Python 3.7+
- web3
- requests
- python-telegram-bot

## 许可证

MIT License 