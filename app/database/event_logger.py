from typing import Any, Dict
import json
from app.database.db_manager import DBManager
from app.core.utils import get_timestamp


class EventLogger:
    def __init__(self, config: Dict[str, Any], logger: Any) -> None:
        self.logger = logger
        self.db = DBManager(config, logger)

    def log_event(
        self,
        sensor_data: Dict[str, Any],
        vision_data: Dict[str, Any],
        decision: str,
        reason: str,
    ) -> None:
        timestamp = get_timestamp()
        self.db.insert_event(
            timestamp=timestamp,
            decision=decision,
            reason=reason,
            sensor_data=json.dumps(sensor_data),
            vision_data=json.dumps(vision_data),
        )
        self.logger.info("Event logged | %s | %s | %s", timestamp, decision, reason)