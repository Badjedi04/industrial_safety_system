from typing import Any, Dict, List


class RuleBasedFusion:
    def __init__(self, thresholds: Dict[str, Any]) -> None:
        self.thresholds = thresholds

    def evaluate_rules(
        self, sensor_data: Dict[str, float], vision_data: Dict[str, List[Dict[str, Any]]]
    ) -> str:
        gas_high = sensor_data.get("gas", 0) > self.thresholds["gas"]
        temp_high = sensor_data.get("temperature", 0) > self.thresholds["temperature"]
        vibration_high = sensor_data.get("vibration", 0) > self.thresholds["vibration"]

        ppe_detections = vision_data.get("ppe", [])
        fall_detections = vision_data.get("fall", [])

        no_helmet = any(det.get("class_id") == 1 for det in ppe_detections)
        fall_detected = len(fall_detections) > 0

        if gas_high and no_helmet:
            return "CRITICAL_ALERT"

        if fall_detected:
            return "EMERGENCY"

        if temp_high or vibration_high:
            return "HIGH_RISK"

        return "SAFE"