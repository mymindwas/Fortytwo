#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FortyTwo Token Telegram Bot - 通过Telegram机器人查询代币数量
"""

import os
import json
import requests
from web3 import Web3
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Constants
MONAD_RPC = "https://testnet-rpc.monad.xyz"
FORTYTWO_TOKEN_ADDRESS = "0x22A3d96424Df6f04d02477cB5ba571BBf615F47E"  # 42T代币合约地址

# BlockVision API配置
BLOCKVISION_API_KEY = os.getenv("BLOCKVISION_API_KEY", "")  # 可选：BlockVision API密钥

DEFAULT_ADDRESSES = [

]

USER_CONFIGS = {}
BALANCE_HISTORY = {}  # 存储余额历史记录

def load_user_configs():
    global USER_CONFIGS, BALANCE_HISTORY
    try:
        if os.path.exists("user_configs.json"):
            with open("user_configs.json", "r") as f:
                USER_CONFIGS = json.load(f)
        if os.path.exists("balance_history.json"):
            with open("balance_history.json", "r") as f:
                BALANCE_HISTORY = json.load(f)
    except Exception as e:
        USER_CONFIGS = {}
        BALANCE_HISTORY = {}

def save_user_configs():
    try:
        with open("user_configs.json", "w") as f:
            json.dump(USER_CONFIGS, f, indent=4)
        with open("balance_history.json", "w") as f:
            json.dump(BALANCE_HISTORY, f, indent=4)
    except Exception as e:
        print(f"Error saving configs: {e}")

def get_token_balance(w3, address, token_address=None):
    """获取代币余额"""
    try:
        if token_address is None:
            # 原生代币 (MON)
            balance = w3.eth.get_balance(address)
            return w3.from_wei(balance, 'ether')
        else:
            # ERC20代币 (42T)
            abi = [
                {
                    "constant": True,
                    "inputs": [{"name": "_owner", "type": "address"}],
                    "name": "balanceOf",
                    "outputs": [{"name": "balance", "type": "uint256"}],
                    "type": "function"
                }
            ]
            contract = w3.eth.contract(address=token_address, abi=abi)
            balance = contract.functions.balanceOf(address).call()
            return balance / (10 ** 18)  # 假设18位小数
    except Exception as e:
        return "Error"

def get_recent_transactions(address, limit=3):
    """获取最近的交易 - 使用BlockVision API"""
    try:
        # 使用BlockVision API获取账户活动
        url = "https://api.blockvision.org/v2/monad/account/activities"
        params = {
            "address": address,
            "limit": limit,
            "ascendingOrder": False  # 最新的记录在前
        }
        
        # 添加API密钥（如果需要）
        headers = {
            "Content-Type": "application/json"
        }
        
        # 如果有API密钥，添加到请求头
        if BLOCKVISION_API_KEY:
            headers["Authorization"] = f"Bearer {BLOCKVISION_API_KEY}"
        
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        if response.ok:
            data = response.json()
            
            if data.get("code") == 0 and data.get("result", {}).get("data"):
                transactions = []
                
                for activity in data["result"]["data"][:limit]:
                    # 从BlockVision API获取详细信息
                    tx_hash = activity.get("hash", "")
                    timestamp = activity.get("timestamp", 0)
                    tx_status = activity.get("txStatus", 0)
                    tx_name = activity.get("txName", "Transfer")
                    transaction_fee = activity.get("transactionFee", "0")
                    
                    # 转换时间戳（毫秒转秒）
                    if timestamp:
                        tx_time = datetime.fromtimestamp(timestamp / 1000)
                        time_str = tx_time.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        time_str = "Unknown"
                    
                    # 获取代币信息
                    token_info = ""
                    if activity.get("addTokens"):
                        for token in activity["addTokens"]:
                            symbol = token.get("symbol", "")
                            amount = token.get("amount", 0)
                            if symbol and amount:
                                token_info += f" +{amount} {symbol}"
                    
                    if activity.get("subTokens"):
                        for token in activity["subTokens"]:
                            symbol = token.get("symbol", "")
                            amount = token.get("amount", 0)
                            if symbol and amount:
                                token_info += f" -{amount} {symbol}"
                    
                    transactions.append({
                        "time": time_str,
                        "hash": tx_hash,
                        "type": tx_name,
                        "status": "✅" if tx_status == 1 else "❌",
                        "fee": transaction_fee,
                        "tokens": token_info.strip()
                    })
                
                return transactions
            else:
                print(f"BlockVision API error: {data.get('reason', 'Unknown error')}")
        
        # 如果BlockVision API失败，尝试备用方法
        print(f"BlockVision API failed, trying fallback methods...")
        
        # 备用方法1：尝试Monad Explorer API
        fallback_urls = [
            f"https://testnet.monadexplorer.com/api/address/{address}/transactions",
            f"https://testnet.monadexplorer.com/api/v1/address/{address}/transactions",
            f"https://testnet.monadexplorer.com/api/transactions?address={address}"
        ]
        
        for url in fallback_urls:
            try:
                response = requests.get(url, timeout=10)
                if response.ok:
                    data = response.json()
                    
                    transactions = []
                    tx_list = data.get("transactions", []) or data.get("data", []) or data.get("result", [])
                    
                    for tx in tx_list[:limit]:
                        timestamp = tx.get("timestamp") or tx.get("time") or tx.get("blockTime")
                        tx_hash = tx.get("hash") or tx.get("txHash")
                        
                        if timestamp and tx_hash:
                            tx_time = datetime.fromtimestamp(int(timestamp))
                            transactions.append({
                                "time": tx_time.strftime("%Y-%m-%d %H:%M:%S"),
                                "hash": tx_hash,
                                "type": "Transfer",
                                "status": "✅",
                                "fee": "0",
                                "tokens": ""
                            })
                    
                    if transactions:
                        return transactions
                        
            except Exception as e:
                continue
        
        # 备用方法2：直接从区块链获取
        try:
            w3 = Web3(Web3.HTTPProvider(MONAD_RPC))
            if w3.is_connected():
                nonce = w3.eth.get_transaction_count(address)
                if nonce > 0:
                    latest_block = w3.eth.block_number
                    for block_num in range(latest_block, max(0, latest_block - 100), -1):
                        try:
                            block = w3.eth.get_block(block_num, full_transactions=True)
                            for tx in block.transactions:
                                if tx['from'].lower() == address.lower() or (tx['to'] and tx['to'].lower() == address.lower()):
                                    tx_time = datetime.fromtimestamp(block.timestamp)
                                    return [{
                                        "time": tx_time.strftime("%Y-%m-%d %H:%M:%S"),
                                        "hash": tx['hash'].hex(),
                                        "type": "Transfer",
                                        "status": "✅",
                                        "fee": str(w3.from_wei(tx.get('gasPrice', 0) * tx.get('gas', 0), 'ether')),
                                        "tokens": ""
                                    }]
                        except:
                            continue
        except:
            pass
            
        return []
        
    except Exception as e:
        print(f"Error getting transactions: {e}")
        return []

def format_address_status(address, mon_balance, fortytwo_balance, recent_txs):
    """格式化地址状态信息"""
    explorer_link = f"https://testnet.monadexplorer.com/address/{address}?tab=Activity&portfolio=Token"
    
    # 获取余额变化
    mon_change, t42_change = get_balance_change(address, mon_balance, fortytwo_balance)
    
    msg = (
        f"<b>Address:</b> <code>{address}</code>\n"
        f"<b>MON Balance:</b> {mon_balance} MON"
    )
    
    # 添加MON余额变化指示器
    if mon_change is not None and mon_change != 0:
        change_symbol = "📈" if mon_change > 0 else "📉"
        change_text = f" (+{mon_change:.6f})" if mon_change > 0 else f" ({mon_change:.6f})"
        msg += f" {change_symbol}{change_text}"
    
    msg += f"\n<b>42T Balance:</b> {fortytwo_balance} 42T"
    
    # 添加42T余额变化指示器
    if t42_change is not None and t42_change != 0:
        change_symbol = "📈" if t42_change > 0 else "📉"
        change_text = f" (+{t42_change:.6f})" if t42_change > 0 else f" ({t42_change:.6f})"
        msg += f" {change_symbol}{change_text}"
    
    # 添加活跃状态指示器
    is_active = (mon_change is not None and mon_change != 0) or (t42_change is not None and t42_change != 0)
    if is_active:
        msg += "\n🟢 <b>ACTIVE - 余额有变化</b>"
    
    if recent_txs:
        msg += "\n\n<b>Recent Transactions:</b>\n"
        for i, tx in enumerate(recent_txs, 1):
            msg += f"{i}. {tx['time']}\n"
            msg += f"   <code>{tx['hash'][:10]}...</code>\n"
    else:
        msg += "\n\n<b>Recent Transactions:</b> No recent activity\n"
    
    msg += f'\n<a href="{explorer_link}">View on Explorer</a>'
    return msg

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""
    welcome_msg = (
        "🪙 FortyTwo Token Monitor Bot\n\n"
        "欢迎使用FortyTwo代币监控机器人！\n\n"
        "可用命令：\n"
        "/check - 检查默认地址列表的代币余额\n"
        "/check_address <code>address</code> - 检查指定地址的代币余额\n"
        "/add_address <code>address</code> - 添加地址到监控列表\n"
        "/list_addresses - 查看监控地址列表\n"
        "/help - 显示帮助信息\n\n"
        "使用 /check 开始查询代币余额！"
    )
    await update.message.reply_text(welcome_msg, parse_mode='HTML')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /help 命令"""
    help_msg = (
        "🪙 <b>FortyTwo Token Monitor Bot - 帮助</b>\n\n"
        "<b>命令说明：</b>\n"
        "• /check - 检查所有默认地址的代币余额\n"
        "• /check_address <code>address</code> - 检查单个地址\n"
        "• /add_address <code>address</code> - 添加监控地址\n"
        "• /list_addresses - 查看监控列表\n"
        "• /clear_history - 清除余额历史记录\n"
        "• /help - 显示此帮助信息\n\n"
        "<b>余额变化指示器：</b>\n"
        "📈 - 余额增加\n"
        "📉 - 余额减少\n"
        "🟢 ACTIVE - 地址有余额变化\n\n"
        "<b>示例：</b>\n"
        "/check_address <code>0x2B0257e1302F2c3e0677956d0EA3F28d84919884</code>"
    )
    await update.message.reply_text(help_msg, parse_mode='HTML')

