import logging

from rick.base import Di
from rick.mixin import Injectable, Runnable
from rick.resource.console import ConsoleWriter
from rick_mailer import Mailer, SMTPFactory

from pokie.constants import DI_TTY, DI_SERVICES, DI_CONFIG
from pokie_mail.constants import (
    SVC_MESSAGE_QUEUE,
    CHANNEL_SMTP,
    STATUS_SENT,
    STATUS_FAILED,
)
from pokie_mail.service import MessageQueueService


class MailJob(Injectable, Runnable):
    DEFAULT_MAILS_PER_RUN = 10000

    def __init__(self, di: Di):
        super().__init__(di)
        self.tty = di.get(DI_TTY) if di.has(DI_TTY) else ConsoleWriter()
        self.mails_per_run = di.get(DI_CONFIG).get(
            "mails_per_run", self.DEFAULT_MAILS_PER_RUN
        )

    @property
    def get_smtp_mailer(self) -> Mailer:
        config = self.get_di().get(DI_CONFIG).asdict()
        return Mailer(SMTPFactory(config))

    @property
    def svc_queue(self) -> MessageQueueService:
        return self.get_di().get(DI_SERVICES).get(SVC_MESSAGE_QUEUE)


class MailQueueJob(MailJob):
    def run_smtp(self):
        total = 0
        while total < self.mails_per_run:
            record = self.svc_queue.fetch_for_processing(CHANNEL_SMTP)
            if record is None:
                # no more messages, exit
                return True

            try:
                if (
                    self.get_smtp_mailer.send_mail(
                        record.title,
                        record.content,
                        record.msg_from,
                        record.msg_to.split(","),
                        html_message=record.html,
                    )
                    > 0
                ):
                    self.svc_queue.update_status(record.id, STATUS_SENT)
            except Exception as e:
                self.tty.error(str(e))
                self.svc_queue.update_status(record.id, STATUS_FAILED)

        return True

    def run(self, di: Di):
        # run smtp - channel 0
        return self.run_smtp()
