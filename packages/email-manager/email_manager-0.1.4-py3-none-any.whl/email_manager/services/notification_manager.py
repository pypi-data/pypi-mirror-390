
from email_manager.factory.provider_factory import ProviderFactory
from email_manager.providers.exceptions import EmailSendError

class EmailNotificationManager:
    def __init__(self, config, logger=None,):
        self.logger = logger
        self.force_mailtrap = config.force_mailtrap
        if not config.mailtrap_params and config.force_mailtrap: raise 'force_mailtrap = True and missing mailtrap_params'
        
        if not config.mailgun_params or not config.smtp_params: raise 'missing mailgun_params or smtp_params'
        
        if self.force_mailtrap:
            self.provider = ProviderFactory.create_provider(config, override="mailtrap")
            self.fallback_provider = None
        else:
            self.provider = ProviderFactory.create_provider(config, override="mailgun")
            self.fallback_provider = ProviderFactory.create_provider(config, override="smtp")

    def send_notification(self, to: str, subject: str, body: str, attachments: list = None) -> bool:
        try:
            return self.provider.send_email(to, subject, body, attachments)
        except EmailSendError as e:
            print(f"⚠️ Fallback [SMTP] activado por error en {e.provider_name}: {e}")
            try:
                return self.fallback_provider.send_email(to, subject, body, attachments)
            except EmailSendError as fallback_error:
                print(f"❌ Fallback también falló: {fallback_error}")
                return False
