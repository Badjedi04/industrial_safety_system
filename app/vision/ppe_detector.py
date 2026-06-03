from typing import Any, Dict, List
import os
import cv2
from app.core.constants import CLASS_NAMES
from app.vision.model_loader import ModelLoader


class PPEDetector:
    def __init__(self, config: Dict[str, Any], logger: Any) -> None:
        self.logger = logger
        vision_cfg = config["vision"]
        model_path = vision_cfg["ppe_model_path"]
        if not os.path.exists(model_path) and vision_cfg.get("use_default_yolo_if_missing", True):
            self.logger.warning(
                "Custom PPE model not found at %s. Using default YOLO fallback; helmet/no-helmet alerts may not work correctly.",
                model_path,
            )

        self.model = ModelLoader.load_yolo_model(
            model_path=model_path,
            use_default_if_missing=vision_cfg.get("use_default_yolo_if_missing", True),
            logger=logger,
        )
        self.conf_threshold = vision_cfg["confidence_threshold"]
        self.class_names = self._build_class_names(self.model.names)
        self.helmet_class_ids = {
            class_id
            for class_id, label in self.class_names.items()
            if self._is_helmet_label(label)
        }
        self.no_helmet_class_ids = {
            class_id
            for class_id, label in self.class_names.items()
            if self._is_no_helmet_label(label)
        }
        self.person_class_ids = {
            class_id
            for class_id, label in self.class_names.items()
            if self._is_person_label(label)
        }

        if not self.helmet_class_ids and not self.no_helmet_class_ids:
            self.logger.warning(
                "PPE model has no helmet/no_helmet classes. Falling back to heuristic head-region inference.",
            )
        else:
            self.logger.info(
                "PPE model classes: helmet_ids=%s no_helmet_ids=%s person_ids=%s",
                sorted(self.helmet_class_ids),
                sorted(self.no_helmet_class_ids),
                sorted(self.person_class_ids),
            )

    def _build_class_names(self, model_names: Dict[int, str]) -> Dict[int, str]:
        normalized = {int(k): str(v) for k, v in model_names.items()}
        for class_id, fallback_name in CLASS_NAMES.items():
            normalized.setdefault(class_id, fallback_name)
        return normalized

    def _normalize_label(self, label: Any) -> str:
        return str(label).strip().lower().replace(" ", "_")

    def _is_person_label(self, label: Any) -> bool:
        label = self._normalize_label(label)
        return label in {"person", "people", "human"} or "person" in label

    def _is_helmet_label(self, label: Any) -> bool:
        label = self._normalize_label(label)
        return any(token in label for token in {"helmet", "hardhat", "hard_hat"})

    def _is_no_helmet_label(self, label: Any) -> bool:
        label = self._normalize_label(label)
        return (
            label in {"no_helmet", "without_helmet", "no_hardhat", "no_hard_hat"}
            or ("no" in label and "helmet" in label)
            or ("no" in label and "hardhat" in label)
        )

    def _iou(self, bbox1: List[float], bbox2: List[float]) -> float:
        x1, y1, x2, y2 = map(int, bbox1)
        xx1, yy1, xx2, yy2 = map(int, bbox2)
        xi1 = max(x1, xx1)
        yi1 = max(y1, yy1)
        xi2 = min(x2, xx2)
        yi2 = min(y2, yy2)
        inter_width = max(0, xi2 - xi1)
        inter_height = max(0, yi2 - yi1)
        inter_area = inter_width * inter_height
        area1 = max(0, x2 - x1) * max(0, y2 - y1)
        area2 = max(0, xx2 - xx1) * max(0, yy2 - yy1)
        if area1 + area2 - inter_area <= 0:
            return 0.0
        return inter_area / float(area1 + area2 - inter_area)

    def _has_helmet_in_head_region(self, frame: Any, bbox: List[float]) -> bool:
        x1, y1, x2, y2 = map(int, bbox)
        width = max(1, x2 - x1)
        height = max(1, y2 - y1)
        head_top = y1
        head_bottom = y1 + max(1, int(height * 0.35))
        head_left = x1 + max(0, int(width * 0.15))
        head_right = x2 - max(0, int(width * 0.15))

        head_crop = frame[head_top:head_bottom, head_left:head_right]
        if head_crop.size == 0:
            return False

        hsv = cv2.cvtColor(head_crop, cv2.COLOR_BGR2HSV)
        yellow_mask = cv2.inRange(hsv, (10, 80, 100), (40, 255, 255))
        white_mask = cv2.inRange(hsv, (0, 0, 180), (180, 60, 255))
        combined = cv2.bitwise_or(yellow_mask, white_mask)
        helmet_pixels = cv2.countNonZero(combined)
        total_pixels = head_crop.shape[0] * head_crop.shape[1]
        if total_pixels == 0:
            return False
        helmet_fraction = helmet_pixels / float(total_pixels)
        return helmet_fraction >= 0.18

    def _infer_no_helmet(self, frame: Any, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if any(self._is_no_helmet_label(det["label"]) for det in detections):
            return detections

        person_detections = [
            det for det in detections if self._is_person_label(det["label"])
        ]
        if not person_detections:
            return detections

        helmet_detections = [
            det for det in detections if self._is_helmet_label(det["label"])
        ]

        inferred = []
        for person in person_detections:
            if helmet_detections:
                overlap = any(
                    self._iou(person["bbox"], helmet["bbox"]) > 0.15
                    for helmet in helmet_detections
                )
                if overlap:
                    continue
            else:
                if self._has_helmet_in_head_region(frame, person["bbox"]):
                    continue

            inferred.append(
                {
                    "class_id": 1,
                    "label": "no_helmet",
                    "confidence": person.get("confidence", 0.0),
                    "bbox": person["bbox"],
                }
            )

        if inferred:
            self.logger.info(
                "Inferred %d missing-helmet detections from person boxes.",
                len(inferred),
            )
            detections.extend(inferred)

        return detections

    def detect(self, frame: Any) -> List[Dict[str, Any]]:
        results = self.model.predict(frame, verbose=False)
        detections: List[Dict[str, Any]] = []

        for result in results:
            for box in result.boxes:
                confidence = float(box.conf[0])
                if confidence < self.conf_threshold:
                    continue

                class_id = int(box.cls[0])
                bbox = box.xyxy[0].tolist()
                raw_label = self.class_names.get(class_id, str(class_id))
                label = raw_label.lower().replace(" ", "_")

                detections.append(
                    {
                        "class_id": class_id,
                        "label": label,
                        "confidence": round(confidence, 3),
                        "bbox": bbox,
                    }
                )

        detections = self._infer_no_helmet(frame, detections)
        self.logger.info("PPE detections count: %d", len(detections))
        return detections

    def has_person(self, detections: List[Dict[str, Any]]) -> bool:
        return any(
            det["label"] == "person" or det.get("class_id") == 4 for det in detections
        )

    def has_no_helmet(self, detections: List[Dict[str, Any]]) -> bool:
        # For a trained PPE model, change the label to match your dataset class
        return any(
            det["label"] in {"no_helmet", "without_helmet"} or det.get("class_id") == 1
            for det in detections
        )