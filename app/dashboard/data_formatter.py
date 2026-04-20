from typing import Any, Dict


class DataFormatter:
    @staticmethod
    def format_status(
        decision: str,
        sensor_data: Dict[str, Any],
        vision_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "decision": decision,
            "sensor_data": sensor_data,
            "vision_data": vision_data,
        }