from typing import Any, Dict
from app.alerts.mqtt_publisher import MQTTPublisher
from app.alerts.email_alert import EmailAlert
from app.alerts.buzzer_alert import BuzzerAlert


class AlertManager:
    def __init__(self, config: Dict[str, Any], logger: Any) -> None:
        self.logger = logger
        self.mqtt = MQTTPublisher(config, logger)
        self.email = EmailAlert(config, logger)
        self.buzzer = BuzzerAlert(logger)
        self.last_decision = None

    def handle_alert(
        self,
        decision: str,
        reason: str,
        sensor_data: Dict[str, Any],
        vision_data: Dict[str, Any],
    ) -> None:
        if decision == "SAFE":
            self.last_decision = decision
            return

        payload = {
            "decision": decision,
            "reason": reason,
            "sensor_data": sensor_data,
            "vision_data": vision_data,
        }

        # Avoid spamming identical alerts every frame
        if decision != self.last_decision:
            self.mqtt.publish(payload)

            if decision in {"MEDIUM_RISK", "HIGH_RISK", "CRITICAL_ALERT", "EMERGENCY"}:
                self.buzzer.trigger()

            if decision in {"CRITICAL_ALERT", "EMERGENCY"}:
                self.email.send(
                    subject=f"Industrial Safety Alert: {decision}",
                    body=(
                        f"Decision: {decision}\n"
                        f"Reason: {reason}\n"
                        f"Sensor Data: {sensor_data}\n"
                        f"Vision Data: {vision_data}\n"
                    ),
                )

            self.logger.warning("Alert handled: %s | %s", decision, reason)

        self.last_decision = decision