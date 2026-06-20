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
from app.performance.metrics_collector import MetricsCollector


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
    metrics = MetricsCollector(output_path="data/performance_metrics.csv")
    frame_number = 0

    camera = camera_manager.start_camera()

    try:
        while True:
            frame_number += 1
            frame_start_time = metrics.now()

            sensor_start_time = metrics.now()
            sensor_data = sensor_manager.read_all()
            sensor_read_time_ms = metrics.elapsed_ms(sensor_start_time)

            frame_read_start_time = metrics.now()
            frame = camera_manager.read_frame(camera)
            frame_read_time_ms = metrics.elapsed_ms(frame_read_start_time)

            if frame is None:
                if getattr(camera_manager, "using_video", False):
                    logger.info("Video stream ended")
                    break

                logger.warning("No frame received from camera")
                continue

            ppe_start_time = metrics.now()
            ppe_results = ppe_detector.detect(frame)
            ppe_detection_time_ms = metrics.elapsed_ms(ppe_start_time)
            logger.debug("PPE detections: %s", ppe_results)

            fall_start_time = metrics.now()
            fall_results = fall_detector.detect(frame)
            fall_detection_time_ms = metrics.elapsed_ms(fall_start_time)

            zone_start_time = metrics.now()
            zone_results = zone_detector.detect(frame)
            zone_detection_time_ms = metrics.elapsed_ms(zone_start_time)

            vision_data = {
                "ppe": ppe_results,
                "fall": fall_results,
                "zone": zone_results,
            }

            fusion_start_time = metrics.now()
            decision, reason = fusion_engine.evaluate(sensor_data, vision_data)
            fusion_time_ms = metrics.elapsed_ms(fusion_start_time)

            alert_start_time = metrics.now()
            alert_manager.handle_alert(decision, reason, sensor_data, vision_data)
            alert_time_ms = metrics.elapsed_ms(alert_start_time)

            logging_start_time = metrics.now()
            event_logger.log_event(sensor_data, vision_data, decision, reason)
            logging_time_ms = metrics.elapsed_ms(logging_start_time)

            annotation_start_time = metrics.now()
            annotated = frame_processor.annotate_frame(
                frame=frame,
                sensor_data=sensor_data,
                vision_data=vision_data,
                decision=decision,
                reason=reason,
            )
            annotation_time_ms = metrics.elapsed_ms(annotation_start_time)

            display_start_time = metrics.now()
            camera_manager.display_frame(annotated)
            display_time_ms = metrics.elapsed_ms(display_start_time)

            frame_end_time = metrics.now()
            frame_processing_time_ms = metrics.elapsed_ms(frame_start_time, frame_end_time)
            fps = metrics.calculate_fps(frame_end_time)
            system_metrics = metrics.get_system_metrics()

            metrics.record_frame(
                {
                    "frame_number": frame_number,
                    "timestamp_sec": round(frame_end_time - metrics.start_time, 3),
                    "fps": fps,
                    "frame_processing_time_ms": frame_processing_time_ms,
                    "sensor_read_time_ms": sensor_read_time_ms,
                    "frame_read_time_ms": frame_read_time_ms,
                    "ppe_detection_time_ms": ppe_detection_time_ms,
                    "fall_detection_time_ms": fall_detection_time_ms,
                    "zone_detection_time_ms": zone_detection_time_ms,
                    "fusion_time_ms": fusion_time_ms,
                    "alert_time_ms": alert_time_ms,
                    "logging_time_ms": logging_time_ms,
                    "annotation_time_ms": annotation_time_ms,
                    "display_time_ms": display_time_ms,
                    "num_ppe_detections": len(ppe_results),
                    "num_fall_detections": len(fall_results),
                    "num_zone_detections": len(zone_results),
                    "decision": decision,
                    "reason": reason,
                    "gas": sensor_data.get("gas", 0),
                    "temperature": sensor_data.get("temperature", 0),
                    "vibration": sensor_data.get("vibration", 0),
                    "cpu_percent": system_metrics["cpu_percent"],
                    "memory_mb": system_metrics["memory_mb"],
                }
            )

            if camera_manager.should_exit():
                logger.info("Exit requested by user")
                break

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as exc:
        logger.exception("Fatal system error: %s", exc)
    finally:
        metrics.save_csv()
        metrics.save_summary()
        logger.info("Performance metrics saved to data/performance_metrics.csv")
        logger.info("Performance summary saved to data/performance_summary.txt")
        camera_manager.release(camera)
        logger.info("System shutdown complete")


if __name__ == "__main__":
    main()
