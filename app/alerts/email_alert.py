from typing import Any, Dict
import smtplib
from email.mime.text import MIMEText


class EmailAlert:
    def __init__(self, config: Dict[str, Any], logger: Any) -> None:
        self.logger = logger
        self.enabled = config["email"]["enabled"]
        self.smtp_server = config["email"]["smtp_server"]
        self.smtp_port = config["email"]["smtp_port"]
        self.sender = config["email"]["sender"]
        self.password = config["email"]["password"]
        self.receiver = config["email"]["receiver"]

    def send(self, subject: str, body: str) -> None:
        if not self.enabled:
            return

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self.sender
        msg["To"] = self.receiver

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.sender, self.password)
            server.send_message(msg)

        self.logger.info("Email alert sent successfully")