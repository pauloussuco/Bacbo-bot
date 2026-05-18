#!/usr/bin/env python3
"""
BacBo Signal Bot - Estilo AYO BOT VIP - Versão final corrigida
Bac Bo Ao Vivo Elephantbet
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes
)
from config.settings import BOT_TOKEN
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
history_handler = HistoryHandler(analyzer, signal_handler)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    g = signal_handler.greens
    r = signal_handler.reds
    acc = signal_handler.accuracy()

    keyboard = [
        [InlineKeyboardButton("🚀 Gerar Sinal", callback_data="signal")],
        [InlineKeyboardButton("📊 Histórico", callback_data="history"),
         InlineKeyboardButton("📈 Estatísticas", callback_data="stats")],
        [InlineKeyboardButton("➕ Registrar Resultado", callback_data="register"),
         InlineKeyboardButton("🔄 Resetar", callback_data="reset")],
        [InlineKeyboardButton("❓ Como usar", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = (
        f"🎲 *Bac Bo Ao Vivo* 🇧🇷\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Olá, *{user.first_name}*! 👋\n\n"
        f"🏦 *Mesa:* Bac Bo Ao Vivo 🇧🇷\n"
        f"🎰 *Casino:* Elephantbet\n\n"
        f"🔵 Player  •  🔴 Banker  •  🟠 Tie\n\n"
        f"📊 *Placard do dia:*\n"
        f"🟢 Greens: *{g}*  🔴 Reds: *{r}*\n"
        f"🎯 Acerto: *{acc}%*\n\n"
        f"✅ *Análise automática ATIVA*\n"
        f"Regista o resultado e recebe o sinal na hora!\n\n"
        f"⚠️ _Jogue com responsabilidade._"
    )
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📖 *Como usar — Bac Bo 🇧🇷*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "*Comandos:*\n"
        "• /start — Menu principal\n"
        "• /signal — Gerar sinal\n"
        "• /resultado [P/B/T] — Registrar resultado\n"
        "• /historico — Últimas 20 rodadas\n"
        "• /stats — Estatísticas e placard\n"
        "• /reset — Limpar histórico\n\n"
        "*Resultados:*\n"
        "• 🔵 `P` — Player (Jogador)\n"
        "• 🔴 `B` — Banker (Bancário)\n"
        "• 🟠 `T` — Tie (Empate)\n\n"
        "🔔 *Após cada resultado o sinal é enviado automaticamente!*\n\n"
        "🟠 *Empate = aposta protegida automaticamente!*\n\n"
        "⚠️ _Nenhum sistema garante lucro em jogos de azar._"
    )
    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown")
    else:
        await update.callback_query.edit_message_text(text, parse_mode="Markdown")


async def signal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("🔍 *Analisando mesa Bac Bo 🇧🇷...*", parse_mode="Markdown")
    signal_data = signal_handler.generate_signal()
    await msg.edit_text(signal_data, parse_mode="Markdown")


async def resultado_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "❌ Informe o resultado!\n\n"
            "🔵 `/resultado P` — Player\n"
            "🔴 `/resultado B` — Banker\n"
            "🟠 `/resultado T` — Tie",
            parse_mode="Markdown"
        )
        return

    resultado = context.args[0].upper()
    resposta = history_handler.register_result(resultado)
    await update.message.reply_text(resposta, parse_mode="Markdown")

    # ── SINAL AUTOMÁTICO ──
    stats = analyzer.get_full_stats()
    if stats["total"] >= 5:
        signal_data = signal_handler.generate_signal()
        await update.message.reply_text(signal_data, parse_mode="Markdown")
    else:
        restantes = 5 - stats["total"]
        await update.message.reply_text(
            f"⏳ *Faltam {restantes} resultado(s)* para análise automática!\n"
            f"📊 Rodadas: *{stats['total']}/5*",
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
        "⚠️ *Tem certeza?* Isso apagará todo o histórico e placard.",
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
            [InlineKeyboardButton("🔵 Player (P)", callback_data="res_P"),
             InlineKeyboardButton("🔴 Banker (B)", callback_data="res_B"),
             InlineKeyboardButton("🟠 Tie (T)",    callback_data="res_T")],
            [InlineKeyboardButton("🔙 Voltar", callback_data="back_menu")],
        ]
        await query.edit_message_text(
            "🎲 *Bac Bo 🇧🇷 — Qual foi o resultado?*\n\n"
            "🔵 Player  •  🔴 Banker  •  🟠 Tie",
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

        # ── SINAL AUTOMÁTICO ──
        stats = analyzer.get_full_stats()
        if stats["total"] >= 5:
            signal_data = signal_handler.generate_signal()
            await query.message.reply_text(signal_data, parse_mode="Markdown")
        else:
            restantes = 5 - stats["total"]
            await query.message.reply_text(
                f"⏳ *Faltam {restantes} resultado(s)* para análise automática!\n"
                f"📊 Rodadas: *{stats['total']}/5*",
                parse_mode="Markdown"
            )

    elif data == "reset":
        keyboard = [
            [InlineKeyboardButton("✅ Confirmar", callback_data="confirm_reset")],
            [InlineKeyboardButton("❌ Cancelar",  callback_data="back_menu")],
        ]
        await query.edit_message_text(
            "⚠️ *Tem certeza?* Isso apagará todo o histórico e placard.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif data == "confirm_reset":
        analyzer.reset()
        signal_handler.greens = 0
        signal_handler.reds = 0
        signal_handler.streak = 0
        signal_handler.last_signal = None
        await query.edit_message_text(
            "✅ *Histórico e placard resetados!*\n"
            "Use /start para começar.",
            parse_mode="Markdown"
        )

    elif data in ("cancel_reset", "back_menu"):
        g = signal_handler.greens
        r = signal_handler.reds
        acc = signal_handler.accuracy()
        keyboard = [
            [InlineKeyboardButton("🚀 Gerar Sinal", callback_data="signal")],
            [InlineKeyboardButton("📊 Histórico", callback_data="history"),
             InlineKeyboardButton("📈 Estatísticas", callback_data="stats")],
            [InlineKeyboardButton("➕ Registrar Resultado", callback_data="register"),
             InlineKeyboardButton("🔄 Resetar", callback_data="reset")],
            [InlineKeyboardButton("❓ Como usar", callback_data="help")],
        ]
        await query.edit_message_text(
            f"🎲 *Bac Bo Ao Vivo* 🇧🇷\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔵 Player  •  🔴 Banker  •  🟠 Tie\n\n"
            f"📊 Placard: 🟢 *{g}*  🔴 *{r}*  🎯 *{acc}%*\n\n"
            f"Escolha uma opção:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif data == "help":
        await help_command(update, context)


def main():
    if not BOT_TOKEN:
        logger.error("❌ Configure o BOT_TOKEN!")
        return

    logger.info("🚀 Iniciando USSUCO VOLVO BOT — Bac Bo 🇧🇷 Elephantbet...")
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",     start))
    app.add_handler(CommandHandler("help",      help_command))
    app.add_handler(CommandHandler("signal",    signal_command))
    app.add_handler(CommandHandler("resultado", resultado_command))
    app.add_handler(CommandHandler("historico", historico_command))
    app.add_handler(CommandHandler("stats",     stats_command))
    app.add_handler(CommandHandler("reset",     reset_command))
    app.add_handler(CallbackQueryHandler(button_callback))

    logger.info("✅ Bot online!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()