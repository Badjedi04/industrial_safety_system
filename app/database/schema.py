CREATE_EVENTS_TABLE = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    decision TEXT NOT NULL,
    reason TEXT NOT NULL,
    sensor_data TEXT NOT NULL,
    vision_data TEXT NOT NULL
);
"""