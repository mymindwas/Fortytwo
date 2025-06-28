# FortyTwo Token Monitor Telegram Bot

FortyTwo代币监控Telegram机器人，查询多个地址的MON和42T代币余额及交易记录。

## 功能特性

- 🔍 查询MON和42T代币余额
- 📊 显示最近交易记录和哈希
- 🔗 提供区块浏览器链接
- 👤 支持自定义监控地址列表
- ⚡ 实时查询，无需等待

## 创建Telegram机器人

### 1. 创建机器人
1. 在Telegram中搜索 `@BotFather`
2. 发送 `/newbot` 命令
3. 按照提示设置机器人名称和用户名
4. 保存获得的Bot Token

### 2. 获取Bot Token示例
```
BotFather: 请为你的机器人选择一个用户名
你: fortytwo_monitor_bot
BotFather: 好的！我已经创建了你的机器人。
使用这个token来访问HTTP API:
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

## 部署方法

### 方法一：Screen手动部署（推荐开发调试）

```bash
# 1. 克隆代码到VPS
git clone https://github.com/mymindwas/Fortytwo.git
cd Fortytwo

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
# 1. 克隆代码到VPS
git clone https://github.com/mymindwas/Fortytwo.git
cd Fortytwo

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

## 输出示例

```
![image](https://github.com/user-attachments/assets/1570530e-d90e-4ee8-9862-1a670387b958)

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

## 高级功能（可选）

### BlockVision API支持
机器人支持使用BlockVision API获取更详细的交易信息（可选功能）：

1. **获取API密钥**：
   - 访问 [BlockVision官网](https://blockvision.org)
   - 注册账号并申请API密钥

2. **配置API密钥**：
   ```bash
   export BLOCKVISION_API_KEY="your_api_key_here"
   ```

3. **功能特点**：
   - 详细的交易状态信息
   - 精确的交易费用
   - 代币变化详情
   - 交易类型分类

**注意**：BlockVision API为可选功能，不配置也能正常使用机器人。 
