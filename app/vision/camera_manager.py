from typing import Any, Dict, Optional
import cv2


class CameraManager:
    def __init__(self, config: Dict[str, Any], logger: Any) -> None:
        self.logger = logger
        self.camera_index = config["vision"]["camera_index"]
        self.frame_width = config["vision"]["frame_width"]
        self.frame_height = config["vision"]["frame_height"]

    def start_camera(self) -> cv2.VideoCapture:
        cap = cv2.VideoCapture(self.camera_index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)

        if not cap.isOpened():
            raise RuntimeError("Unable to open webcam/camera")

        self.logger.info("Camera initialized successfully")
        return cap

    def read_frame(self, cap: cv2.VideoCapture) -> Optional[Any]:
        ret, frame = cap.read()
        if not ret:
            return None
        return frame

    def display_frame(self, frame: Any) -> None:
        cv2.imshow("Industrial Safety Monitoring", frame)

    def should_exit(self) -> bool:
        return (cv2.waitKey(1) & 0xFF) == ord("q")

    def release(self, cap: cv2.VideoCapture) -> None:
        if cap is not None:
            cap.release()
        cv2.destroyAllWindows()
        self.logger.info("Camera released and windows destroyed")