from typing import Any, Dict
from app.sensors.sensor_reader import SensorReader
from app.sensors.sensor_preprocessing import SensorPreprocessor


class SensorManager:
    def __init__(self, config: Dict[str, Any], logger: Any) -> None:
        self.logger = logger
        self.reader = SensorReader(config, logger)
        self.preprocessor = SensorPreprocessor()

    def read_all(self) -> Dict[str, float]:
        raw_data = self.reader.read()
        normalized = self.preprocessor.normalize(raw_data)
        processed = self.preprocessor.smooth(normalized)

        self.logger.info(
            "Sensor data | raw=%s | processed=%s",
            raw_data,
            processed,
        )
        return processed