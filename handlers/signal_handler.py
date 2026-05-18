"""
Signal Handler - Estilo AYO BOT VIP - Versão corrigida
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
        if self.last_signal is None:
            return None
        if self.last_signal == resultado:
            self.greens += 1
            self.streak += 1
            return "green"
        elif resultado == "T":
            return "tie"
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
                f"📊 Rodadas: *{stats['total']}/5*"
            )

        sug = data["suggestion"]
        conf = data["confidence"]
        stats = data["stats"]
        freq = stats["frequency"]

        # Barra de confiança
        if conf >= CONFIDENCE_HIGH:
            conf_bar = "🟢🟢🟢🟢🟢"
        elif conf >= CONFIDENCE_MEDIUM:
            conf_bar = "🟡🟡🟡⚫⚫"
        else:
            conf_bar = "🔴🔴⚫⚫⚫"

        # Histórico visual
        last5 = stats.get("last_5", [])
        visual = "  ".join(self.EMOJI.get(r, "⚫") for r in last5)

        # Streak info
        streak_sig = stats.get("streak_result")
        streak_len = stats.get("streak_length", 0)
        streak_txt = ""
        if streak_sig and streak_len >= 2:
            streak_txt = f"🔥 Streak: {self.EMOJI.get(streak_sig,'')} *{streak_len}x* seguidos\n"

        # Placard
        acc = self.accuracy()
        placard = ""
        if (self.greens + self.reds) > 0:
            placard = (
                f"\n📊 Placard do dia  🟢 *{self.greens}*  🔴 *{self.reds}*\n"
                f"🎯 Acertamos: *{acc}%* das vezes"
            )

        # Greens seguidos
        greens_txt = ""
        if self.streak >= 2:
            greens_txt = f"\n💰 *Estamos com {self.streak} greens seguidos!*"

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
            f"{streak_txt}"
            f"⏪ Últimas 5: {visual}"
            f"{greens_txt}"
            f"{placard}\n\n"
            f"⚠️ _Use com responsabilidade._"
        )

        self.last_signal = sug
        return text

    def get_resultado_feedback(self, resultado: str) -> str:
        outcome = self.register_outcome(resultado)
        emoji_r = self.EMOJI.get(resultado, "⚫")
        label_r = self.LABEL.get(resultado, resultado)

        if outcome == "green":
            return (
                f"✅ *GREEN* 🟢\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"Resultado: {emoji_r} *{label_r}*\n\n"
                f"💰 *{self.streak} green(s) seguidos!*\n"
                f"🟢 Greens: *{self.greens}*  🔴 Reds: *{self.reds}*\n"
                f"🎯 Acerto: *{self.accuracy()}%*"
            )
        elif outcome == "red":
            return (
                f"❌ *RED* 🔴\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"Resultado: {emoji_r} *{label_r}*\n\n"
                f"🟢 Greens: *{self.greens}*  🔴 Reds: *{self.reds}*\n"
                f"🎯 Acerto: *{self.accuracy()}%*"
            )
        elif outcome == "tie":
            return (
                f"🟠 *EMPATE — Protegido!*\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"Resultado: {emoji_r} *{label_r}*\n\n"
                f"🛡️ Aposta protegida no empate!\n"
                f"🟢 Greens: *{self.greens}*  🔴 Reds: *{self.reds}*"
            )
        else:
            return (
                f"📝 *Resultado registado*\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"Resultado: {emoji_r} *{label_r}*\n\n"
                f"📊 Total de rodadas: *{len(self.analyzer.history)}*"
            )