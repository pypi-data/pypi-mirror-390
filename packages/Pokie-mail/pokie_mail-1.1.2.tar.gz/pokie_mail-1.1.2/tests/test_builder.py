from pokie_mail.constants import STATUS_DRAFT
from pokie_mail.helpers import MessageBuilder
from pokie_mail.service import MessageTemplateService
from tests.unit.constants import TPL_LOCALE, TPL_2_NAME


class TestBuilder:
    def test_builder(
        self, template_1, template_2, svc_template: MessageTemplateService
    ):
        # add template
        svc_template.insert(template_1)
        svc_template.insert(template_2)

        # list templates, should have 2
        rows, items = svc_template.list(None)
        assert rows == 2

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

        # assemble message with default placeholders
        record = builder.assemble(msg_from="origin", msg_to="destination", data={})
        assert record.sent is None
        assert record.status == STATUS_DRAFT
        assert record.msg_to == "destination"
        assert record.msg_from == "origin"
        assert record.html == "the quick blue duck flies over the lazy dog"
        assert record.content == record.html
