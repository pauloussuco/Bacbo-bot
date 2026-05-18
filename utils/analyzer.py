"""
Analisador estatístico para Bac Bo - Versão corrigida e equilibrada
"""

from collections import Counter, deque
from config.settings import MAX_HISTORY, MIN_HISTORY_SIGNAL


class BacBoAnalyzer:

    VALID_RESULTS = {"P", "B", "T"}
    LABELS = {"P": "🔵 Player", "B": "🔴 Banker", "T": "🟠 Tie"}

    def __init__(self):
        self.history: deque = deque(maxlen=MAX_HISTORY)
        self.wins = 0
        self.losses = 0
        self.total_signals = 0

    def add_result(self, result: str) -> bool:
        result = result.upper()
        if result not in self.VALID_RESULTS:
            return False
        self.history.append(result)
        return True

    def reset(self):
        self.history.clear()
        self.wins = 0
        self.losses = 0
        self.total_signals = 0

    def generate_signal(self) -> dict:
        h = list(self.history)
        n = len(h)

        if n < MIN_HISTORY_SIGNAL:
            return {
                "suggestion": None,
                "confidence": 0,
                "reason": f"Histórico insuficiente ({n}/{MIN_HISTORY_SIGNAL} rodadas mínimas).",
                "trend": "neutral",
                "stats": self._base_stats(h),
            }

        scores = {"P": 0.0, "B": 0.0, "T": 0.0}

        # Indicador 1 — Frequência últimas 20
        last20 = h[-20:] if len(h) >= 20 else h
        freq20 = self._frequency(last20)
        for k in ("P", "B", "T"):
            scores[k] += freq20.get(k, 0) * 1.0

        # Indicador 2 — Tendência recente últimas 8 (peso 2x)
        recent = h[-8:]
        freq_recent = self._frequency(recent)
        for k in ("P", "B", "T"):
            scores[k] += freq_recent.get(k, 0) * 2.0

        # Indicador 3 — Streak ativo
        streak_sig, streak_len = self._streak_signal(h)
        if streak_sig:
            if streak_len >= 3:
                for k in ("P", "B"):
                    if k != streak_sig:
                        scores[k] += streak_len * 5
            elif streak_len >= 2:
                scores[streak_sig] += streak_len * 2

        # Indicador 4 — Alternância
        alt = self._alternation_signal(h)
        if alt:
            scores[alt] += 25

        # Indicador 5 — Zigzag
        zigzag = self._zigzag_signal(h)
        if zigzag:
            scores[zigzag] += 20

        # Indicador 6 — Desequilíbrio histórico
        freq_all = self._frequency(h)
        p_pct = freq_all.get("P", 0)
        b_pct = freq_all.get("B", 0)
        if p_pct > 60:
            scores["B"] += 20
        elif b_pct > 60:
            scores["P"] += 20

        # Escolhe entre P e B apenas (T só se muito dominante)
        pb_scores = {"P": scores["P"], "B": scores["B"]}
        t_score = scores["T"]

        if t_score > max(pb_scores.values()) * 1.8:
            suggestion = "T"
        else:
            suggestion = max(pb_scores, key=lambda k: pb_scores[k])

        total_score = sum(scores.values()) or 1
        confidence = round((scores[suggestion] / total_score) * 100)
        confidence = max(50, min(confidence, 88))

        trend = self._trend(h)
        reason = self._build_reason(h, suggestion, streak_sig, streak_len, zigzag, alt, freq_recent)

        return {
            "suggestion": suggestion,
            "confidence": confidence,
            "reason": reason,
            "trend": trend,
            "stats": self._base_stats(h),
        }

    def _frequency(self, history: list) -> dict:
        if not history:
            return {"P": 0, "B": 0, "T": 0}
        c = Counter(history)
        total = len(history)
        return {k: round(c.get(k, 0) / total * 100, 1) for k in self.VALID_RESULTS}

    def _streak_signal(self, history: list) -> tuple:
        if not history:
            return None, 0
        last = history[-1]
        count = 1
        for r in reversed(history[:-1]):
            if r == last:
                count += 1
            else:
                break
        return last, count

    def _alternation_signal(self, history: list):
        if len(history) < 6:
            return None
        pb_only = [r for r in history[-6:] if r in ("P", "B")]
        if len(pb_only) < 4:
            return None
        alternating = all(pb_only[i] != pb_only[i + 1] for i in range(len(pb_only) - 1))
        if alternating:
            return "B" if pb_only[-1] == "P" else "P"
        return None

    def _zigzag_signal(self, history: list):
        if len(history) < 6:
            return None
        pb = [r for r in history[-8:] if r in ("P", "B")]
        if len(pb) < 6:
            return None
        pairs = [pb[i] == pb[i + 1] for i in range(0, len(pb) - 1, 2)]
        if len(pairs) >= 3 and all(pairs):
            last_pair = pb[-2:]
            if len(set(last_pair)) == 1:
                return "B" if last_pair[0] == "P" else "P"
            else:
                return pb[-1]
        return None

    def _trend(self, history: list) -> str:
        if len(history) < 10:
            return "neutral"
        last10 = history[-10:]
        p = last10.count("P")
        b = last10.count("B")
        if p >= 7:
            return "player_dominant"
        if b >= 7:
            return "banker_dominant"
        return "balanced"

    def _build_reason(self, h, suggestion, streak_sig, streak_len, zigzag, alt, recent_freq) -> str:
        reasons = []
        if streak_sig and streak_len >= 3 and suggestion != streak_sig:
            reasons.append(f"Streak de {streak_len}x {self.LABELS[streak_sig]} — quebra provável")
        elif streak_sig and streak_len >= 2 and suggestion == streak_sig:
            reasons.append(f"Sequência ativa de {streak_len}x {self.LABELS[streak_sig]}")
        if alt and suggestion == alt:
            reasons.append("Padrão alternância detectado")
        if zigzag and suggestion == zigzag:
            reasons.append("Padrão zigzag identificado")
        dominant = max(recent_freq, key=lambda k: recent_freq.get(k, 0)) if recent_freq else None
        if dominant and dominant == suggestion:
            reasons.append(f"{self.LABELS[dominant]} dominando ({recent_freq.get(dominant, 0):.0f}%)")
        if not reasons:
            freq = self._frequency(h)
            reasons.append(f"Frequência favorece {self.LABELS[suggestion]} ({freq.get(suggestion, 0):.1f}%)")
        return " • ".join(reasons)

    def _base_stats(self, history: list) -> dict:
        freq = self._frequency(history)
        streak_sig, streak_len = self._streak_signal(history)
        return {
            "total": len(history),
            "frequency": freq,
            "streak_result": streak_sig,
            "streak_length": streak_len,
            "last_5": history[-5:] if len(history) >= 5 else history,
        }

    def get_full_stats(self) -> dict:
        h = list(self.history)
        return {**self._base_stats(h), "wins": self.wins, "losses": self.losses, "total_signals": self.total_signals}