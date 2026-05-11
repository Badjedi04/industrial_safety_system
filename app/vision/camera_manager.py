from pathlib import Path
from typing import Any, Dict, List, Optional
import cv2


class CameraManager:
    def __init__(self, config: Dict[str, Any], logger: Any) -> None:
        self.logger = logger
        vision_config = config["vision"]
        self.input_source = vision_config.get("input_source", "camera")
        self.camera_index = vision_config.get("camera_index", 0)
        self.video_path = vision_config.get("video_path", "")
        self.video_directory = vision_config.get("video_directory", "")
        self.frame_width = vision_config.get("frame_width", 960)
        self.frame_height = vision_config.get("frame_height", 540)
        self.video_extensions = tuple(vision_config.get("video_extensions", [".mp4", ".avi", ".mov", ".mkv"]))
        self.video_files: List[Path] = []
        self.current_video_index = 0

    def start_camera(self) -> cv2.VideoCapture:
        if self.input_source == "video_folder":
            self.video_files = self._scan_video_folder(self.video_directory)
            if not self.video_files:
                raise RuntimeError(f"No video files found in folder: {self.video_directory}")
            self.current_video_index = 0
            return self._open_video_file(self.video_files[self.current_video_index])

        if self.input_source == "video":
            cap = cv2.VideoCapture(self.video_path)
            source_name = self.video_path
        else:
            cap = cv2.VideoCapture(self.camera_index)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            source_name = f"camera index {self.camera_index}"

        if not cap.isOpened():
            raise RuntimeError(f"Unable to open video source: {source_name}")

        self.logger.info("Video source initialized successfully: %s", source_name)
        return cap

    def _scan_video_folder(self, folder_path: str) -> List[Path]:
        folder = Path(folder_path)
        if not folder.exists() or not folder.is_dir():
            raise RuntimeError(f"Invalid video folder path: {folder_path}")

        files = [path for path in sorted(folder.iterdir()) if path.suffix.lower() in self.video_extensions]
        self.logger.info("Found %d video(s) in folder: %s", len(files), folder_path)
        return files

    def _open_video_file(self, video_file: Path) -> cv2.VideoCapture:
        cap = cv2.VideoCapture(str(video_file))
        if not cap.isOpened():
            raise RuntimeError(f"Unable to open video file: {video_file}")

        self.logger.info("Opened video file: %s", video_file)
        return cap

    def advance_to_next_video(self, cap: Optional[cv2.VideoCapture]) -> Optional[cv2.VideoCapture]:
        if self.input_source != "video_folder":
            return None

        if cap is not None:
            cap.release()

        self.current_video_index += 1
        if self.current_video_index >= len(self.video_files):
            return None

        return self._open_video_file(self.video_files[self.current_video_index])

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
        self.logger.info("Video source released and windows destroyed")

    def is_video_source(self) -> bool:
        return self.input_source in {"video", "video_folder"}

    def is_video_folder_source(self) -> bool:
        return self.input_source == "video_folder"
    def is_video_source(self) -> bool:
        return self.input_source == "video"