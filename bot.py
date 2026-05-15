#!/usr/bin/env python3
"""
BacBo Signal Bot - Com notificações e análise automática
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
        f"✅ *Notificação automática ATIVA*\n"
        f"Após cada resultado registado receves o sinal automaticamente!\n\n"
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
        "• /stats — Estatísticas\n"
        "• /reset — Limpar histórico\n\n"
        "*Resultados válidos:*\n"
        "• `P` — Player\n"
        "• `B` — Banker\n"
        "• `T` — Tie (Empate)\n\n"
        "🔔 *Notificação automática:*\n"
        "_Após cada resultado o bot envia o sinal automaticamente!_\n\n"
        "⚠️ _Nenhum sistema garante lucro em jogos de azar._"
    )
    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown")
    else:
        await update.callback_query.edit_message_text(text, parse_mode="Markdown")


async def signal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("🔍 Analisando padrões...")
    signal_data = signal_handler.generate_signal()
    await msg.edit_text(signal_data, parse_mode="Markdown")


async def resultado_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "❌ Informe o resultado!\nExemplo: `/resultado P`",
            parse_mode="Markdown"
        )
        return

    resultado = context.args[0].upper()
    resposta = history_handler.register_result(resultado)
    await update.message.reply_text(resposta, parse_mode="Markdown")

    # ── ANÁLISE E NOTIFICAÇÃO AUTOMÁTICA ──
    stats = analyzer.get_full_stats()
    if stats["total"] >= 5:
        await update.message.reply_text("🔍 *Analisando próxima rodada...*", parse_mode="Markdown")
        signal_data = signal_handler.generate_signal()
        await update.message.reply_text(signal_data, parse_mode="Markdown")
    else:
        restantes = 5 - stats["total"]
        await update.message.reply_text(
            f"⏳ *Faltam {restantes} resultado(s)* para ativar a análise automática!",
            parse_mode="Markdown"
        )


async def historico_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = history_handler.get_history_text()
    await update.message.reply_text(text, parse_mode="Markdown")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = history_handler.get_stats_text()
    await update.message.reply_text(text, parse_mode="Markdown")


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✅ Confirmar Reset", callback_data="confirm_reset")],
        [InlineKeyboardButton("❌ Cancelar", callback_data="back_menu")],
    ]
    await update.message.reply_text(
        "⚠️ *Tem certeza?* Isso apagará todo o histórico.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "signal":
        signal_data = signal_handler.generate_signal()
        await query.edit_message_text(signal_data, parse_mode="Markdown")

    elif data == "history":
        text = history_handler.get_history_text()
        keyboard = [[InlineKeyboardButton("🔙 Voltar", callback_data="back_menu")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "stats":
        text = history_handler.get_stats_text()
        keyboard = [[InlineKeyboardButton("🔙 Voltar", callback_data="back_menu")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "register":
        keyboard = [
            [InlineKeyboardButton("👤 Player (P)", callback_data="res_P"),
             InlineKeyboardButton("🏦 Banker (B)", callback_data="res_B"),
             InlineKeyboardButton("🤝 Tie (T)", callback_data="res_T")],
            [InlineKeyboardButton("🔙 Voltar", callback_data="back_menu")],
        ]
        await query.edit_message_text(
            "🎲 *Qual foi o resultado desta rodada?*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif data.startswith("res_"):
        resultado = data.split("_")[1]
        resposta = history_handler.register_result(resultado)

        keyboard = [
            [InlineKeyboardButton("➕ Novo Resultado", callback_data="register")],
            [InlineKeyboardButton("🔙 Menu", callback_data="back_menu")],
        ]
        await query.edit_message_text(
            resposta, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )

        # ── ANÁLISE E NOTIFICAÇÃO AUTOMÁTICA VIA BOTÃO ──
        stats = analyzer.get_full_stats()
        if stats["total"] >= 5:
            signal_data = signal_handler.generate_signal()
            await query.message.reply_text(
                "🔔 *Sinal Automático:*\n" + signal_data,
                parse_mode="Markdown"
            )
        else:
            restantes = 5 - stats["total"]
            await query.message.reply_text(
                f"⏳ *Faltam {restantes} resultado(s)* para ativar a análise automática!",
                parse_mode="Markdown"
            )

    elif data == "reset":
        keyboard = [
            [InlineKeyboardButton("✅ Confirmar", callback_data="confirm_reset")],
            [InlineKeyboardButton("❌ Cancelar", callback_data="back_menu")],
        ]
        await query.edit_message_text(
            "⚠️ *Tem certeza?* Isso apagará todo o histórico.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif data == "confirm_reset":
        analyzer.reset()
        await query.edit_message_text(
            "✅ Histórico resetado!\nUse /start para começar.",
            parse_mode="Markdown"
        )

    elif data in ("cancel_reset", "back_menu"):
        keyboard = [
            [InlineKeyboardButton("🎯 Gerar Sinal", callback_data="signal")],
            [InlineKeyboardButton("📊 Histórico", callback_data="history"),
             InlineKeyboardButton("📈 Estatísticas", callback_data="stats")],
            [InlineKeyboardButton("➕ Registrar Resultado", callback_data="register"),
             InlineKeyboardButton("🔄 Resetar", callback_data="reset")],
            [InlineKeyboardButton("❓ Como usar", callback_data="help")],
        ]
        await query.edit_message_text(
            "♠️ *BacBo Signal Bot* ♥️\n━━━━━━━━━━━━━━━━\nEscolha uma opção:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif data == "help":
        await help_command(update, context)


def main():
    if not BOT_TOKEN or BOT_TOKEN == "SEU_TOKEN_AQUI":
        logger.error("❌ Configure o BOT_TOKEN em config/settings.py")
        return

    logger.info("🚀 Iniciando BacBo Signal Bot...")
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("signal", signal_command))
    app.add_handler(CommandHandler("resultado", resultado_command))
    app.add_handler(CommandHandler("historico", historico_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(CallbackQueryHandler(button_callback))

    logger.info("✅ Bot online! Aguardando mensagens...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()