async def check_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /check 命令 - 检查所有地址"""
    user_id = str(update.effective_user.id)
    addresses = USER_CONFIGS.get(user_id, {}).get("addresses", DEFAULT_ADDRESSES)
    
    if not addresses:
        await update.message.reply_text("❌ 没有配置监控地址，请使用 /add_address 添加地址")
        return
    
    status_msg = await update.message.reply_text("🔍 正在查询代币余额，请稍候...")
    
    try:
        w3 = Web3(Web3.HTTPProvider(MONAD_RPC))
        if not w3.is_connected():
            await status_msg.edit_text("❌ 无法连接到Monad网络")
            return
        
        messages = []
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        header_msg = f"🪙 <b>FortyTwo Token Monitor</b>\n<b>Time:</b> {current_time}\n"
        messages.append(header_msg)
        
        for i, address in enumerate(addresses, 1):
            mon_balance = get_token_balance(w3, address)
            fortytwo_balance = get_token_balance(w3, address, FORTYTWO_TOKEN_ADDRESS)
            recent_txs = get_recent_transactions(address)
            
            msg = format_address_status(address, mon_balance, fortytwo_balance, recent_txs)
            messages.append(msg)
            
            if i < len(addresses):
                messages.append("─" * 50)
        
        full_message = "\n\n".join(messages)
        
        if len(full_message) > 4096:
            chunks = [full_message[i:i+4096] for i in range(0, len(full_message), 4096)]
            for i, chunk in enumerate(chunks):
                if i == 0:
                    await status_msg.edit_text(chunk, parse_mode='HTML', disable_web_page_preview=True)
                else:
                    await update.message.reply_text(chunk, parse_mode='HTML', disable_web_page_preview=True)
        else:
            await status_msg.edit_text(full_message, parse_mode='HTML', disable_web_page_preview=True)
            
    except Exception as e:
        error_msg = f"❌ 查询过程中出现错误：\n<code>{str(e)}</code>"
        await status_msg.edit_text(error_msg, parse_mode='HTML')

async def check_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /check_address 命令"""
    if not context.args:
        await update.message.reply_text("❌ 请提供地址：\n/check_address <address>")
        return
    
    address = context.args[0]
    
    if not Web3.is_address(address):
        await update.message.reply_text("❌ 无效的地址格式")
        return
    
    status_msg = await update.message.reply_text(f"🔍 正在查询地址 {address} 的代币余额...")
    
    try:
        w3 = Web3(Web3.HTTPProvider(MONAD_RPC))
        if not w3.is_connected():
            await status_msg.edit_text("❌ 无法连接到Monad网络")
            return
        
        mon_balance = get_token_balance(w3, address)
        fortytwo_balance = get_token_balance(w3, address, FORTYTWO_TOKEN_ADDRESS)
        recent_txs = get_recent_transactions(address)
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header_msg = f"🪙 <b>FortyTwo Token Monitor</b>\n<b>Time:</b> {current_time}\n"
        
        full_message = header_msg + "\n" + format_address_status(address, mon_balance, fortytwo_balance, recent_txs)
        
        await status_msg.edit_text(full_message, parse_mode='HTML', disable_web_page_preview=True)
        
    except Exception as e:
        error_msg = f"❌ 查询过程中出现错误：\n<code>{str(e)}</code>"
        await status_msg.edit_text(error_msg, parse_mode='HTML')

