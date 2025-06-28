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
MONAD_RPC = "https://rpc.testnet.monad.xyz"
DEFAULT_ADDRESSES = [
    "0x2B0257e1302F2c3e0677956d0EA3F28d84919884",
    "0x438b28b1f4AeC1A38aCF577Ad63921a21AB1BC4F",
    "0x5a015B23eD0851eE17720F11B788a6C0bE918AF6",
    "0xbA511e574aA768245C26602a9FD82608Daa840cc",
    "0x5DBB65DE18295a3920c556893A11C11F1Da9C721",
    "0xa2106b7DAF74b7a649115e3C02Cce1C6CDcF27C7",
    "0x4054D631D426B87Eb9a1bf666832227f469e06AF"
]

USER_CONFIGS = {}

def load_user_configs():
    global USER_CONFIGS
    try:
        if os.path.exists("user_configs.json"):
            with open("user_configs.json", "r") as f:
                USER_CONFIGS = json.load(f)
    except Exception as e:
        USER_CONFIGS = {}

def save_user_configs():
    try:
        with open("user_configs.json", "w") as f:
            json.dump(USER_CONFIGS, f, indent=4)
    except Exception as e:
        print(f"Error saving configs: {e}")

def get_token_balance(w3, address):
    """获取MON代币余额"""
    try:
        balance = w3.eth.get_balance(address)
        return w3.from_wei(balance, 'ether')
    except Exception as e:
        return "Error"

def get_recent_transactions(address, limit=3):
    """获取最近的交易"""
    try:
        url = f"https://testnet.monadexplorer.com/api/address/{address}/transactions"
        response = requests.get(url, timeout=10)
        
        if response.ok:
            data = response.json()
            transactions = []
            
            for tx in data.get("transactions", [])[:limit]:
                tx_time = datetime.fromtimestamp(tx.get("timestamp", 0))
                tx_hash = tx.get("hash", "")
                
                transactions.append({
                    "time": tx_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "hash": tx_hash
                })
            
            return transactions
        else:
            return []
            
    except Exception as e:
        return []

def format_address_status(address, mon_balance, recent_txs):
    """格式化地址状态信息"""
    explorer_link = f"https://testnet.monadexplorer.com/address/{address}?tab=Activity&portfolio=Token"
    
    msg = (
        f"<b>Address:</b> <code>{address}</code>\n"
        f"<b>MON Balance:</b> {mon_balance} MON\n"
    )
    
    if recent_txs:
        msg += "\n<b>Recent Transactions:</b>\n"
        for i, tx in enumerate(recent_txs, 1):
            msg += f"{i}. {tx['time']}\n"
            msg += f"   <code>{tx['hash'][:10]}...</code>\n"
    else:
        msg += "\n<b>Recent Transactions:</b> No recent activity\n"
    
    msg += f'\n<a href="{explorer_link}">View on Explorer</a>'
    return msg

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""
    welcome_msg = (
        "🪙 <b>FortyTwo Token Monitor Bot</b>\n\n"
        "欢迎使用FortyTwo代币监控机器人！\n\n"
        "<b>可用命令：</b>\n"
        "/check - 检查默认地址列表的代币余额\n"
        "/check_address <address> - 检查指定地址的代币余额\n"
        "/add_address <address> - 添加地址到监控列表\n"
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
        "• /check_address <address> - 检查单个地址\n"
        "• /add_address <address> - 添加监控地址\n"
        "• /list_addresses - 查看监控列表\n"
        "• /help - 显示此帮助信息\n\n"
        "<b>示例：</b>\n"
        "/check_address 0x2B0257e1302F2c3e0677956d0EA3F28d84919884"
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
            recent_txs = get_recent_transactions(address)
            
            msg = format_address_status(address, mon_balance, recent_txs)
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
        recent_txs = get_recent_transactions(address)
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header_msg = f"🪙 <b>FortyTwo Token Monitor</b>\n<b>Time:</b> {current_time}\n"
        
        full_message = header_msg + "\n" + format_address_status(address, mon_balance, recent_txs)
        
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
    
    print("🤖 FortyTwo Token Monitor Bot 正在启动...")
    print("使用 /start 开始使用机器人")
    
    application.run_polling()

if __name__ == "__main__":
    main() 