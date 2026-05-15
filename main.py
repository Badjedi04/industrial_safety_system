from app.core.config_loader import load_config
from app.core.logger import setup_logger
from app.sensors.sensor_manager import SensorManager
from app.vision.camera_manager import CameraManager
from app.vision.ppe_detector import PPEDetector
from app.vision.fall_detector import FallDetector
from app.vision.zone_detector import ZoneDetector
from app.vision.frame_processor import FrameProcessor
from app.fusion.fusion_engine import FusionEngine
from app.alerts.alert_manager import AlertManager
from app.database.event_logger import EventLogger


def main() -> None:
    config = load_config("config.yaml")
    logger = setup_logger(config)

    logger.info("Starting Industrial Safety Monitoring System")

    sensor_manager = SensorManager(config, logger)
    camera_manager = CameraManager(config, logger)
    ppe_detector = PPEDetector(config, logger)
    fall_detector = FallDetector(config, logger)
    zone_detector = ZoneDetector(config, logger)
    frame_processor = FrameProcessor(config, logger)
    fusion_engine = FusionEngine(config, logger)
    alert_manager = AlertManager(config, logger)
    event_logger = EventLogger(config, logger)

    camera = camera_manager.start_camera()

    try:
        while True:
            sensor_data = sensor_manager.read_all()

            frame = camera_manager.read_frame(camera)
            if frame is None:
                if camera_manager.is_video_folder_source():
                    logger.info("Finished video: %s", camera_manager.get_current_video_name())
                    if not camera_manager.has_next_video():
                        logger.info("No more videos in folder")
                        break

                    logger.info("Press 'n' to open the next video, or 'q' to quit")
                    while True:
                        key = cv2.waitKey(0) & 0xFF
                        if key == ord("n"):
                            camera = camera_manager.advance_to_next_video(camera)
                            if camera is None:
                                logger.info("All videos processed from folder")
                                break
                            logger.info("Opening next video: %s", camera_manager.get_current_video_name())
                            break
                        if key == ord("q"):
                            logger.info("Exit requested by user")
                            camera = None
                            break

                    if camera is None:
                        break
                    continue

                if camera_manager.is_video_source():
                    logger.info("End of video file reached")
                    break

                logger.warning("No frame received from camera")
                continue

            ppe_results = ppe_detector.detect(frame)
            fall_results = fall_detector.detect(frame)
            zone_results = zone_detector.detect(frame)

            vision_data = {
                "ppe": ppe_results,
                "fall": fall_results,
                "zone": zone_results,
            }

            decision, reason = fusion_engine.evaluate(sensor_data, vision_data)

            alert_manager.handle_alert(decision, reason, sensor_data, vision_data)
            event_logger.log_event(sensor_data, vision_data, decision, reason)

            annotated = frame_processor.annotate_frame(
                frame=frame,
                sensor_data=sensor_data,
                vision_data=vision_data,
                decision=decision,
                reason=reason,
            )

            camera_manager.display_frame(annotated)

            if camera_manager.should_exit():
                logger.info("Exit requested by user")
                break

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as exc:
        logger.exception("Fatal system error: %s", exc)
    finally:
        camera_manager.release(camera)
        logger.info("System shutdown complete")


if __name__ == "__main__":
    main()