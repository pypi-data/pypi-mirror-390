from pokie_mail.constants import STATUS_DRAFT, STATUS_SENT, STATUS_QUEUED
from pokie_mail.helpers import MessageBuilder
from pokie_mail.service import MessageTemplateService, MessageQueueService
from tests.unit.constants import TPL_LOCALE, TPL_2_NAME


class TestQueue:
    def test_queue(
        self,
        template_2,
        svc_queue: MessageQueueService,
        svc_template: MessageTemplateService,
    ):
        # add template
        svc_template.insert(template_2)

        builder = svc_template.get_builder(TPL_2_NAME, TPL_LOCALE, 0)
        assert isinstance(builder, MessageBuilder)

        # assemble message from template, with placeholders
        record = builder.assemble(
            msg_from="origin",
            msg_to="destination",
            data={"{{color}}": "brown", "{{animal}}": "fox", "{{what}}": "jumps"},
        )
        assert record.sent is None
        assert record.status == STATUS_DRAFT
        assert record.msg_to == "destination"
        assert record.msg_from == "origin"
        assert record.html == "the quick brown fox jumps over the lazy dog"
        assert record.content == record.html
        assert record.channel == 0

        # queue message
        msg_id = svc_queue.queue(record)

        # fetch for processing
        msg_to_send = svc_queue.fetch_for_processing(0)
        assert msg_to_send is not None
        assert msg_id == msg_to_send.id

        # simulate the sending of message
        svc_queue.update_status(msg_id, STATUS_SENT)
        msg_to_send = svc_queue.fetch_for_processing(0)
        assert msg_to_send is None

        results = svc_queue.list_by_status(0, STATUS_SENT)
        assert len(results) == 1

        results = svc_queue.list_by_status(0, STATUS_QUEUED)
        assert len(results) == 0
