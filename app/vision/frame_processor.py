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

        # Draw detection boxes with color-coding
        for category in vision_data.values():
            for det in category:
                bbox = det.get("bbox")
                if not bbox:
                    continue
                x1, y1, x2, y2 = map(int, bbox)
                label = det.get("label", "obj")
                conf = det.get("confidence", 0.0)

                # Normalize label for matching
                norm_label = str(label).lower()

                # Color mapping: red for violations, green for compliant
                if norm_label in {"no_helmet", "without_helmet", "no_vest", "no_personal_protection"}:
                    color = (0, 0, 255)  # red
                    badge_text = "NO HELMET" if "helmet" in norm_label else "NO PPE"
                elif norm_label in {"helmet", "vest", "with_helmet", "with_vest"}:
                    color = (0, 255, 0)  # green
                    badge_text = None
                elif norm_label == "person":
                    color = (255, 255, 0)  # yellow
                    badge_text = None
                else:
                    color = (0, 255, 0)
                    badge_text = None

                cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
                cv2.putText(
                    annotated,
                    f"{label} {conf:.2f}",
                    (x1, max(y1 - 8, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    color,
                    2,
                )

                # Draw a prominent badge for no-helmet cases
                if badge_text:
                    badge_w, badge_h = 200, 30
                    bx1 = x1
                    by1 = max(y1 - badge_h - 8, 8)
                    bx2 = bx1 + badge_w
                    by2 = by1 + badge_h
                    cv2.rectangle(annotated, (bx1, by1), (bx2, by2), (0, 0, 255), -1)
                    cv2.putText(
                        annotated,
                        badge_text,
                        (bx1 + 8, by1 + 22),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (255, 255, 255),
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