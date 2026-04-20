def test_alert_payload_structure():
    payload = {
        "decision": "CRITICAL_ALERT",
        "sensor_data": {"gas": 500},
        "vision_data": {"ppe": []},
    }
    assert "decision" in payload
    assert "sensor_data" in payload
    assert "vision_data" in payload