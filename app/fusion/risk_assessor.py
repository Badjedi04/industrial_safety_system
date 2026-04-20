class RiskAssessor:
    @staticmethod
    def assess(score: float) -> str:
        if score >= 0.85:
            return "CRITICAL_ALERT"
        if score >= 0.65:
            return "HIGH_RISK"
        if score >= 0.40:
            return "MEDIUM_RISK"
        if score > 0:
            return "LOW_RISK"
        return "SAFE"