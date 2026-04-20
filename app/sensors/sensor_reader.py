from typing import Any, Dict
import json
import random
import time

try:
    import serial
except ImportError:
    serial = None


class SensorReader:
    def __init__(self, config: Dict[str, Any], logger: Any) -> None:
        self.logger = logger
        self.mode = config["sensor"]["mode"]
        self.serial_port = config["sensor"]["serial_port"]
        self.baud_rate = config["sensor"]["baud_rate"]
        self.connection = None
        self._last_spike_time = 0.0

        if self.mode == "serial" and serial is not None:
            try:
                self.connection = serial.Serial(
                    self.serial_port,
                    self.baud_rate,
                    timeout=1,
                )
                self.logger.info("Connected to serial sensor source: %s", self.serial_port)
            except Exception as exc:
                self.logger.warning(
                    "Serial connection failed (%s). Falling back to simulated mode.",
                    exc,
                )
                self.mode = "simulated"

    def _read_serial(self) -> Dict[str, float]:
        if self.connection is None:
            raise RuntimeError("Serial connection is not initialized")

        line = self.connection.readline().decode("utf-8", errors="ignore").strip()
        if not line:
            return {"gas": 0.0, "temperature": 0.0, "vibration": 0.0}

        try:
            data = json.loads(line)
            return {
                "gas": float(data.get("gas", 0.0)),
                "temperature": float(data.get("temperature", 0.0)),
                "vibration": float(data.get("vibration", 0.0)),
            }
        except Exception:
            self.logger.warning("Invalid serial sensor payload: %s", line)
            return {"gas": 0.0, "temperature": 0.0, "vibration": 0.0}

    def _read_simulated(self) -> Dict[str, float]:
        gas = random.uniform(180, 360)
        temperature = random.uniform(28, 40)
        vibration = random.uniform(80, 180)

        now = time.time()
        if now - self._last_spike_time > 10 and random.random() < 0.08:
            event_type = random.choice(["gas", "temperature", "vibration"])
            self._last_spike_time = now

            if event_type == "gas":
                gas = random.uniform(430, 650)
            elif event_type == "temperature":
                temperature = random.uniform(52, 70)
            else:
                vibration = random.uniform(320, 500)

        return {
            "gas": round(gas, 2),
            "temperature": round(temperature, 2),
            "vibration": round(vibration, 2),
        }

    def read(self) -> Dict[str, float]:
        if self.mode == "serial":
            return self._read_serial()
        return self._read_simulated()