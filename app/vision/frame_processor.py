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

        # Draw a moving zone in front of the detected vehicle if present,
        # otherwise keep the static restricted area.
        dynamic_zone = self._compute_dynamic_zone(frame, vision_data)
        if dynamic_zone is not None:
            zx1, zy1, zx2, zy2 = dynamic_zone
            zone_label = "Vehicle Ahead"
        else:
            zx1, zy1, zx2, zy2 = (
                self.zone["x1"],
                self.zone["y1"],
                self.zone["x2"],
                self.zone["y2"],
            )
            zone_label = "Restricted Zone"

        cv2.rectangle(annotated, (zx1, zy1), (zx2, zy2), (255, 0, 0), 2)
        cv2.putText(
            annotated,
            zone_label,
            (zx1, max(zy1 - 10, 20)),
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

    def _compute_dynamic_zone(self, frame: Any, vision_data: Dict[str, Any]) -> Any:
        vehicle_bbox = self._find_vehicle_bbox(vision_data)
        if vehicle_bbox is None:
            return None
        return self._zone_in_front_of_bbox(frame, vehicle_bbox)

    def _find_vehicle_bbox(self, vision_data: Dict[str, Any]) -> Any:
        vehicle_labels = {
            "vehicle",
            "car",
            "truck",
            "bus",
            "van",
            "motorbike",
            "motorcycle",
            "bicycle",
            "bike",
        }
        for category in vision_data.values():
            for det in category:
                label = str(det.get("label", "")).lower()
                if label in vehicle_labels:
                    bbox = det.get("bbox")
                    if bbox:
                        return list(map(int, bbox))
        return None

    def _zone_in_front_of_bbox(self, frame: Any, bbox: Any) -> Any:
        frame_h, frame_w = frame.shape[:2]
        x1, y1, x2, y2 = bbox
        width = x2 - x1
        height = y2 - y1
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2

        if width >= height:
            zone_h = max(int(height * 0.45), 40)
            if center_x < frame_w / 2:
                zx1 = x2 + 10
                zx2 = min(zx1 + width, frame_w - 1)
            else:
                zx2 = x1 - 10
                zx1 = max(zx2 - width, 0)
            zy1 = max(y1 + height // 4, 0)
            zy2 = min(zy1 + zone_h, frame_h - 1)
        else:
            zone_w = max(int(width * 0.8), 40)
            if center_y < frame_h / 2:
                zy1 = y2 + 10
                zy2 = min(zy1 + height, frame_h - 1)
            else:
                zy2 = y1 - 10
                zy1 = max(zy2 - height, 0)
            zx1 = max(x1 + (width - zone_w) // 2, 0)
            zx2 = min(zx1 + zone_w, frame_w - 1)

        if zx2 <= zx1 or zy2 <= zy1:
            return None

        return (zx1, zy1, zx2, zy2)