async def add_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /add_address 命令"""
    if not context.args:
        await update.message.reply_text("❌ 请提供地址：\n/add_address <address>")
        return
    
    address = context.args[0]
    user_id = str(update.effective_user.id)
    
    if not Web3.is_address(address):
        await update.message.reply_text("❌ 无效的地址格式")
        return
    
    if user_id not in USER_CONFIGS:
        USER_CONFIGS[user_id] = {"addresses": []}
    
    if address in USER_CONFIGS[user_id]["addresses"]:
        await update.message.reply_text("⚠️ 该地址已在监控列表中")
        return
    
    USER_CONFIGS[user_id]["addresses"].append(address)
    save_user_configs()
    
    await update.message.reply_text(f"✅ 已添加地址到监控列表：\n<code>{address}</code>", parse_mode='HTML')

async def list_addresses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /list_addresses 命令"""
    user_id = str(update.effective_user.id)
    
    if user_id not in USER_CONFIGS or not USER_CONFIGS[user_id].get("addresses"):
        await update.message.reply_text("📝 你的监控列表为空，将使用默认地址列表")
        return
    
    addresses = USER_CONFIGS[user_id]["addresses"]
    msg = f"📝 <b>你的监控地址列表 ({len(addresses)} 个地址)：</b>\n\n"
    
    for i, address in enumerate(addresses, 1):
        msg += f"{i}. <code>{address}</code>\n"
    
    await update.message.reply_text(msg, parse_mode='HTML')

