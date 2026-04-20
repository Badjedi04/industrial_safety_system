from typing import Any
import os
from ultralytics import YOLO


class ModelLoader:
    @staticmethod
    def load_yolo_model(model_path: str, use_default_if_missing: bool, logger: Any) -> YOLO:
        if os.path.exists(model_path):
            logger.info("Loading YOLO model from %s", model_path)
            return YOLO(model_path)

        if use_default_if_missing:
            logger.warning(
                "Custom model not found at %s. Falling back to yolov8n.pt",
                model_path,
            )
            return YOLO("yolov8n.pt")

        raise FileNotFoundError(f"Model file not found: {model_path}")