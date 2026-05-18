"""
Signal Handler - Estilo AYO BOT VIP
"""

from datetime import datetime
from utils.analyzer import BacBoAnalyzer
from config.settings import CONFIDENCE_HIGH, CONFIDENCE_MEDIUM


class SignalHandler:

    EMOJI = {"P": "🔵", "B": "🔴", "T": "🟠"}
    LABEL = {"P": "PLAYER", "B": "BANKER", "T": "TIE"}

    def __init__(self, analyzer: BacBoAnalyzer):
        self.analyzer = analyzer
        self.greens = 0
        self.reds = 0
        self.last_signal = None
        self.streak = 0

    def register_outcome(self, resultado: str):
        """Verifica se o último sinal acertou."""
        if self.last_signal is None:
            return

        if self.last_signal == resultado or (self.last_signal != "T" and resultado == "T"):
            self.greens += 1
            self.streak += 1
            return "green"
        else:
            self.reds += 1
            self.streak = 0
            return "red"

    def accuracy(self) -> float:
        total = self.greens + self.reds
        if total == 0:
            return 0.0
        return round((self.greens / total) * 100, 2)

    def generate_signal(self) -> str:
        data = self.analyzer.generate_signal()
        now = datetime.now().strftime("%H:%M")

        if data["suggestion"] is None:
            stats = data["stats"]
            restantes = 5 - stats["total"]
            return (
                f"⏳ *Analisando mesa...*\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🎲 *Bac Bo Ao Vivo* 🇧🇷\n\n"
                f"Faltam *{restantes}* resultado(s) para o primeiro sinal!\n\n"
                f"📊 Rodadas registadas: *{stats['total']}/5*"
            )

        sug = data["suggestion"]
        conf = data["confidence"]
        stats = data["stats"]
        freq = stats["frequency"]
        sk = stats["streak_result"]
        sl = stats["streak_length"]

        # Streak texto
        streak_txt = ""
        if self.streak >= 2:
            streak_txt = f"\n💰 *Estamos com {self.streak} greens seguidos!*\n"

        # Placard
        acc = self.accuracy()
        placard = (
            f"📊 Placard do dia  🟢 *{self.greens}*  🔴 *{self.reds}*\n"
            f"🎯 Acertamos: *{acc}%* das vezes"
        ) if (self.greens + self.reds) > 0 else ""

        # Confiança
        if conf >= CONFIDENCE_HIGH:
            conf_bar = "🟢🟢🟢🟢🟢"
        elif conf >= CONFIDENCE_MEDIUM:
            conf_bar = "🟡🟡🟡⚫⚫"
        else:
            conf_bar = "🔴🔴⚫⚫⚫"

        # Histórico visual
        last5 = stats.get("last_5", [])
        visual = "  ".join(self.EMOJI.get(r, "⚫") for r in last5)

        text = (
            f"🚀 *APOSTE NA COR* {self.EMOJI[sug]}\n"
            f"🟠 Proteger no empate!\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🎲 *Bac Bo Ao Vivo* 🇧🇷 — `{now}`\n\n"
            f"🎯 *Apostar em:* {self.EMOJI[sug]} `{self.LABEL[sug]}`\n\n"
            f"📶 Confiança: {conf_bar} *{conf}%*\n\n"
            f"📈 *Frequências:*\n"
            f"🔵 Player: `{freq.get('P', 0):.1f}%`\n"
            f"🔴 Banker: `{freq.get('B', 0):.1f}%`\n"
            f"🟠 Tie:    `{freq.get('T', 0):.1f}%`\n\n"
            f"⏪ Últimas 5: {visual}\n\n"
        )

        if streak_txt:
            text += streak_txt + "\n"

        if placard:
            text += placard + "\n"

        text += f"\n⚠️ _Use com responsabilidade._"

        # Guarda último sinal
        self.last_signal = sug

        return text

    def get_resultado_feedback(self, resultado: str) -> str:
        """Retorna feedback após registar resultado."""
        outcome = self.register_outcome(resultado)

        emoji_r = self.EMOJI.get(resultado, "⚫")
        label_r = self.LABEL.get(resultado, resultado)

        if outcome == "green":
            return (
                f"✅ *+DINHEIRO NA CONTA* 🤑\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"Resultado: {emoji_r} *{label_r}*\n\n"
                f"💰 *{self.streak} green(s) seguidos!*\n"
                f"🟢 Greens: *{self.greens}*  🔴 Reds: *{self.reds}*\n"
                f"🎯 Acerto: *{self.accuracy()}%*"
            )
        elif outcome == "red":
            return (
                f"❌ *Resultado diferente*\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"Resultado: {emoji_r} *{label_r}*\n\n"
                f"🟢 Greens: *{self.greens}*  🔴 Reds: *{self.reds}*\n"
                f"🎯 Acerto: *{self.accuracy()}%*"
            )
        else:
            return (
                f"📝 *Resultado registado*\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"Resultado: {emoji_r} *{label_r}*\n\n"
                f"📊 Total de rodadas: *{len(self.analyzer.history)}*"
            )