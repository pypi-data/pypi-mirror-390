from typing import Optional
from pokie.rest import RestService

from pokie_mail.constants import CHANNEL_SMTP
from pokie_mail.dto import MessageTemplateRecord
from pokie_mail.helpers import MessageBuilder
from pokie_mail.repository import MessageTemplateRepository


class MessageTemplateService(RestService):
    record_class = MessageTemplateRecord
    repository_class = MessageTemplateRepository

    def get_template(
        self, template: str, locale: str, channel: int = CHANNEL_SMTP
    ) -> Optional[MessageTemplateRecord]:
        return self.repository.find_template(template, locale, channel)

    def get_builder(
        self, template: str, locale: str, channel: int = CHANNEL_SMTP
    ) -> Optional[MessageBuilder]:
        template = self.repository.find_template(template, locale, channel)
        if template is None:
            return None
        return MessageBuilder(template)
