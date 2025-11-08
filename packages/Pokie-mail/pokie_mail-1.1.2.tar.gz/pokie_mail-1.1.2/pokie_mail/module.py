from pokie_mail.constants import SVC_MESSAGE_TEMPLATE, SVC_MESSAGE_QUEUE
from pokie.core import BaseModule


class Module(BaseModule):
    name = "mail"
    description = "Mail template module"

    services = {
        SVC_MESSAGE_TEMPLATE: "pokie_mail.service.MessageTemplateService",
        SVC_MESSAGE_QUEUE: "pokie_mail.service.MessageQueueService",
    }

    cmd = {
        "mail:purge": "pokie_mail.cli.PurgeQueueCmd",
        "mail:run": "pokie_mail.cli.RunQueueCmd",
    }

    jobs = [
        "pokie_mail.job.MailQueueJob",
    ]
