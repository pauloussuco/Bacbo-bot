"""
Gerencia registro e exibição do histórico de rodadas.
"""

from datetime import datetime
from utils.analyzer import BacBoAnalyzer


class HistoryHandler:

    EMOJI = {"P": "👤", "B": "🏦", "T": "🤝"}
    LABEL = {"P": "Player", "B": "Banker", "T": "Tie"}
    VALID = {"P", "B", "T", "PLAYER", "BANKER", "TIE"}
    ALIAS = {"PLAYER": "P", "BANKER": "B", "TIE": "T"}

    def __init__(self, analyzer: BacBoAnalyzer):
        self.analyzer = analyzer

    def register_result(self, raw: str) -> str:
        result = self.ALIAS.get(raw.upper(), raw.upper())

        if result not in ("P", "B", "T"):
            return (
                "❌ *Resultado inválido!*\n"
                "Use: `P` (Player), `B` (Banker) ou `T` (Tie)\n"
                "Exemplo: `/resultado B`"
            )

        ok = self.analyzer.add_result(result)
        if not ok:
            return "❌ Erro ao registrar resultado."

        total = len(self.analyzer.history)
        emoji = self.EMOJI[result]
        label = self.LABEL[result]
        now = datetime.now().strftime("%H:%M:%S")

        return (
            f"✅ *Resultado registrado!*\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"{emoji} *{label}*  `{now}`\n\n"
            f"📋 Total de rodadas: *{total}*\n"
            f"💡 Use /signal para ver o próximo sinal."
        )

    def get_history_text(self) -> str:
        h = list(self.analyzer.history)
        if not h:
            return "📭 *Histórico vazio.*\nUse /resultado para registrar rodadas."

        last20 = h[-20:]
        rows = []
        for i, r in enumerate(reversed(last20), 1):
            e = self.EMOJI.get(r, "❓")
            l = self.LABEL.get(r, r)
            rows.append(f"`{i:>2}.` {e} {l}")

        visual = " ".join(self.EMOJI.get(r, "❓") for r in last20)

        return (
            f"📊 *Histórico — últimas {len(last20)} rodadas*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"*Visual:*\n{visual}\n\n"
            + "\n".join(rows) +
            f"\n\n📋 Total acumulado: *{len(h)}* rodadas"
        )

    def get_stats_text(self) -> str:
        stats = self.analyzer.get_full_stats()
        h = list(self.analyzer.history)
        freq = stats["frequency"]
        sk = stats["streak_result"]
        sl = stats["streak_length"]

        if not h:
            return "📭 *Sem dados suficientes.*\nRegistre pelo menos 5 rodadas."

        def bar(pct):
            filled = round(pct / 5)
            return "█" * filled + "░" * (20 - filled)

        p_pct = freq.get("P", 0)
        b_pct = freq.get("B", 0)
        t_pct = freq.get("T", 0)

        streak_str = (
            f"{self.EMOJI.get(sk,'')} {self.LABEL.get(sk,'')} — {sl} seguidos"
            if sk and sl > 1 else "Nenhum streak ativo"
        )

        return (
            f"📈 *Estatísticas Completas*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📋 *Total de rodadas:* {stats['total']}\n\n"
            f"*Distribuição:*\n"
            f"👤 Player `{p_pct:5.1f}%` `{bar(p_pct)}`\n"
            f"🏦 Banker `{b_pct:5.1f}%` `{bar(b_pct)}`\n"
            f"🤝 Tie    `{t_pct:5.1f}%` `{bar(t_pct)}`\n\n"
            f"🔥 *Streak atual:* {streak_str}\n\n"
            f"⏪ *Últimas 10:*\n"
            f"{'  '.join(self.EMOJI.get(r,'❓') for r in h[-10:])}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💡 Use /signal para gerar sinal."
  )
