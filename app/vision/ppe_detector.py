from typing import Any, Dict, List
import os
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

    def _build_class_names(self, model_names: Dict[int, str]) -> Dict[int, str]:
        normalized = {int(k): str(v) for k, v in model_names.items()}
        for class_id, fallback_name in CLASS_NAMES.items():
            normalized.setdefault(class_id, fallback_name)
        return normalized

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