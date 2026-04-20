from typing import Any, Dict
import cv2


class FrameProcessor:
    def __init__(self, config: Dict[str, Any], logger: Any) -> None:
        self.logger = logger
        self.zone = config["zones"]["restricted_area"]

    def annotate_frame(
        self,
        frame: Any,
        sensor_data: Dict[str, Any],
        vision_data: Dict[str, Any],
        decision: str,
        reason: str,
    ) -> Any:
        annotated = frame.copy()

        # Draw restricted zone
        cv2.rectangle(
            annotated,
            (self.zone["x1"], self.zone["y1"]),
            (self.zone["x2"], self.zone["y2"]),
            (255, 0, 0),
            2,
        )
        cv2.putText(
            annotated,
            "Restricted Zone",
            (self.zone["x1"], self.zone["y1"] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 0, 0),
            2,
        )

        # Draw detection boxes
        for category in vision_data.values():
            for det in category:
                bbox = det.get("bbox")
                if not bbox:
                    continue
                x1, y1, x2, y2 = map(int, bbox)
                label = det.get("label", "obj")
                conf = det.get("confidence", 0.0)

                cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(
                    annotated,
                    f"{label} {conf:.2f}",
                    (x1, max(y1 - 8, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (0, 255, 0),
                    2,
                )

        # Sensor panel
        y = 25
        for text in [
            f"Decision: {decision}",
            f"Reason: {reason}",
            f"Gas: {sensor_data.get('gas', 0)}",
            f"Temperature: {sensor_data.get('temperature', 0)}",
            f"Vibration: {sensor_data.get('vibration', 0)}",
        ]:
            cv2.putText(
                annotated,
                text,
                (10, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 0, 255) if y == 25 else (255, 255, 255),
                2,
            )
            y += 28

        return annotated