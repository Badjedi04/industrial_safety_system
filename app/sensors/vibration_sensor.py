from typing import Any, Dict


class VibrationSensor:
    def __init__(self, config: Dict[str, Any], logger: Any) -> None:
        self.threshold = config["thresholds"]["vibration"]
        self.logger = logger

    def read(self) -> float:
        value = 120.0
        self.logger.debug("Vibration sensor value: %s", value)
        return value

    def is_alert(self, value: float) -> bool:
        return value > self.threshold