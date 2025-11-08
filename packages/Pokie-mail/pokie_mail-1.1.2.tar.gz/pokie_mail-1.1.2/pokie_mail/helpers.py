import json
import re

from pokie_mail.constants import STATUS_DRAFT
from pokie_mail.dto import MessageTemplateRecord, MessageQueueRecord


class MessageBuilder:
    def __init__(self, template: MessageTemplateRecord):
        self.template = template

    def assemble(self, msg_from, msg_to, data: dict = None):
        message = MessageQueueRecord(channel=self.template.channel, status=STATUS_DRAFT)
        if data is None:
            data = {}

        if len(self.template.placeholders) > 0:
            tmp = json.loads(self.template.placeholders)
            data = {**tmp, **data}

        if isinstance(msg_to, (list, tuple)):
            msg_to = ",".join(msg_to)

        if not msg_from or not msg_to:
            raise ValueError("assemble(): msg_from and msg_to cannot be empty")

        message.msg_from = msg_from
        message.msg_to = msg_to
        message.title = self._replace(data, self.template.subject)
        message.content = (
            self._replace(data, self.template.body)
            if len(self.template.body) > 0
            else ""
        )
        message.html = (
            self._replace(data, self.template.html)
            if len(self.template.html) > 0
            else None
        )
        return message

    def _replace(self, replace_map: dict, src) -> str:
        regexp = re.compile("|".join(map(re.escape, replace_map)))
        return regexp.sub(lambda match: replace_map[match.group(0)], src)
