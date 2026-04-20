from typing import Any, Dict


class GasSensor:
    def __init__(self, config: Dict[str, Any], logger: Any) -> None:
        self.threshold = config["thresholds"]["gas"]
        self.logger = logger

    def read(self) -> float:
        # Replace with real sensor reading logic
        value = 350.0
        self.logger.debug("Gas sensor value: %s", value)
        return value

    def is_alert(self, value: float) -> bool:
        return value > self.threshold