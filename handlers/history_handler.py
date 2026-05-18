"""
History Handler - Estilo AYO BOT VIP
"""

from datetime import datetime
from utils.analyzer import BacBoAnalyzer


class HistoryHandler:

    EMOJI = {"P": "🔵", "B": "🔴", "T": "🟠"}
    LABEL = {"P": "Player", "B": "Banker", "T": "Tie"}
    ALIAS = {"PLAYER": "P", "BANKER": "B", "TIE": "T"}

    def __init__(self, analyzer: BacBoAnalyzer, signal_handler=None):
        self.analyzer = analyzer
        self.signal_handler = signal_handler

    def register_result(self, raw: str) -> str:
        result = self.ALIAS.get(raw.upper(), raw.upper())

        if result not in ("P", "B", "T"):
            return (
                "❌ *Resultado inválido!*\n\n"
                "🔵 `/resultado P` — Player\n"
                "🔴 `/resultado B` — Banker\n"
                "🟠 `/resultado T` — Tie"
            )

        ok = self.analyzer.add_result(result)
        if not ok:
            return "❌ Erro ao registar resultado."

        # Feedback do sinal anterior
        if self.signal_handler:
            return self.signal_handler.get_resultado_feedback(result)

        total = len(self.analyzer.history)
        emoji = self.EMOJI[result]
        label = self.LABEL[result]
        now = datetime.now().strftime("%H:%M:%S")

        return (
            f"✅ *Resultado registado!*\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"{emoji} *{label}*  `{now}`\n\n"
            f"📊 Total de rodadas: *{total}*"
        )

    def get_history_text(self) -> str:
        h = list(self.analyzer.history)
        if not h:
            return (
                "📭 *Histórico vazio*\n\n"
                "Regista os resultados:\n"
                "🔵 `/resultado P`\n"
                "🔴 `/resultado B`\n"
                "🟠 `/resultado T`"
            )

        last20 = h[-20:]
        visual = " ".join(self.EMOJI.get(r, "⚫") for r in last20)

        rows = []
        for i, r in enumerate(reversed(last20), 1):
            e = self.EMOJI.get(r, "⚫")
            l = self.LABEL.get(r, r)
            rows.append(f"`{i:>2}.` {e} {l}")

        # Stats rápidas
        p = last20.count("P")
        b = last20.count("B")
        t = last20.count("T")

        return (
            f"📊 *Histórico — Bac Bo 🇧🇷*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"*Últimas {len(last20)} rodadas:*\n"
            f"{visual}\n\n"
            + "\n".join(rows) +
            f"\n\n"
            f"🔵 Player: *{p}*  🔴 Banker: *{b}*  🟠 Tie: *{t}*\n"
            f"📋 Total acumulado: *{len(h)}* rodadas"
        )

    def get_stats_text(self) -> str:
        stats = self.analyzer.get_full_stats()
        h = list(self.analyzer.history)
        freq = stats["frequency"]
        sk = stats["streak_result"]
        sl = stats["streak_length"]

        if not h:
            return "📭 *Sem dados suficientes.*\nRegista pelo menos 5 rodadas."

        def bar(pct):
            filled = round(pct / 10)
            return "🟩" * filled + "⬛" * (10 - filled)

        p_pct = freq.get("P", 0)
        b_pct = freq.get("B", 0)
        t_pct = freq.get("T", 0)

        streak_emoji = self.EMOJI.get(sk, "")
        streak_label = self.LABEL.get(sk, "")
        streak_str = (
            f"{streak_emoji} {streak_label} — *{sl}x* seguidos"
            if sk and sl > 1 else "Sem streak ativo"
        )

        # Placard do bot
        acc_txt = ""
        if self.signal_handler:
            g = self.signal_handler.greens
            r = self.signal_handler.reds
            acc = self.signal_handler.accuracy()
            acc_txt = (
                f"\n📊 *Placard do dia*\n"
                f"🟢 Greens: *{g}*  🔴 Reds: *{r}*\n"
                f"🎯 Acerto: *{acc}%*\n"
            )

        return (
            f"📈 *Estatísticas — Bac Bo 🇧🇷*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📋 *Total de rodadas:* {stats['total']}\n\n"
            f"*Distribuição:*\n"
            f"🔵 Player {bar(p_pct)} `{p_pct:.1f}%`\n"
            f"🔴 Banker {bar(b_pct)} `{b_pct:.1f}%`\n"
            f"🟠 Tie    {bar(t_pct)} `{t_pct:.1f}%`\n\n"
            f"🔥 *Streak atual:* {streak_str}\n\n"
            f"⏪ *Últimas 10:*\n"
            f"{'  '.join(self.EMOJI.get(r,'⚫') for r in h[-10:])}\n"
            + acc_txt +
            f"\n⚠️ _Use com responsabilidade._"
        )