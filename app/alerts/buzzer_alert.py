from typing import Any


class BuzzerAlert:
    def __init__(self, logger: Any) -> None:
        self.logger = logger

    def trigger(self) -> None:
        # Future GPIO/buzzer integration point.
        self.logger.warning("Buzzer alert triggered")