from typing import Any, Dict, List
from app.vision.model_loader import ModelLoader


class PPEDetector:
    def __init__(self, config: Dict[str, Any], logger: Any) -> None:
        self.logger = logger
        vision_cfg = config["vision"]
        self.model = ModelLoader.load_yolo_model(
            model_path=vision_cfg["ppe_model_path"],
            use_default_if_missing=vision_cfg.get("use_default_yolo_if_missing", True),
            logger=logger,
        )
        self.conf_threshold = vision_cfg["confidence_threshold"]

        # Demo mapping:
        # If custom PPE model exists, adjust labels according to training.
        # For fallback COCO model: 0=person is the main useful class.
        self.class_names = self.model.names

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
                label = self.class_names.get(class_id, str(class_id))

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
        return any(det["label"] == "person" for det in detections)

    def has_no_helmet(self, detections: List[Dict[str, Any]]) -> bool:
        # For a trained PPE model, change the label to match your dataset class
        return any(det["label"] in {"no_helmet", "without_helmet"} for det in detections)