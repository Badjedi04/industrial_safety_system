from app.fusion.risk_assessor import RiskAssessor


def test_risk_assessment():
    assert RiskAssessor.assess(0.9) == "CRITICAL_ALERT"
    assert RiskAssessor.assess(0.7) == "HIGH_RISK"
    assert RiskAssessor.assess(0.0) == "SAFE"