from typing import Any, Dict, List, Tuple


class FusionEngine:
    def __init__(self, config: Dict[str, Any], logger: Any) -> None:
        self.logger = logger
        self.thresholds = config["thresholds"]
        self.sensor_weight = config["risk_weights"]["sensor_weight"]
        self.vision_weight = config["risk_weights"]["vision_weight"]

    def _sensor_score(self, sensor_data: Dict[str, float]) -> float:
        gas_score = min(sensor_data["gas"] / self.thresholds["gas"], 1.0)
        temp_score = min(sensor_data["temperature"] / self.thresholds["temperature"], 1.0)
        vibration_score = min(sensor_data["vibration"] / self.thresholds["vibration"], 1.0)
        return max(gas_score, temp_score, vibration_score)

    def _vision_score(self, ppe_detections: List[Dict[str, Any]]) -> float:
        if not ppe_detections:
            return 0.0
        return max(det.get("confidence", 0.0) for det in ppe_detections)

    def _has_person(self, ppe_detections: List[Dict[str, Any]]) -> bool:
        return any(det.get("label") == "person" for det in ppe_detections)

    def _has_no_helmet(self, ppe_detections: List[Dict[str, Any]]) -> bool:
        return any(det.get("label") in {"no_helmet", "without_helmet"} for det in ppe_detections)

    def evaluate(
        self,
        sensor_data: Dict[str, float],
        vision_data: Dict[str, Any],
    ) -> Tuple[str, str]:
        ppe_detections = vision_data.get("ppe", [])
        fall_detections = vision_data.get("fall", [])

        gas_high = sensor_data["gas"] > self.thresholds["gas"]
        temp_high = sensor_data["temperature"] > self.thresholds["temperature"]
        vibration_high = sensor_data["vibration"] > self.thresholds["vibration"]

        has_person = self._has_person(ppe_detections)
        has_no_helmet = self._has_no_helmet(ppe_detections)
        fall_detected = len(fall_detections) > 0

        # Rule-based safety logic
        if gas_high and has_no_helmet:
            return "CRITICAL_ALERT", "Gas leak detected with missing head protection"

        if fall_detected:
            return "EMERGENCY", "Worker fall detected"

        if gas_high and has_person:
            return "HIGH_RISK", "Gas level above threshold in occupied area"

        if temp_high and has_person:
            return "HIGH_RISK", "Abnormal temperature in worker vicinity"

        if vibration_high:
            return "MEDIUM_RISK", "Abnormal machine vibration detected"

        # Weighted fallback score
        sensor_score = self._sensor_score(sensor_data)
        vision_score = self._vision_score(ppe_detections)
        final_score = (self.sensor_weight * sensor_score) + (
            self.vision_weight * vision_score
        )

        if final_score >= 0.85:
            return "HIGH_RISK", "Combined multimodal anomaly score is very high"
        if final_score >= 0.60:
            return "MEDIUM_RISK", "Combined multimodal anomaly score is elevated"

        return "SAFE", "No significant hazard detected"