
from email_manager.factory.provider_factory import ProviderFactory
from email_manager.providers.exceptions import EmailSendError

class EmailNotificationManager:
    def __init__(self, config, logger=None,):
        self.logger = logger
        self.provider_type = config.provider_type.lower()
        if not config.mailtrap_params and config.provider_type == 'mailtrap': 
            print('provider_type = mailtrap and missing mailtrap_params')
            return
        
        if not config.mailgun_params or not config.smtp_params: 
            print('missing mailgun_params or smtp_params')
            return
            
        if self.provider_type == 'mailtrap':
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