async def clear_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /clear_history 命令"""
    global BALANCE_HISTORY
    BALANCE_HISTORY = {}
    save_user_configs()
    await update.message.reply_text("✅ 已清除所有余额历史记录")

def get_balance_change(address, current_mon, current_42t):
    """获取余额变化"""
    if address not in BALANCE_HISTORY:
        BALANCE_HISTORY[address] = {
            "mon": current_mon,
            "42t": current_42t,
            "last_update": datetime.now().isoformat()
        }
        return None, None
    
    prev = BALANCE_HISTORY[address]
    mon_change = None
    t42_change = None
    
    if isinstance(current_mon, (int, float)) and isinstance(prev["mon"], (int, float)):
        mon_change = current_mon - prev["mon"]
    
    if isinstance(current_42t, (int, float)) and isinstance(prev["42t"], (int, float)):
        t42_change = current_42t - prev["42t"]
    
    # 更新历史记录
    BALANCE_HISTORY[address] = {
        "mon": current_mon,
        "42t": current_42t,
        "last_update": datetime.now().isoformat()
    }
    
    return mon_change, t42_change

def main():
    """主函数"""
    load_user_configs()
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ 请设置环境变量 TELEGRAM_BOT_TOKEN")
        print("例如：export TELEGRAM_BOT_TOKEN='your_bot_token_here'")
        return
    
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("check", check_all))
    application.add_handler(CommandHandler("check_address", check_address))
    application.add_handler(CommandHandler("add_address", add_address))
    application.add_handler(CommandHandler("list_addresses", list_addresses))
    application.add_handler(CommandHandler("clear_history", clear_history))
    
    print("🤖 FortyTwo Token Monitor Bot 正在启动...")
    print("使用 /start 开始使用机器人")
    
    application.run_polling()

if __name__ == "__main__":
    main() 