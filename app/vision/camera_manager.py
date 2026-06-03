from typing import Any, Dict, Optional
import cv2


class CameraManager:
    def __init__(self, config: Dict[str, Any], logger: Any) -> None:
        self.logger = logger
        self.source = config["vision"].get("source", "camera").lower()
        self.video_path = config["vision"].get("video_path", "")
        self.camera_index = config["vision"]["camera_index"]
        self.frame_width = config["vision"]["frame_width"]
        self.frame_height = config["vision"]["frame_height"]
        self.using_video = self.source == "video"

    def start_camera(self) -> cv2.VideoCapture:
        if self.using_video:
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                raise RuntimeError(f"Unable to open video file: {self.video_path}")
            self.logger.info("Video file opened successfully: %s", self.video_path)
        else:
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
        if frame is None:
            return

        height, width = frame.shape[:2]
        if width != self.frame_width or height != self.frame_height:
            frame = cv2.resize(frame, (self.frame_width, self.frame_height), interpolation=cv2.INTER_AREA)

        cv2.imshow("Industrial Safety Monitoring", frame)

    def should_exit(self) -> bool:
        return (cv2.waitKey(1) & 0xFF) == ord("q")

    def release(self, cap: cv2.VideoCapture) -> None:
        if cap is not None:
            cap.release()
        cv2.destroyAllWindows()
        self.logger.info("Camera released and windows destroyed")