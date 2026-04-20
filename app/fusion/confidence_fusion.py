from typing import Dict


class ConfidenceFusion:
    def __init__(self, sensor_weight: float, vision_weight: float) -> None:
        self.sensor_weight = sensor_weight
        self.vision_weight = vision_weight

    def compute(self, sensor_score: float, vision_score: float) -> float:
        return (self.sensor_weight * sensor_score) + (
            self.vision_weight * vision_score
        )

    @staticmethod
    def normalize_score(score: float, max_value: float = 1.0) -> float:
        if max_value <= 0:
            return 0.0
        return min(max(score / max_value, 0.0), 1.0)