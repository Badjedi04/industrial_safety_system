from typing import Any, Dict


class TemperatureSensor:
    def __init__(self, config: Dict[str, Any], logger: Any) -> None:
        self.threshold = config["thresholds"]["temperature"]
        self.logger = logger

    def read(self) -> float:
        value = 32.0
        self.logger.debug("Temperature sensor value: %s", value)
        return value

    def is_alert(self, value: float) -> bool:
        return value > self.threshold