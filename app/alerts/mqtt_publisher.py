from typing import Any, Dict
import json
import paho.mqtt.client as mqtt


class MQTTPublisher:
    def __init__(self, config: Dict[str, Any], logger: Any) -> None:
        self.logger = logger
        self.enabled = config["mqtt"]["enabled"]
        self.topic = config["mqtt"]["topic"]
        self.client = None

        if self.enabled:
            self.client = mqtt.Client()
            self.client.connect(config["mqtt"]["broker"], config["mqtt"]["port"])
            self.logger.info("MQTT connected to %s", config["mqtt"]["broker"])

    def publish(self, payload: Dict[str, Any]) -> None:
        if not self.enabled or self.client is None:
            return

        message = json.dumps(payload)
        self.client.publish(self.topic, message)
        self.logger.info("Published MQTT message: %s", message)