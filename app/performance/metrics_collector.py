import csv
import os
import time
from typing import Any, Dict, List, Optional

try:
    import psutil
except ImportError:  # pragma: no cover - optional runtime dependency
    psutil = None


class MetricsCollector:
    """Collect frame-level runtime metrics for research evaluation."""

    def __init__(self, output_path: str = "data/performance_metrics.csv") -> None:
        self.output_path = output_path
        self.records: List[Dict[str, Any]] = []
        self.start_time = time.perf_counter()
        self.last_frame_time: Optional[float] = None
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

    @staticmethod
    def now() -> float:
        return time.perf_counter()

    @staticmethod
    def elapsed_ms(start_time: float, end_time: Optional[float] = None) -> float:
        if end_time is None:
            end_time = time.perf_counter()
        return round((end_time - start_time) * 1000, 3)

    def calculate_fps(self, current_time: float) -> float:
        if self.last_frame_time is None:
            self.last_frame_time = current_time
            return 0.0

        delta = current_time - self.last_frame_time
        self.last_frame_time = current_time
        if delta <= 0:
            return 0.0
        return round(1.0 / delta, 3)

    def get_system_metrics(self) -> Dict[str, float]:
        if psutil is None:
            return {"cpu_percent": -1.0, "memory_mb": -1.0}

        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / (1024 * 1024)
        return {
            "cpu_percent": float(psutil.cpu_percent(interval=None)),
            "memory_mb": round(memory_mb, 3),
        }

    def record_frame(self, record: Dict[str, Any]) -> None:
        self.records.append(record)

    def save_csv(self) -> None:
        if not self.records:
            return

        with open(self.output_path, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=list(self.records[0].keys()))
            writer.writeheader()
            writer.writerows(self.records)

    def _average(self, key: str) -> float:
        values = [
            row[key]
            for row in self.records
            if isinstance(row.get(key), (int, float))
        ]
        if not values:
            return 0.0
        return round(sum(values) / len(values), 3)

    def summarize(self) -> Dict[str, Any]:
        if not self.records:
            return {}

        decision_distribution: Dict[str, int] = {}
        for row in self.records:
            decision = str(row.get("decision", "UNKNOWN"))
            decision_distribution[decision] = decision_distribution.get(decision, 0) + 1

        return {
            "total_frames": len(self.records),
            "average_fps": self._average("fps"),
            "average_frame_processing_time_ms": self._average("frame_processing_time_ms"),
            "average_sensor_read_time_ms": self._average("sensor_read_time_ms"),
            "average_frame_read_time_ms": self._average("frame_read_time_ms"),
            "average_ppe_detection_time_ms": self._average("ppe_detection_time_ms"),
            "average_fall_detection_time_ms": self._average("fall_detection_time_ms"),
            "average_zone_detection_time_ms": self._average("zone_detection_time_ms"),
            "average_fusion_time_ms": self._average("fusion_time_ms"),
            "average_alert_time_ms": self._average("alert_time_ms"),
            "average_logging_time_ms": self._average("logging_time_ms"),
            "average_annotation_time_ms": self._average("annotation_time_ms"),
            "average_display_time_ms": self._average("display_time_ms"),
            "average_cpu_percent": self._average("cpu_percent"),
            "average_memory_mb": self._average("memory_mb"),
            "decision_distribution": decision_distribution,
        }

    def save_summary(self, output_path: str = "data/performance_summary.txt") -> None:
        summary = self.summarize()
        if not summary:
            return

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as file:
            for key, value in summary.items():
                file.write(f"{key}: {value}\n")
