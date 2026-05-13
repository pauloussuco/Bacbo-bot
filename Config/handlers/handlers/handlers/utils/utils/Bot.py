#!/usr/bin/env python3
"""
BacBo Signal Bot - Bot de análise estatística para Bac Bo
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes
)
from config.settings import BOT_TOKEN, ADMIN_IDS
from handlers.signal_handler import SignalHandler
from handlers.history_handler import HistoryHandler
from utils.analyzer import BacBoAnalyzer

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

analyzer = BacBoAnalyzer()
signal_handler = SignalHandler(analyzer)
history_handler = HistoryHandler(analyzer)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("🎯 Gerar Sinal", callback_data="signal")],
        [InlineKeyboardButton("📊 Histórico", callback_data="history"),
         InlineKeyboardButton("📈 Estatísticas", callback_data="stats")],
        [InlineKeyboardButton("➕ Registrar Resultado", callback_data="register"),
         InlineKeyboardButton("🔄 Resetar", callback_data="reset")],
        [InlineKeyboardButton("❓ Como usar", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = (
        f"♠️ *BacBo Signal Bot* ♥️\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Olá, *{user.first_name}*! 👋\n\n"
        f"Sou um bot de análise estatística para *Bac Bo*.\n\n"
        f"⚠️ _Jogue com responsabilidade._\n\n"
        f"Escolha uma opção abaixo:"
    )
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📖 *Como usar o BacBo Signal Bot*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "*Comandos:*\n"
        "• /start — Menu principal\n"
        "• /signal — Gerar sinal\n"
        "• /resultado [P/B/T] — Registrar resultado\n"
        "• /historico — Últimas 20 rodadas\n"
        "• /stats — Estatísti
