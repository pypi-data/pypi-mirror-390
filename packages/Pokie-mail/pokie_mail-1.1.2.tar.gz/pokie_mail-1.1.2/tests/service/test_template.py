from pokie_mail.dto import MessageTemplateRecord
from pokie_mail.helpers import MessageBuilder
from pokie_mail.service import MessageTemplateService
from tests.unit.constants import TPL_LOCALE, TPL_1_NAME


class TestTemplate:
    def test_template_add(self, template_1, svc_template: MessageTemplateService):
        # list templates, should be empty
        rows, items = svc_template.list(None)
        assert rows == 0

        # add template
        svc_template.insert(template_1)

        # list templates, should have 1
        rows, items = svc_template.list(None)
        assert rows == 1

        # read a valid template
        tpl = svc_template.get_template(TPL_1_NAME, TPL_LOCALE, 0)
        assert isinstance(tpl, MessageTemplateRecord)

        # read an invalid template - invalid channel
        tpl = svc_template.get_template(TPL_1_NAME, TPL_LOCALE, 1)
        assert tpl is None

    def test_template_get_builder(
        self, template_1, template_2, svc_template: MessageTemplateService
    ):
        # add template
        svc_template.insert(template_1)
        svc_template.insert(template_2)

        # list templates, should have 2
        rows, items = svc_template.list(None)
        assert rows == 2

        builder = svc_template.get_builder(TPL_1_NAME, TPL_LOCALE, 0)
        assert isinstance(builder, MessageBuilder)
