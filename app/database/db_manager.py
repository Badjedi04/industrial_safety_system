from typing import Any, Dict
import os
import sqlite3
from app.database.schema import CREATE_EVENTS_TABLE


class DBManager:
    def __init__(self, config: Dict[str, Any], logger: Any) -> None:
        self.logger = logger
        self.db_path = config["database"]["path"]

        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self._initialize()

    def _initialize(self) -> None:
        cursor = self.connection.cursor()
        cursor.execute(CREATE_EVENTS_TABLE)
        self.connection.commit()
        self.logger.info("Database initialized at %s", self.db_path)

    def insert_event(
        self,
        timestamp: str,
        decision: str,
        reason: str,
        sensor_data: str,
        vision_data: str,
    ) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO events (timestamp, decision, reason, sensor_data, vision_data)
            VALUES (?, ?, ?, ?, ?)
            """,
            (timestamp, decision, reason, sensor_data, vision_data),
        )
        self.connection.commit()