from app.sensors.sensor_preprocessing import SensorPreprocessor


def test_sensor_normalization():
    raw = {"gas": "100", "temperature": "32", "vibration": "50"}
    result = SensorPreprocessor.normalize(raw)
    assert result["gas"] == 100.0
    assert result["temperature"] == 32.0
    assert result["vibration"] == 50.0