"""
Formata e entrega sinais para o Telegram.
"""

from datetime import datetime
from utils.analyzer import BacBoAnalyzer
from config.settings import CONFIDENCE_HIGH, CONFIDENCE_MEDIUM


class SignalHandler:

    EMOJI_RESULT = {"P": "👤", "B": "🏦", "T": "🤝"}
    LABEL = {"P": "PLAYER", "B": "BANKER", "T": "TIE"}

    def __init__(self, analyzer: BacBoAnalyzer):
        self.analyzer = analyzer

    def generate_signal(self) -> str:
        data = self.analyzer.generate_signal()
        now = datetime.now().strftime("%H:%M:%S")

        if data["suggestion"] is None:
            stats = data["stats"]
            return (
                "⏳ *Sinal indisponível*\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"{data['reason']}\n\n"
                f"📋 Rodadas registradas: *{stats['total']}*\n"
                f"Use /resultado para registrar mais rodadas."
            )

        sug = data["suggestion"]
        conf = data["confidence"]
        stats = data["stats"]
        freq = stats["frequency"]

        if conf >= CONFIDENCE_HIGH:
            conf_icon = "🟢"
            conf_label = "ALTA"
        elif conf >= CONFIDENCE_MEDIUM:
            conf_icon = "🟡"
            conf_label = "MÉDIA"
        else:
            conf_icon = "🔴"
            conf_label = "BAIXA"

        last5 = stats.get("last_5", [])
        last5_str = "  ".join(self.EMOJI_RESULT.get(r, "❓") for r in last5) or "—"

        sk = stats["streak_result"]
        sl = stats["streak_length"]
        streak_str = f"{self.EMOJI_RESULT.get(sk,'')} {sl}x seguidos" if sk and sl > 1 else "Sem streak"

        trend_map = {
            "player_dominant": "📈 Player dominando",
            "banker_dominant": "📉 Banker dominando",
            "balanced": "⚖️ Equilibrado",
            "neutral": "➖ Neutro",
        }
        trend_str = trend_map.get(data["trend"], "—")

        text = (
            f"🎲 *SINAL BAC BO*  `{now}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🎯 *Apostar em:*  {self.EMOJI_RESULT[sug]} `{self.LABEL[sug]}`\n\n"
            f"{conf_icon} *Confiança:* {conf}% — {conf_label}\n\n"
            f"📊 *Frequências (geral)*\n"
            f"  👤 Player: `{freq.get('P', 0):.1f}%`\n"
            f"  🏦 Banker: `{freq.get('B', 0):.1f}%`\n"
            f"  🤝 Tie:    `{freq.get('T', 0):.1f}%`\n\n"
            f"🔥 *Streak atual:* {streak_str}\n"
            f"📈 *Tendência:* {trend_str}\n\n"
            f"⏪ *Últimas 5:*  {last5_str}\n\n"
            f"💡 *Análise:*\n_{data['reason']}_\n\n"
            f"📋 Total de rodadas: *{stats['total']}*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ _Use com responsabilidade._"
        )
        return text
