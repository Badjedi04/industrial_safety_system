from typing import Dict, List


class SensorPreprocessor:
    def __init__(self) -> None:
        self.history: List[Dict[str, float]] = []

    def normalize(self, data: Dict[str, float]) -> Dict[str, float]:
        normalized = {
            "gas": float(data.get("gas", 0.0)),
            "temperature": float(data.get("temperature", 0.0)),
            "vibration": float(data.get("vibration", 0.0)),
        }
        return normalized

    def smooth(self, data: Dict[str, float], window_size: int = 5) -> Dict[str, float]:
        self.history.append(data)
        if len(self.history) > window_size:
            self.history.pop(0)

        avg_gas = sum(item["gas"] for item in self.history) / len(self.history)
        avg_temp = sum(item["temperature"] for item in self.history) / len(self.history)
        avg_vib = sum(item["vibration"] for item in self.history) / len(self.history)

        return {
            "gas": round(avg_gas, 2),
            "temperature": round(avg_temp, 2),
            "vibration": round(avg_vib, 2),
        }