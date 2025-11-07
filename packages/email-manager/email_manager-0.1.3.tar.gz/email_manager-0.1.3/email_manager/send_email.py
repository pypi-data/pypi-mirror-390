
from email_manager.config.email_config import EmailConfig
from email_manager.services.notification_manager import EmailNotificationManager

class EmailSystem:
    def __init__(
        self,
        provider_type: str,
        timeout: int = 10,
        max_retries: int = 3,
        mailgun_params: dict = None,
        smtp_params: dict = None,
        mailtrap_params: dict = None,
        force_mailtrap: bool = False
    ):
        config = EmailConfig(
            provider_type=provider_type,
            timeout=timeout,
            max_retries=max_retries,
            mailgun_params=mailgun_params,
            smtp_params=smtp_params,
            mailtrap_params=mailtrap_params,
            force_mailtrap=force_mailtrap
        )
        self.manager = EmailNotificationManager(config)

    def send(self, to: str, subject: str, body: str, attachments: list = None) -> bool:
        return self.manager.send_notification(to, subject, body, attachments)

