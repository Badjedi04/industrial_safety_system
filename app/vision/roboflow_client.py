import json
import uuid
import urllib.error
import urllib.request
from typing import Any, Dict, List

import cv2
import numpy as np


class RoboflowPredictionBox:
    def __init__(self, confidence: float, class_id: int, bbox: List[float]) -> None:
        self.conf = np.array([confidence], dtype=float)
        self.cls = np.array([class_id], dtype=int)
        self.xyxy = np.array([bbox], dtype=float)


class RoboflowResult:
    def __init__(self, boxes: List[RoboflowPredictionBox]) -> None:
        self.boxes = boxes


class RoboflowModel:
    def __init__(
        self,
        api_key: str,
        model_id: str,
        model_version: str,
        logger: Any,
    ) -> None:
        self.api_key = api_key
        self.model_id = model_id
        self.model_version = model_version
        self.logger = logger
        self.class_names: Dict[int, str] = {}
        self.label_to_id: Dict[str, int] = {}

    @property
    def names(self) -> Dict[int, str]:
        return self.class_names

    @property
    def endpoint_url(self) -> str:
        return (
            f"https://detect.roboflow.com/{self.model_id}/{self.model_version}"
            f"?api_key={self.api_key}"
        )

    def predict(self, frame: Any, verbose: bool = False) -> List[RoboflowResult]:
        success, encoded_image = cv2.imencode(".jpg", frame)
        if not success:
            raise RuntimeError("Failed to encode frame for Roboflow inference")

        data = self._build_multipart_body(encoded_image.tobytes())
        headers = {
            "Content-Type": f"multipart/form-data; boundary={data['boundary']}"
        }

        request = urllib.request.Request(
            self.endpoint_url,
            data=data["body"],
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            self.logger.error(
                "Roboflow HTTP error %s: %s",
                exc.code,
                exc.read().decode("utf-8", errors="ignore"),
            )
            raise
        except urllib.error.URLError as exc:
            self.logger.error("Roboflow request failed: %s", exc)
            raise

        results = json.loads(payload)
        predictions = results.get("predictions") or results.get("objects") or []
        if not isinstance(predictions, list):
            predictions = []

        boxes: List[RoboflowPredictionBox] = []
        for pred in predictions:
            raw_label = str(pred.get("class") or pred.get("label") or "").strip()
            if not raw_label:
                continue

            label = raw_label.lower().replace(" ", "_")
            class_id = self._label_to_id(label)
            confidence = float(pred.get("confidence", 0.0))
            x = float(pred.get("x", 0.0))
            y = float(pred.get("y", 0.0))
            width = float(pred.get("width", pred.get("w", 0.0)))
            height = float(pred.get("height", pred.get("h", 0.0)))

            x1 = x - width / 2.0
            y1 = y - height / 2.0
            x2 = x + width / 2.0
            y2 = y + height / 2.0

            boxes.append(
                RoboflowPredictionBox(
                    confidence=confidence,
                    class_id=class_id,
                    bbox=[x1, y1, x2, y2],
                )
            )

        return [RoboflowResult(boxes)]

    def _label_to_id(self, label: str) -> int:
        if label in self.label_to_id:
            return self.label_to_id[label]

        class_id = len(self.label_to_id) + 1
        self.label_to_id[label] = class_id
        self.class_names[class_id] = label
        return class_id

    def _build_multipart_body(self, image_bytes: bytes) -> Dict[str, Any]:
        boundary = uuid.uuid4().hex
        lines: List[bytes] = []

        def add_field(name: str, value: str) -> None:
            lines.append(f"--{boundary}".encode("utf-8"))
            lines.append(
                f"Content-Disposition: form-data; name=\"{name}\"".encode("utf-8")
            )
            lines.append(b"")
            lines.append(value.encode("utf-8"))

        def add_file(name: str, filename: str, content: bytes, content_type: str) -> None:
            lines.append(f"--{boundary}".encode("utf-8"))
            lines.append(
                f"Content-Disposition: form-data; name=\"{name}\"; filename=\"{filename}\"".encode("utf-8")
            )
            lines.append(f"Content-Type: {content_type}".encode("utf-8"))
            lines.append(b"")
            lines.append(content)

        add_field("api_key", self.api_key)
        add_file("image", "image.jpg", image_bytes, "image/jpeg")
        lines.append(f"--{boundary}--".encode("utf-8"))
        lines.append(b"")

        body = b"\r\n".join(lines)
        return {"boundary": boundary, "body": body}
