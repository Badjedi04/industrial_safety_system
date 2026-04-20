from typing import Any, Dict, List


class ZoneDetector:
    def __init__(self, config: Dict[str, Any], logger: Any) -> None:
        self.logger = logger
        self.zone = config["zones"]["restricted_area"]

    def detect(self, frame: Any) -> List[Dict[str, Any]]:
        # This module can be connected to tracked human bounding boxes later.
        return []

    def point_inside_zone(self, x: int, y: int) -> bool:
        return (
            self.zone["x1"] <= x <= self.zone["x2"]
            and self.zone["y1"] <= y <= self.zone["y2"]
        )