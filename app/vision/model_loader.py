from typing import Any
import os
from ultralytics import YOLO

from app.vision.roboflow_client import RoboflowModel


class ModelLoader:
    @staticmethod
    def load_model(
        model_path: str,
        use_default_if_missing: bool,
        logger: Any,
        use_roboflow: bool = False,
        roboflow_api_key: str = "",
        roboflow_model_id: str = "",
        roboflow_model_version: str = "",
    ) -> Any:
        if use_roboflow:
            if not roboflow_api_key or not roboflow_model_id or not roboflow_model_version:
                raise ValueError(
                    "Roboflow configuration is incomplete. "
                    "Please set roboflow_api_key, roboflow_model_id, and roboflow_model_version."
                )
            logger.info(
                "Loading Roboflow hosted model %s version %s",
                roboflow_model_id,
                roboflow_model_version,
            )
            return RoboflowModel(
                api_key=roboflow_api_key,
                model_id=roboflow_model_id,
                model_version=roboflow_model_version,
                logger=logger,
            )

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