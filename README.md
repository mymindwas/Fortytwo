# FortyTwo Token Monitor Telegram Bot

FortyTwo代币监控Telegram机器人，查询多个地址的MON和42T代币余额及交易记录。

## 功能特性

- 🔍 查询多个地址的MON代币余额
- 📊 显示最近的交易记录（支持BlockVision API）
- 🔗 提供区块浏览器链接
- 👤 支持用户自定义监控地址列表
- ⚡ 实时查询，无需等待
- 🎯 详细的交易信息（类型、状态、费用、代币变化）

## 高级功能

### BlockVision API 支持
机器人支持使用 [BlockVision API](https://docs.blockvision.org/reference/retrieve-monad-account-activity) 获取更详细的交易信息：

- ✅ 交易状态（成功/失败）
- 💰 交易费用
- 🪙 代币变化详情（接收/发送的代币）
- 📝 交易类型（Transfer、Swap、Deposit等）
- 🕐 精确时间戳

**可选配置：**
```bash
# 设置BlockVision API密钥（可选，免费用户有30次试用）
export BLOCKVISION_API_KEY="your_api_key_here"
```

**注意：** BlockVision API是付费服务，但提供30次免费试用。如果没有API密钥，机器人会自动使用备用方法。

## 部署方法

### 方法一：Screen手动部署（推荐开发调试）

```bash
# 1. 上传文件到VPS
cd /root/42bot

# 2. 安装依赖
apt update && apt install python3 python3-pip python3-venv screen

# 3. 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 4. 设置环境变量
export TELEGRAM_BOT_TOKEN="your_bot_token_here"

# 5. 创建screen会话
screen -S fortytwo-bot

# 6. 运行机器人
python3 fortytwo_telegram_bot.py

# 7. 按 Ctrl+A+D 退出screen（机器人继续运行）

# 常用命令：
screen -ls          # 查看所有会话
screen -r fortytwo-bot  # 重新连接
screen -S fortytwo-bot -X quit  # 停止机器人
```

### 方法二：自动部署脚本（推荐生产环境）

```bash
# 1. 上传文件到VPS
cd /root/42bot

# 2. 给脚本执行权限
chmod +x deploy_bot.sh

# 3. 运行部署脚本
./deploy_bot.sh YOUR_BOT_TOKEN

# 4. 选择运行方式（推荐选择2或4）
```

## 使用方法

### 基本命令
- `/start` - 启动机器人
- `/check` - 检查所有默认地址
- `/check_address <address>` - 检查指定地址
- `/add_address <address>` - 添加监控地址
- `/list_addresses` - 查看监控列表
- `/help` - 显示帮助

### 使用示例
```
/check
/check_address 0x2B0257e1302F2c3e0677956d0EA3F28d84919884
```

## 默认监控地址

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
42T Balance: 0.500000 42T

Recent Transactions:
1. 2024-01-15 14:25:30
   0x1234567890...

View on Explorer
```

## 技术信息

- **MON代币**: 原生代币
- **42T代币**: ERC20代币 (0x22A3d96424Df6f04d02477cB5ba571BBf615F47E)
- **RPC节点**: https://testnet-rpc.monad.xyz
- **区块浏览器**: https://testnet.monadexplorer.com

## 故障排除

### 常见问题
1. **机器人无响应** - 检查Bot Token和网络连接
2. **无法连接Monad网络** - 检查RPC节点可用性
3. **交易记录为空** - 地址可能无最近交易

### 日志查看
```bash
# Screen方式
screen -r fortytwo-bot

# 自动部署方式
tail -f bot.log
journalctl -u fortytwo-bot -f
```

## 依赖项

- Python 3.7+
- web3>=6.0.0
- requests>=2.28.0
- python-telegram-bot>=20.0 